<template>
  <div class="login-page">
    <div class="login-box">
      <h1>短链追踪系统</h1>
      <input v-model="username" placeholder="账号" />
      <input v-model="password" type="password" placeholder="密码" />
      <button @click="login" :disabled="loading">{{ loading ? '登录中...' : '登录' }}</button>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api.js'
const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
async function login() {
  loading.value = true
  error.value = ''
  const res = await api.login(username.value, password.value)
  loading.value = false
  if (res && res.token) {
    localStorage.setItem('token', res.token)
    router.push('/')
  } else {
    error.value = res?.error || '登录失败'
  }
}
</script>

<style scoped>
.login-page { display: flex; justify-content: center; align-items: center; min-height: 100vh; background: #0f172a; }
.login-box { background: #1e293b; padding: 2.5rem; border-radius: 12px; width: 320px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
h1 { text-align: center; margin-bottom: 1.5rem; color: #60a5fa; font-size: 1.3rem; }
input { width: 100%; padding: 0.75rem; margin-bottom: 0.75rem; border: 1px solid #334155; border-radius: 8px; background: #0f172a; color: #e2e8f0; font-size: 0.9rem; }
button { width: 100%; padding: 0.75rem; background: #2563eb; color: white; border: none; border-radius: 8px; font-size: 0.9rem; cursor: pointer; }
button:hover { background: #3b82f6; }
.error { color: #ef4444; text-align: center; margin-top: 0.5rem; font-size: 0.85rem; }
</style>
