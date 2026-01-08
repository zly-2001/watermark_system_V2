# AIGC抗性水印溯源管理系统 (StegaStamp Demo)

面向AIGC的隐形水印溯源管理系统 - 毕业设计演示系统

## 项目简介

本系统是一个用于演示 StegaStamp 算法在对抗 AIGC 重绘（Stable Diffusion 模拟）时的鲁棒性的 Web 应用。系统通过直观的滑块对比和图表分析来展示水印嵌入、攻击模拟和溯源提取的完整流程。

## 技术栈

### 后端
- Python 3.10+
- FastAPI
- Uvicorn
- Pillow (PIL) - 图像处理
- ReportLab - PDF 报告生成
- Python-Jose & Passlib - JWT 认证

### 前端
- Vue 3
- Vite
- Element Plus
- Axios
- ECharts
- vue-compare-image

## 项目结构

```
watermark_system_V2/
├── backend/                 # FastAPI 后端
│   ├── main.py             # 主入口文件
│   ├── requirements.txt    # Python 依赖
│   └── routers/           # 路由模块
│       ├── auth.py        # 认证模块
│       ├── watermark.py   # 水印核心模块
│       └── attack.py      # 攻击实验室模块
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   │   ├── Login.vue
│   │   │   ├── EmbeddingStudio.vue
│   │   │   ├── AttackLab.vue
│   │   │   ├── TracingCenter.vue
│   │   │   └── Dashboard.vue
│   │   ├── layout/        # 布局组件
│   │   ├── router/        # 路由配置
│   │   └── utils/         # 工具函数
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 快速开始

### 1. 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动服务器
uvicorn main:app --reload --port 8000
```

后端将在 `http://localhost:8000` 启动

### 2. 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 `http://localhost:5173` 启动

### 3. 默认账户

- 用户名: `admin`
- 密码: `admin123`

## 功能模块

### 1. 嵌入工作台
- 上传图片并嵌入隐形水印
- 可调节隐蔽性与鲁棒性平衡参数
- 使用 vue-compare-image 实现原图与水印图的滑块对比
- 显示 PSNR 和 SSIM 质量指标

### 2. 异构攻击实验室
- **AIGC 破坏模拟**: 模拟 Stable Diffusion 重绘造成的细节丢失
  - 高斯模糊
  - 颜色抖动
  - 轻微噪点
- **常规几何攻击**:
  - 裁剪攻击
  - JPEG 压缩
  - 旋转攻击

### 3. 智能溯源与报告
- 提取水印信息
- 显示误码率 (BER) 仪表盘
- 生成 PDF 法证分析报告

### 4. 算法效能看板
- 攻击强度 vs 提取准确率折线图
- StegaStamp vs 传统 LSB 算法对比柱状图

## API 接口

### 认证接口
- `POST /api/register` - 用户注册
- `POST /api/login` - 用户登录（返回 JWT Token）
- `GET /api/me` - 获取当前用户信息

### 水印接口
- `POST /api/embed` - 嵌入水印
- `POST /api/extract` - 提取水印
- `POST /api/report` - 生成 PDF 报告

### 攻击接口
- `POST /api/attack` - 应用图像攻击

## 注意事项

1. **Mock 数据**: 当前版本使用 Mock 数据模拟 StegaStamp 算法效果，实际项目中需要集成真实的模型
2. **跨域配置**: 后端已配置 CORS，允许前端跨域访问
3. **图片格式**: 支持 JPG、PNG 格式，建议尺寸不超过 2048x2048
4. **Base64 处理**: 前端会自动处理 Base64 图片前缀

## 开发说明

### 后端占位符函数

在 `routers/watermark.py` 中：
- `run_stegastamp_encoder()` - StegaStamp 编码器占位符
- `run_stegastamp_decoder()` - StegaStamp 解码器占位符

这些函数需要后续集成真实的 StegaStamp 模型。

### 攻击实现

`routers/attack.py` 中的攻击函数使用 PIL 库实现真实的图像处理：
- `apply_aigc_sim_attack()` - AIGC 模拟攻击
- `apply_crop_attack()` - 裁剪攻击
- `apply_jpeg_attack()` - JPEG 压缩
- `apply_rotate_attack()` - 旋转攻击

## 许可证

本项目用于毕业设计演示，仅供学习参考。

