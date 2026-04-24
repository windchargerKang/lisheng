<template>
  <div class="team-page">
    <van-nav-bar
      title="我的团队"
      left-arrow
      @click-left="$router.back()"
    />

    <van-list
      v-model:loading="loading"
      :finished="finished"
      finished-text="没有更多成员了"
      @load="onLoad"
    >
      <van-cell
        v-for="member in teamMembers"
        :key="member.id"
        :title="member.username"
        :label="`${getRoleText(member.role_type)} | 加入时间：${formatDate(member.created_at)}`"
      >
        <template #icon>
          <van-icon name="user-o" size="40" color="#1989fa" />
        </template>
      </van-cell>
    </van-list>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import apiClient from '@/api'

const loading = ref(false)
const finished = ref(false)
const teamMembers = ref<any[]>([])

const getRoleText = (roleType: string): string => {
  const textMap: Record<string, string> = {
    customer: '客户',
    shop: '店铺',
    agent: '区代',
    admin: '管理员',
  }
  return textMap[roleType] || '未知'
}

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

const fetchTeam = async () => {
  loading.value = true
  try {
    const params = {
      page: 1,
      page_size: 10,
    }
    const response = await apiClient.get('/referral/team', { params })
    teamMembers.value = response.data.items || []
    finished.value = teamMembers.value.length < 10
  } catch (error) {
    console.error('获取团队列表失败:', error)
  } finally {
    loading.value = false
  }
}

const onLoad = () => {
  fetchTeam()
}
</script>

<style scoped>
.team-page {
  min-height: 100vh;
  background-color: #f5f5f5;
}
</style>
