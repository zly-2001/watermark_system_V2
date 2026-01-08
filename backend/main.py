"""
AIGC抗性水印溯源管理系统 - FastAPI 主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, watermark, attack, history

app = FastAPI(
    title="AIGC抗性水印溯源管理系统",
    description="StegaStamp Demo - 面向AIGC的隐形水印溯源管理系统",
    version="2.0.0"
)

# 配置 CORS - 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite 默认端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api", tags=["认证"])
app.include_router(watermark.router, prefix="/api", tags=["水印"])
app.include_router(attack.router, prefix="/api", tags=["攻击"])
app.include_router(history.router, prefix="/api", tags=["历史记录"])


@app.get("/")
async def root():
    return {
        "message": "AIGC抗性水印溯源管理系统 API",
        "version": "2.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

