# 远程部署文档

## 服务器信息

| 项目 | 值 |
|------|-----|
| 服务器 IP | 100.4.14.23 |
| SSH 用户 | root |
| 部署目录 | /opt/lisheng/lisheng-project |
| 前端端口 | 5173 |
| H5 端口 | 3000 |
| 后端端口 | 8000 |
| 外部访问 IP | 60.191.123.122 |

## 外部访问端口映射

| 服务 | 外部端口 | 用途 |
|------|---------|------|
| 运营管理端 | 40284 | Web 管理后台 |
| H5 端 | 40285 | 移动端页面 |
| 后端 API | 40286 | API 接口 |

---

## 部署前准备

### 1. SSH 连接

```bash
# 使用密码登录
ssh root@100.4.14.23
# 密码：passwd
```

### 2. 确认项目目录

```bash
cd /opt/lisheng/lisheng-project
ls -la
# 应包含：docker-compose.yml, backend/, frontend/, h5/
```

---

## 前端部署（运营管理端）

### 目录结构

```
/opt/lisheng/lisheng-project/frontend/
├── Dockerfile
├── nginx.conf          # 关键配置文件
├── package.json
├── vite.config.ts
└── dist/               # 构建产物（服务器本地）
```

### 关键配置：nginx.conf

**⚠️ 易错点 1：location 优先级**

```nginx
# ✅ 正确：/admin/assets/ 必须在 /admin/ 之前
location ^~ /admin/assets/ {
    alias /usr/share/nginx/html/assets/;
    expires 1y;
    add_header Cache-Control "public, immutable";
}

location ^~ /admin/ {
    alias /usr/share/nginx/html/;
    try_files $uri $uri/ /index.html;
}

location = /admin {
    alias /usr/share/nginx/html/index.html;
}
```

**错误示例**（会导致 404）：
```nginx
# ❌ 错误：/admin/ 在前会先匹配，导致 /admin/assets/ 永远无法命中
location /admin/ {
    alias /usr/share/nginx/html/;
}
location /admin/assets/ {
    alias /usr/share/nginx/html/assets/;
}
```

**⚠️ 易错点 2：alias 路径末尾斜杠**

```nginx
# ✅ 正确
location /admin/assets/ {
    alias /usr/share/nginx/html/assets/;
}

# ❌ 错误：末尾缺少斜杠会导致路径拼接错误
location /admin/assets/ {
    alias /usr/share/nginx/html/assets;
}
```

### 构建和部署步骤

```bash
# 1. 本地构建
cd frontend
npm run build

# 2. 上传到服务器
tar -czf frontend-dist.tar.gz -C dist .
SSHPASS='passwd' sshpass -e scp frontend-dist.tar.gz root@100.4.14.23:/tmp/

# 3. 服务器上解压
SSHPASS='passwd' sshpass -e ssh root@100.4.14.23 << 'EOF'
rm -rf /opt/lisheng/lisheng-project/frontend/dist
mkdir -p /opt/lisheng/lisheng-project/frontend/dist
tar -xzf /tmp/frontend-dist.tar.gz -C /opt/lisheng/lisheng-project/frontend/dist/
EOF

# 4. 复制文件到容器并重启
SSHPASS='passwd' sshpass -e ssh root@100.4.14.23 << 'EOF'
docker cp /opt/lisheng/lisheng-project/frontend/dist/. lisheng-frontend:/usr/share/nginx/html/
docker cp /opt/lisheng/lisheng-project/frontend/nginx.conf lisheng-frontend:/etc/nginx/conf.d/default.conf
docker exec lisheng-frontend nginx -s reload
EOF
```

### 验证

```bash
# 测试 CSS 文件访问
curl -sI 'http://100.4.14.23:5173/admin/assets/index-*.css' | head -3
# 应返回 HTTP/1.1 200 OK

# 测试页面访问
curl -s 'http://100.4.14.23:5173/admin/wallet' | grep -o 'title>.*</title'
# 应返回：title>渠道销售管理系统 - 运营端</title
```

---

## H5 端部署

### 目录结构

```
/opt/lisheng/lisheng-project/h5/
├── Dockerfile
├── nginx.conf          # 关键配置文件
├── package.json
├── vite.config.ts
└── dist/               # 构建产物
```

