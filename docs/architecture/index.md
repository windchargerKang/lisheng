# 架构总览

## 项目类型

前端项目

## 技术栈

待补充 - 请根据实际使用的框架（React/Vue/Angular 等）更新此部分

## 目录结构

```
project-root/
├── src/
│   ├── components/     # 可复用组件
│   ├── pages/          # 页面组件
│   ├── services/       # API 服务层
│   ├── store/          # 状态管理
│   ├── utils/          # 工具函数
│   └── styles/         # 样式文件
├── public/             # 静态资源
├── tests/              # 测试文件
├── docs/               # 项目文档
│   ├── architecture/   # 架构文档
│   ├── product/        # 产品文档
│   └── standards/      # 开发规范
└── openspec/           # OpenSpec 变更管理
    ├── changes/        # 变更工件
    └── specs/          # 系统规格
```

## 架构原则

1. **组件化**：UI 拆分为独立可复用的组件
2. **单向数据流**：状态变化遵循可预测的流向
3. **关注点分离**：UI、业务逻辑、数据访问分离
4. **类型安全**：优先使用 TypeScript

## 必读文件

- [产品规则](../product/index.md)
- [测试规范](../standards/testing.md)
- [隐性业务约定](implicit-contracts.md)
