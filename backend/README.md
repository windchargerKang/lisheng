# 渠道销售管理系统 - Python FastAPI 后端

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env` 并修改配置：

```bash
cp .env.example .env
```

### 3. 初始化数据库

```bash
python scripts/init_db.py
```

### 4. 启动服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 访问 API 文档

打开浏览器访问：http://localhost:8000/docs

## 项目结构

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── api.py       # 路由注册
│   │   │   ├── auth.py      # 认证 API
│   │   │   ├── regions.py   # 区域管理 API
│   │   │   ├── shops.py     # 店铺管理 API
│   │   │   ├── agents.py    # 区代管理 API
│   │   │   └── products.py  # 产品管理 API
│   │   └── dependencies/    # FastAPI 依赖
│   ├── core/
│   │   ├── config.py        # 应用配置
│   │   ├── database.py      # 数据库配置
│   │   └── security.py      # 安全工具
│   ├── models/              # SQLAlchemy 模型
│   ├── schemas/             # Pydantic Schemas
│   ├── services/            # 业务逻辑层
│   └── utils/               # 工具函数
├── scripts/
│   └── init_db.py           # 数据库初始化
├── tests/                   # 测试文件
├── requirements.txt         # 依赖列表
└── README.md
```

## 运行测试

```bash
pytest
```
