<template>
  <div class="dashboard">
    <h2>欢迎使用渠道销售管理系统</h2>
    <el-row :gutter="20" style="margin-top: 30px">
      <el-col :span="6">
        <el-card>
          <div class="stat-card">
            <el-icon :size="40" color="#409EFF"><Shop /></el-icon>
            <div class="stat-info">
              <div class="stat-value">0</div>
              <div class="stat-label">店铺总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-card">
            <el-icon :size="40" color="#67C23A"><User /></el-icon>
            <div class="stat-info">
              <div class="stat-value">0</div>
              <div class="stat-label">区代总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-card">
            <el-icon :size="40" color="#E6A23C"><Goods /></el-icon>
            <div class="stat-info">
              <div class="stat-value">0</div>
              <div class="stat-label">产品总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-card">
            <el-icon :size="40" color="#F56C6C"><Location /></el-icon>
            <div class="stat-info">
              <div class="stat-value">0</div>
              <div class="stat-label">区域总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
// 仪表盘页面 - 后续会接入真实数据
</script>

<style scoped>
.dashboard h2 {
  color: #303133;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}
</style>
