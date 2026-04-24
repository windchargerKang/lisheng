# 渠道销售管理系统

基于 FastAPI + Vue3 的全渠道销售管理系统。

## 技术栈

- **后端**: FastAPI + SQLAlchemy + SQLite
- **前端 (H5)**: Vue3 + Vite + Vant4
- **前端 (运营管理)**: Vue3 + Vite + Element Plus

## 快速部署

### 方式一：Docker 部署（推荐）

#### 1. 安装 Docker 和 Docker Compose

```bash
# CentOS/RHEL
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker

# 配置 Docker 镜像加速器（国内服务器必需）
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.1panel.live",
    "https://hub.rat.dev",
    "https://dhub.kubesre.xyz"
  ]
}
EOF

sudo systemctl daemon-reload
sudo systemctl restart docker

# 验证配置
docker info | grep -A 5 "Registry Mirrors"
```

#### 2. 上传代码到服务器

```bash
# 方式 1: Git 克隆
git clone <repository-url>
cd lisheng-project

# 方式 2: 本地打包上传
# 本地执行：
tar -czf lisheng-project.tar.gz --exclude='.git' --exclude='node_modules' --exclude='.pytest_cache' .
# 上传到服务器：
scp lisheng-project.tar.gz root@服务器 IP:/opt/
# 服务器解压：
tar -xzf lisheng-project.tar.gz -C /opt/lisheng-project
```

#### 3. 构建并启动服务

```bash
cd /opt/lisheng-project

# 构建镜像
./docker-deploy.sh build

# 启动服务
./docker-deploy.sh start
```

#### 4. 访问系统

- **H5 前端（C 端用户）**: http://服务器 IP:3000/
- **运营管理端（B 端管理）**: http://服务器 IP:5173/
- **后端 API**: http://服务器 IP:8000/
- **API 文档**: http://服务器 IP:8000/docs

#### 5. 常用命令

```bash
# 查看服务状态
./docker-deploy.sh status

# 查看日志
./docker-deploy.sh logs           # 查看所有服务日志
./docker-deploy.sh logs backend   # 查看后端日志
./docker-deploy.sh logs h5        # 查看 H5 日志
./docker-deploy.sh logs frontend  # 查看运营管理端日志

# 重启服务
./docker-deploy.sh restart

# 停止服务
./docker-deploy.sh stop

# 清理所有资源（包括数据卷）
./docker-deploy.sh clean
```

---

### 方式二：传统部署

#### 环境要求

- Python 3.11+
- Node.js 20+

#### 1. 后端部署

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 2. H5 前端部署

```bash
cd h5

# 安装依赖
npm install

# 开发模式
npm run dev

# 生产构建
npm run build
```

#### 3. 运营管理前端部署

```bash
cd frontend

# 安装依赖
npm install

# 开发模式
npm run dev

# 生产构建
npm run build
```

---

## 更新代码

### Docker 环境更新

```bash
# 1. 拉取最新代码
git pull

# 2. 重新构建并重启
./docker-deploy.sh stop
./docker-deploy.sh build
./docker-deploy.sh start

# 或者使用重启命令（不重新构建）
./docker-deploy.sh restart
```

### 传统部署更新

```bash
# 1. 拉取最新代码
git pull

# 2. 重启后端
cd backend
# 如果使用进程管理
./deploy.sh restart

# 3. 重新构建前端（如有前端变更）
cd h5
npm run build

cd frontend
npm run build
```

---

## 目录结构

```
lisheng-project/
├── backend/           # 后端服务
│   ├── app/          # 应用代码
│   ├── scripts/      # 脚本文件
│   ├── uploads/      # 上传文件
│   └── logs/         # 日志文件
├── h5/               # H5 前端（C 端）
├── frontend/         # 运营管理前端（B 端）
├── docker-compose.yml
└── docker-deploy.sh  # Docker 部署脚本
```

---

## 开发环境

### 后端开发

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端开发

```bash
# H5 前端
cd h5
npm run dev

# 运营管理前端
cd frontend
npm run dev
```

---

## 常见问题

### 1. Docker 构建失败（网络问题）

配置 Docker 镜像加速器，参考上方"安装 Docker 和 Docker Compose"章节。

### 2. 端口被占用

修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "8001:8000"  # 将 8000 改为 8001
```

### 3. 数据库初始化

```bash
cd backend
python scripts/init_db.py
```

### 4. 查看容器日志

```bash
docker logs lisheng-backend
docker logs lisheng-h5
docker logs lisheng-frontend
```

### 5. 进入容器调试

```bash
docker exec -it lisheng-backend bash
docker exec -it lisheng-h5 sh
docker exec -it lisheng-frontend sh
```

---

## 许可证

Copyright © 2024 渠道销售管理系统
