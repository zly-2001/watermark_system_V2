"""
认证模块 - JWT 登录与注册
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets

router = APIRouter()

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 配置
SECRET_KEY = secrets.token_urlsafe(32)  # 随机生成密钥
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# 内存数据库（演示用）
# 延迟初始化以避免模块导入时的 bcrypt 错误
fake_users_db = {}


def _init_default_users():
    """初始化默认用户（仅在首次访问时调用）"""
    if not fake_users_db:
        fake_users_db["admin"] = {
            "username": "admin",
            "hashed_password": pwd_context.hash("admin123"),  # 默认密码
            "email": "admin@example.com"
        }


class User(BaseModel):
    username: str
    email: Optional[str] = None


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def get_user(username: str) -> Optional[UserInDB]:
    """从数据库获取用户"""
    _init_default_users()  # 确保默认用户已初始化
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)
    return None


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """验证用户身份"""
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建 JWT Token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """获取当前登录用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return User(username=user.username, email=user.email)


@router.post("/register", response_model=dict)
async def register(user_data: RegisterRequest):
    """用户注册"""
    if user_data.username in fake_users_db:
        raise HTTPException(
            status_code=400,
            detail="用户名已存在"
        )
    
    hashed_password = get_password_hash(user_data.password)
    fake_users_db[user_data.username] = {
        "username": user_data.username,
        "hashed_password": hashed_password,
        "email": user_data.email or f"{user_data.username}@example.com"
    }
    
    return {
        "message": "注册成功",
        "username": user_data.username
    }


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """用户登录 - 返回 JWT Token"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user

