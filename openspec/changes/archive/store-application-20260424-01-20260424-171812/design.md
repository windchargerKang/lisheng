---
name: store-application-20260424-01
status: designed
---

# 技术方案：H5 端"我想开店"申请功能

## 方案概述
在 H5 端"我的"页面增加"我想开店"入口，允许普通客户在线提交升级为店铺或区代的申请。运营管理端提供审核功能，审核通过后自动升级用户角色。申请记录独立存储，与正式店铺/区代记录分离。

## 详细设计

### 架构变更

**后端新增文件**：
- `backend/app/models/store_application.py` - 申请数据模型
- `backend/app/api/v1/store_applications.py` - 申请管理 API

**后端修改文件**：
- `backend/app/api/v1/api.py` - 注册新路由
- `backend/app/models/__init__.py` - 导出新模型

**前端新增文件**：
- `h5/src/views/StoreApply.vue` - 申请页面
- `h5/src/views/StoreApplyRecords.vue` - 申请记录页面

**前端修改文件**：
- `h5/src/views/Profile.vue` - 增加"我想开店"入口

### 数据模型变更

```python
class StoreApplicationStatus(str, enum.Enum):
    PENDING = "PENDING"      # 待审核
    APPROVED = "APPROVED"    # 审核通过
    REJECTED = "REJECTED"    # 审核拒绝

class StoreApplicationType(str, enum.Enum):
    SHOP = "SHOP"            # 店铺申请
    AGENT = "AGENT"          # 区代申请

class StoreApplication(Base):
    __tablename__ = "store_applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    apply_type = Column(Enum(StoreApplicationType), nullable=False)
    
    # 店铺申请字段
    shop_name = Column(String(100), nullable=True)
    shop_region_id = Column(Integer, ForeignKey("regions.id"), nullable=True)
    shop_agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    shop_latitude = Column(Numeric(10, 8), nullable=True)
    shop_longitude = Column(Numeric(11, 8), nullable=True)
    
    # 区代申请字段
    agent_name = Column(String(100), nullable=True)
    agent_region_id = Column(Integer, ForeignKey("regions.id"), nullable=True)
    referrer_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    
    # 审核状态
    status = Column(Enum(StoreApplicationStatus), nullable=False, default=StoreApplicationStatus.PENDING)
    reject_reason = Column(String(500), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### 接口变更

**新增 API 端点**：

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | /store-applications/my | 获取当前用户的申请记录 | 用户 |
| POST | /store-applications | 提交申请 | 用户 |
| GET | /store-applications/{id} | 获取申请详情 | 用户/管理员 |
| GET | /store-applications | 获取申请列表（管理端） | 管理员 |
| POST | /store-applications/{id}/approve | 审核通过 | 管理员 |
| POST | /store-applications/{id}/reject | 审核拒绝 | 管理员 |

**区域重复性校验 API**：
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /store-applications/check-region?region_id=xxx&type=AGENT | 校验区域是否已被占用 |

### 影响范围
- 受影响模块：用户管理、店铺管理、区代管理、H5 端"我的"页面
- 受保护路径变更：无
- 向后兼容性：不影响现有功能

### 风险评估
| 风险 | 等级 | 缓解方案 |
|------|------|----------|
| 并发提交导致区代区域重复 | 中 | 后端加唯一索引 + 事务锁 |
| 审核通过时用户已被删除 | 低 | 加外键 RESTRICT 约束 |
| 地图选点失败 | 低 | 允许手动输入经纬度 |
| 审核通过时角色升级失败 | 中 | 使用事务保证原子性 |

### 事务与数据
- **事务边界**：审核通过时，创建 Shop/Agent 记录 + 更新用户 role_id 必须在同一事务中
- **数据迁移**：无需迁移
- **回滚方案**：审核通过失败时，事务自动回滚，申请状态保持 PENDING

### 测试策略
1. **单元测试**：
   - 申请表创建逻辑
   - 区域重复性校验逻辑
   - 审核通过/拒绝逻辑

2. **集成测试**：
   - 提交申请 API
   - 审核 API
   - 角色升级流程

3. **前端测试**：
   - 申请表单提交
   - 地图选点交互
   - 申请状态展示
