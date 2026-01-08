# 🔧 故障排查指南

## ❌ 错误：numpy.dtype size changed

### 错误信息
```
ValueError: numpy.dtype size changed, may indicate binary incompatibility. 
Expected 96 from C header, got 88 from PyObject
```

### 原因
- numpy 和 scikit-image 版本不兼容
- scikit-image 是用不同版本的 numpy 编译的

### 解决方法

#### 方法1：使用修复脚本（推荐）

```bash
cd /Users/zly/Downloads/watermark_system_V2/backend

# 激活虚拟环境
source venv/bin/activate

# 运行修复脚本
bash FIX_DEPENDENCIES.sh
```

#### 方法2：手动修复

```bash
cd /Users/zly/Downloads/watermark_system_V2/backend
source venv/bin/activate

# 1. 卸载冲突的包
pip uninstall -y numpy scikit-image scipy

# 2. 重新安装兼容版本
pip install numpy==1.26.2
pip install scipy==1.11.4
pip install scikit-image==0.22.0

# 3. 验证
python -c "from skimage.metrics import structural_similarity; print('✓ OK')"
```

#### 方法3：重建虚拟环境（最彻底）

```bash
cd /Users/zly/Downloads/watermark_system_V2/backend

# 删除旧的虚拟环境
rm -rf venv

# 创建新的虚拟环境
python3 -m venv venv

# 激活
source venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装所有依赖
pip install -r requirements.txt

# 验证
python -c "from skimage.metrics import structural_similarity; print('✓ OK')"
```

---

## ❌ 错误：invisible-watermark 未安装

### 错误信息
```
ModuleNotFoundError: No module named 'invisible_watermark'
```

### 解决方法

```bash
source venv/bin/activate
pip install invisible-watermark opencv-python PyWavelets
```

---

## ❌ 错误：端口已被占用

### 错误信息
```
ERROR: [Errno 48] Address already in use
```

### 解决方法

```bash
# 查找占用 8000 端口的进程
lsof -i :8000

# 杀死进程（替换 PID）
kill -9 <PID>

# 或者使用其他端口
uvicorn main:app --reload --port 8001
```

---

## ❌ 错误：前端启动失败

### 错误信息
```
Error: Cannot find module ...
```

### 解决方法

```bash
cd /Users/zly/Downloads/watermark_system_V2/frontend

# 删除旧的依赖
rm -rf node_modules package-lock.json

# 重新安装
npm install

# 启动
npm run dev
```

---

## ❌ 错误：CORS 跨域问题

### 错误信息（浏览器控制台）
```
Access to XMLHttpRequest has been blocked by CORS policy
```

### 解决方法

检查 `backend/main.py` 中的 CORS 配置：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## ❌ 错误：登录后无法跳转

### 症状
点击登录后，页面没有跳转到主页

### 解决方法

1. 打开浏览器开发者工具（F12）
2. 查看 Console 标签页
3. 检查是否有 JWT token 相关错误
4. 清除浏览器缓存和 localStorage：
   ```javascript
   localStorage.clear()
   location.reload()
   ```

---

## ❌ 错误：图片上传失败

### 症状
上传图片后没有反应或报错

### 解决方法

1. 检查图片格式（支持 JPG, PNG）
2. 检查图片大小（建议 < 5MB）
3. 检查后端日志是否有错误
4. 尝试使用其他图片

---

## ❌ 错误：水印提取失败

### 症状
提取水印时显示 "Mock 模式" 或提取失败

### 解决方法

```bash
# 检查 invisible-watermark 是否正确安装
python -c "from invisible_watermark import WatermarkEncoder; print('OK')"

# 如果失败，重新安装
pip install --force-reinstall invisible-watermark opencv-python
```

---

## 🔍 调试技巧

### 1. 查看后端日志

```bash
# 启动时会显示详细日志
uvicorn main:app --reload --log-level debug
```

### 2. 查看前端控制台

打开浏览器开发者工具（F12）：
- Console: 查看 JavaScript 错误
- Network: 查看 API 请求状态
- Application: 查看 localStorage 中的 token

### 3. 测试 API

```bash
# 测试后端是否运行
curl http://127.0.0.1:8000/

# 测试登录 API
curl -X POST "http://127.0.0.1:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### 4. 检查依赖版本

```bash
# Python 依赖
pip list

# Node.js 依赖
npm list

# 检查特定包
pip show invisible-watermark
```

---

## 📦 完整重装指南

如果问题无法解决，尝试完全重装：

```bash
# 1. 停止所有服务（Ctrl+C）

# 2. 删除虚拟环境
cd /Users/zly/Downloads/watermark_system_V2/backend
rm -rf venv

# 3. 删除前端依赖
cd ../frontend
rm -rf node_modules package-lock.json

# 4. 重新安装后端
cd ../backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5. 重新安装前端
cd ../frontend
npm install

# 6. 启动后端
cd ../backend
source venv/bin/activate
uvicorn main:app --reload

# 7. 启动前端（新终端）
cd /Users/zly/Downloads/watermark_system_V2/frontend
npm run dev
```

---

## 💡 预防措施

### 1. 使用兼容的 Python 版本

```bash
# 检查 Python 版本
python3 --version

# 推荐 Python 3.9 或 3.10
```

### 2. 定期更新依赖

```bash
# 后端
pip install --upgrade pip
pip list --outdated

# 前端
npm outdated
```

### 3. 使用版本锁定

```bash
# 生成精确的依赖版本
pip freeze > requirements-lock.txt

# 使用锁定版本安装
pip install -r requirements-lock.txt
```

---

## 📞 获取帮助

如果以上方法都无法解决问题：

1. **检查终端输出**：完整的错误信息
2. **检查浏览器控制台**：前端错误信息
3. **查看日志文件**：如果有的话
4. **搜索错误信息**：复制完整错误到 Google

---

## ✅ 验证安装

所有修复完成后，运行这些命令验证：

```bash
# 1. 后端依赖
source venv/bin/activate
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
python -c "from skimage.metrics import structural_similarity; print('scikit-image: OK')"
python -c "from invisible_watermark import WatermarkEncoder; print('invisible-watermark: OK')"

# 2. 前端依赖
cd ../frontend
npm list vue
npm list element-plus

# 3. 启动测试
cd ../backend
uvicorn main:app --reload
# 看到 "Uvicorn running on http://127.0.0.1:8000" 就成功了

# 4. 访问测试
curl http://127.0.0.1:8000/
# 应该返回 {"message": "Watermark System API"}
```

---

**最后更新：** 2026-01-07