### 关键配置：nginx.conf

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # API 代理 - ⚠️ 必须配置，否则 H5 无法调用后端
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态资源
    location /assets/ {
        alias /usr/share/nginx/html/assets/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # SPA 路由
    location / {
        try_files $uri $uri/ /index.html;
    }

    # uploads 目录代理
    location /uploads/ {
        proxy_pass http://backend:8000/uploads/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

**⚠️ 易错点：H5 的 nginx 必须配置 /api/ 代理**

H5 端没有独立的后端服务，所有 API 请求通过 nginx 代理到 backend:8000，缺少此配置会导致 405/404 错误。

### 构建和部署步骤

```bash
# 1. 本地构建
cd h5
npm run build

# 2. 上传到服务器
tar -czf h5-dist.tar.gz -C dist .
SSHPASS='passwd' sshpass -e scp h5-dist.tar.gz root@100.4.14.23:/tmp/

# 3. 服务器上解压
SSHPASS='passwd' sshpass -e ssh root@100.4.14.23 << 'EOF'
rm -rf /opt/lisheng/lisheng-project/h5/dist
mkdir -p /opt/lisheng/lisheng-project/h5/dist
tar -xzf /tmp/h5-dist.tar.gz -C /opt/lisheng/lisheng-project/h5/dist/
EOF

# 4. 复制文件到容器并重启
SSHPASS='passwd' sshpass -e ssh root@100.4.14.23 << 'EOF'
docker cp /opt/lisheng/lisheng-project/h5/dist/. lisheng-h5:/usr/share/nginx/html/
docker cp /opt/lisheng/lisheng-project/h5/nginx.conf lisheng-h5:/etc/nginx/conf.d/default.conf
docker restart lisheng-h5
EOF
```

### 验证

```bash
# 测试登录接口
curl -sX POST 'http://100.4.14.23:3000/api/v1/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}'
# 应返回 token 信息

# 测试 H5 页面
curl -s 'http://100.4.14.23:3000/' | grep -o 'title>.*</title'
```

---

## 后端服务部署

### 目录结构

```
/opt/lisheng/lisheng-project/backend/
├── app/
│   ├── api/
│   ├── main.py
│   └── ...
├── requirements.txt
├── uploads/            # ⚠️ 重要：产品图片等上传文件
└── data/
    └── channel_sales.db  # ⚠️ 重要：SQLite 数据库
```

### 关键配置：docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: lisheng-backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      # ⚠️ 必须挂载 uploads 目录，否则产品图片 404
      - ./backend/uploads:/app/uploads
      # ⚠️ 必须挂载 logs 目录，否则日志丢失
      - ./backend/logs:/app/logs
      # ⚠️ 数据库挂载 - 确保路径正确
      - ./backend/data/channel_sales.db:/app/data/channel_sales.db
    environment:
      - DATABASE_URL=sqlite+aiosqlite:////app/data/channel_sales.db
    networks:
      - lisheng-network

  frontend:
    # ... 见前端配置

  h5:
    # ... 见 H5 配置
```

**⚠️ 易错点 1：数据库挂载路径**

```yaml
# ✅ 正确：挂载单个文件
- ./backend/data/channel_sales.db:/app/data/channel_sales.db

# ⚠️ 可能问题：挂载目录但容器内路径不匹配
- ./backend/data:/app/data
# 如果容器内代码使用 /app/data/channel_sales.db 则没问题
# 如果代码使用其他路径则需要对齐
```

**⚠️ 易错点 2：uploads 目录必须挂载**

产品图片存储在 `backend/uploads/products/`，如果不挂载：
- 容器重启后图片丢失
- 多容器间图片不共享

```yaml
# ✅ 正确
- ./backend/uploads:/app/uploads
```

### 部署步骤

```bash
# 1. 确保 uploads 目录已上传到服务器
# 首次部署时需要：
SSHPASS='passwd' sshpass -e scp -r backend/uploads root@100.4.14.23:/opt/lisheng/lisheng-project/backend/

# 2. 重启后端服务
cd /opt/lisheng/lisheng-project
docker-compose up -d backend

# 3. 验证数据库挂载
docker exec lisheng-backend ls -la /app/data/
# 应看到 channel_sales.db 文件

# 4. 验证 uploads 挂载
docker exec lisheng-backend ls /app/uploads/products/
# 应看到产品图片文件
```

### 验证

```bash
# 测试 API 健康检查
curl -s 'http://100.4.14.23:8000/docs' | head -5

# 测试产品图片访问
curl -sI 'http://100.4.14.23:8000/uploads/products/*.png' | head -3
# 应返回 200 OK

# 测试用户列表接口
curl -s 'http://100.4.14.23:8000/api/v1/users?page=1&page_size=10' | jq '.total'
```

---

## 完整部署流程

### 方式一：使用部署脚本（推荐）

```bash
#!/bin/bash
# deploy.sh

SERVER="100.4.14.23"
PASSWORD="passwd"
export SSHPASS="$PASSWORD"

echo "=== 构建前端 ==="
cd frontend && npm run build && cd ..
tar -czf frontend-dist.tar.gz -C frontend/dist .
sshpass -e scp frontend-dist.tar.gz root@$SERVER:/tmp/

echo "=== 构建 H5 ==="
cd h5 && npm run build && cd ..
tar -czf h5-dist.tar.gz -C h5/dist .
sshpass -e scp h5-dist.tar.gz root@$SERVER:/tmp/

echo "=== 上传 uploads 目录 ==="
sshpass -e scp -r backend/uploads root@$SERVER:/opt/lisheng/lisheng-project/backend/

echo "=== 服务器部署 ==="
sshpass -e ssh root@$SERVER << 'ENDSSH'
cd /opt/lisheng/lisheng-project

# 解压前端
rm -rf frontend/dist && mkdir -p frontend/dist
tar -xzf /tmp/frontend-dist.tar.gz -C frontend/dist/

# 解压 H5
rm -rf h5/dist && mkdir -p h5/dist
tar -xzf /tmp/h5-dist.tar.gz -C h5/dist/

# 复制文件到容器
docker cp frontend/dist/. lisheng-frontend:/usr/share/nginx/html/
docker cp frontend/nginx.conf lisheng-frontend:/etc/nginx/conf.d/default.conf
docker cp h5/dist/. lisheng-h5:/usr/share/nginx/html/
docker cp h5/nginx.conf lisheng-h5:/etc/nginx/conf.d/default.conf

# 重启服务
docker restart lisheng-frontend lisheng-h5
docker exec lisheng-frontend nginx -s reload
docker exec lisheng-h5 nginx -s reload

# 清理
rm /tmp/frontend-dist.tar.gz /tmp/h5-dist.tar.gz
ENDSSH

echo "=== 部署完成 ==="
rm frontend-dist.tar.gz h5-dist.tar.gz
```

### 方式二：手动部署

```bash
# 1. 构建并上传前端
cd frontend && npm run build
tar -czf frontend-dist.tar.gz -C dist .
SSHPASS='passwd' sshpass -e scp frontend-dist.tar.gz root@100.4.14.23:/tmp/

# 2. 构建并上传 H5
cd ../h5 && npm run build
tar -czf h5-dist.tar.gz -C dist .
SSHPASS='passwd' sshpass -e scp h5-dist.tar.gz root@100.4.14.23:/tmp/

# 3. 服务器上解压部署
SSHPASS='passwd' sshpass -e ssh root@100.4.14.23 << 'EOF'
# 解压前端
rm -rf /opt/lisheng/lisheng-project/frontend/dist
mkdir -p /opt/lisheng/lisheng-project/frontend/dist
tar -xzf /tmp/frontend-dist.tar.gz -C /opt/lisheng/lisheng-project/frontend/dist/

# 解压 H5
rm -rf /opt/lisheng/lisheng-project/h5/dist
mkdir -p /opt/lisheng/lisheng-project/h5/dist
tar -xzf /tmp/h5-dist.tar.gz -C /opt/lisheng/lisheng-project/h5/dist/

# 复制到容器
docker cp /opt/lisheng/lisheng-project/frontend/dist/. lisheng-frontend:/usr/share/nginx/html/
docker cp /opt/lisheng/lisheng-project/frontend/nginx.conf lisheng-frontend:/etc/nginx/conf.d/default.conf
docker cp /opt/lisheng/lisheng-project/h5/dist/. lisheng-h5:/usr/share/nginx/html/
docker cp /opt/lisheng/lisheng-project/h5/nginx.conf lisheng-h5:/etc/nginx/conf.d/default.conf

# 重启
docker restart lisheng-frontend lisheng-h5
docker exec lisheng-frontend nginx -s reload
docker exec lisheng-h5 nginx -s reload

# 清理临时文件
rm /tmp/frontend-dist.tar.gz /tmp/h5-dist.tar.gz
EOF

# 4. 清理本地
rm frontend-dist.tar.gz h5-dist.tar.gz
```

---

## 常见问题排查

### 1. 前端 404 错误

**症状**：`/admin/assets/*.css` 返回 404

**原因**：nginx location 优先级错误

**解决**：
```bash
# 检查容器内配置
docker exec lisheng-frontend cat /etc/nginx/conf.d/default.conf | grep -A 3 'location /admin'

# 确保 /admin/assets/ 在 /admin/ 之前
# 修改后重启
docker exec lisheng-frontend nginx -s reload
```

### 2. 产品图片 404

**症状**：`/uploads/products/*.png` 返回 404

**原因**：uploads 目录未挂载或文件未上传

**解决**：
```bash
# 检查 uploads 是否挂载
docker exec lisheng-backend ls /app/uploads/products/

# 如果为空，上传文件
SSHPASS='passwd' sshpass -e scp -r backend/uploads root@100.4.14.23:/opt/lisheng/lisheng-project/backend/

# 重启后端
docker restart lisheng-backend
```

### 3. H5 登录 405 错误

**症状**：POST `/api/v1/auth/login` 返回 405

**原因**：H5 的 nginx 缺少 /api/ 代理配置

**解决**：
```bash
# 检查 H5 nginx 配置
docker exec lisheng-h5 cat /etc/nginx/conf.d/default.conf | grep -A 5 '/api/'

# 如果没有，更新 nginx.conf 添加：
# location /api/ {
#     proxy_pass http://backend:8000;
#     proxy_set_header Host $host;
#     proxy_set_header X-Real-IP $remote_addr;
# }
```

### 4. 数据库重置

**症状**：重启后数据丢失

**原因**：数据库挂载路径错误

**解决**：
```bash
# 检查数据库文件
docker exec lisheng-backend ls -la /app/data/

# 检查挂载配置
cat docker-compose.yml | grep -A 2 'volumes:'

# 确保挂载正确
- ./backend/data/channel_sales.db:/app/data/channel_sales.db
```

### 5. 浏览器缓存问题

**症状**：部署后页面仍显示旧内容

**解决**：
1. 强制刷新：Ctrl+Shift+R (Windows) / Cmd+Shift+R (Mac)
2. 清除浏览器缓存
3. 使用无痕模式测试

---

## 快速验证清单

部署完成后执行以下检查：

```bash
SERVER="100.4.14.23"

# 1. 前端 CSS 加载
curl -sI "http://$SERVER:5173/admin/assets/index-*.css" | grep "200 OK"

# 2. H5 登录接口
curl -sX POST "http://$SERVER:3000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq '.access_token'

# 3. 后端 API
curl -s "http://$SERVER:8000/api/v1/shops?page=1" | jq '.total'

# 4. 产品图片
curl -sI "http://$SERVER:8000/uploads/products/*.png" | grep "200 OK"

# 5. 数据库状态
SSHPASS='passwd' sshpass -e ssh root@$SERVER \
  "docker exec lisheng-backend sqlite3 /app/data/channel_sales.db 'SELECT COUNT(*) FROM shops;'"
```

---

## 数据库迁移

### 产品分润比例迁移

执行以下 SQL 脚本添加产品分润比例字段：

```sql
-- 新增服务费比例字段 (0.3000 = 30%)
ALTER TABLE products ADD COLUMN service_fee_rate NUMERIC(5, 4);

-- 新增区代利润比例字段 (0.1000 = 10%)
ALTER TABLE products ADD COLUMN agent_profit_rate NUMERIC(5, 4);
```

**执行方式**：
```bash
# SSH 到服务器
ssh root@100.4.14.23

# 进入项目目录
cd /opt/lisheng/lisheng-project

# 执行 SQL 迁移
sqlite3 backend/data/channel_sales.db < backend/migrations/add_product_profit_rate.sql
```

---

## 附录：关键文件路径

| 文件 | 服务器路径 | 用途 |
|------|-----------|------|
| 前端 nginx 配置 | /etc/nginx/conf.d/default.conf (容器内) | 前端路由和静态资源 |
| H5 nginx 配置 | /etc/nginx/conf.d/default.conf (容器内) | H5 路由和 API 代理 |
| 数据库 | /opt/lisheng/lisheng-project/backend/data/channel_sales.db | SQLite 数据 |
| 上传文件 | /opt/lisheng/lisheng-project/backend/uploads/ | 产品图片等 |
| 前端 dist | /opt/lisheng/lisheng-project/frontend/dist/ | 构建产物 |
| H5 dist | /opt/lisheng/lisheng-project/h5/dist/ | 构建产物 |
| 迁移脚本 | /opt/lisheng/lisheng-project/backend/migrations/ | 数据库迁移脚本 |
