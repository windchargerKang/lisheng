# 服务器部署更新指南

## 快速更新（推荐）

```bash
# 1. 进入项目目录
cd /opt/lisheng-project

# 2. 拉取最新代码
git pull origin master

# 3. 重新构建并重启所有服务
./docker-deploy.sh restart

# 或者单独重启某个服务
./docker-deploy.sh restart backend
./docker-deploy.sh restart h5
./docker-deploy.sh restart frontend
```

## 完整部署流程

### 首次部署

```bash
# 1. 安装 Docker 和 Docker Compose
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker

# 2. 配置 Docker 镜像加速（国内服务器必需）
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

# 3. 克隆项目
cd /opt
git clone https://github.com/windchargerKang/lisheng.git
cd lisheng-project

# 4. 构建并启动
./docker-deploy.sh build
./docker-deploy.sh start

# 5. 查看服务状态
./docker-deploy.sh status
```

### 更新代码

```bash
# 方式 1：使用部署脚本（推荐）
cd /opt/lisheng-project
git pull origin master
./docker-deploy.sh restart

# 方式 2：手动更新
cd /opt/lisheng-project
git pull origin master

# 停止服务
docker-compose down

# 重新构建（如有 Dockerfile 或依赖变更）
docker-compose build

# 启动服务
docker-compose up -d
```

### 查看日志

```bash
# 查看所有服务日志
./docker-deploy.sh logs

# 查看后端日志
./docker-deploy.sh logs backend
docker logs lisheng-backend

# 查看 H5 前端日志
./docker-deploy.sh logs h5
docker logs lisheng-h5

# 查看运营管理前端日志
./docker-deploy.sh logs frontend
docker logs lisheng-frontend

# 实时查看日志
docker logs -f lisheng-backend
```

### 服务管理

```bash
# 启动所有服务
./docker-deploy.sh start

# 停止所有服务
./docker-deploy.sh stop

# 重启所有服务
./docker-deploy.sh restart

# 查看服务状态
./docker-deploy.sh status

# 清理所有资源（包括数据）
./docker-deploy.sh clean
```

## 访问地址

部署完成后：

- **H5 前端（C 端用户）**: http://服务器IP:3000/
- **运营管理端（B 端管理）**: http://服务器IP:5173/
- **后端 API**: http://服务器IP:8000/
- **API 文档**: http://服务器IP:8000/docs

## 常见问题

### 1. 端口被占用

修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "8001:8000"  # 将 8000 改为 8001
```

### 2. 数据库初始化

```bash
# 进入后端容器
docker exec -it lisheng-backend bash

# 运行初始化脚本
python scripts/init_db.py
```

### 3. 进入容器调试

```bash
# 后端容器
docker exec -it lisheng-backend bash

# H5 前端容器
docker exec -it lisheng-h5 sh

# 运营管理前端容器
docker exec -it lisheng-frontend sh
```

### 4. 强制重新构建

```bash
# 停止服务
./docker-deploy.sh stop

# 清理旧镜像
docker-compose build --no-cache

# 重新启动
./docker-deploy.sh start
```

### 5. 数据持久化

数据已配置持久化到主机目录：

- 数据库：`./backend/channel_sales.db`
- 上传文件：`./backend/uploads/`
- 日志文件：`./backend/logs/`

修改 `docker-compose.yml` 中的 volumes 配置可调整持久化路径。

## 生产环境建议

1. **修改 SECRET_KEY**：编辑 `docker-compose.yml` 中的 `SECRET_KEY` 环境变量

2. **配置防火墙**：
   ```bash
   # 开放必要端口
   firewall-cmd --permanent --add-port=8000/tcp
   firewall-cmd --permanent --add-port=3000/tcp
   firewall-cmd --permanent --add-port=5173/tcp
   firewall-cmd --reload
   ```

3. **配置 HTTPS**：建议使用 nginx 反向代理配置 SSL 证书

4. **定期备份数据库**：
   ```bash
   cp ./backend/channel_sales.db ./backup/channel_sales.db.$(date +%Y%m%d)
   ```
