# 渠道销售管理系统 - Vue 3 Web 运营端

## 技术栈

- Vue 3 + TypeScript
- Vite 5
- Element Plus
- Pinia (状态管理)
- Vue Router (路由)
- Axios (HTTP 客户端)

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

访问：http://localhost:5173

### 3. 构建生产版本

```bash
npm run build
```

### 4. 预览生产构建

```bash
npm run preview
```

## 项目结构

```
frontend/
├── src/
│   ├── api/              # API 客户端
│   ├── assets/           # 静态资源
│   ├── components/       # 通用组件
│   ├── composables/      # 组合式函数
│   ├── layouts/          # 布局组件
│   ├── router/           # 路由配置
│   ├── stores/           # Pinia 状态管理
│   ├── types/            # TypeScript 类型定义
│   ├── utils/            # 工具函数
│   ├── views/            # 页面组件
│   ├── App.vue           # 根组件
│   └── main.ts           # 入口文件
├── public/               # 公共静态资源
├── tests/                # 测试文件
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## 页面路由

| 路径 | 组件 | 说明 |
|------|------|------|
| /login | Login.vue | 登录页 |
| /dashboard | Dashboard.vue | 仪表盘 |
| /regions | Regions.vue | 区域管理 |
| /shops | Shops.vue | 店铺管理 |
| /agents | Agents.vue | 区代管理 |
| /products | Products.vue | 产品管理 |

## 运行测试

```bash
npm run test
```
