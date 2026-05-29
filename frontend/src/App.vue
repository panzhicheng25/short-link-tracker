<template>
  <div class="app">
    <nav v-if="isLoggedIn" class="navbar">
      <div class="nav-brand">短链追踪</div>
      <div class="nav-links">
        <router-link to="/">仪表盘</router-link>
        <router-link to="/links">链接管理</router-link>
        <a href="#" @click.prevent="logout">退出</a>
      </div>
    </nav>
    <router-view />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()
const isLoggedIn = computed(() => !!localStorage.getItem('token'))
function logout() {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style scoped>
.navbar { display: flex; justify-content: space-between; align-items: center; padding: 1rem 2rem; background: #1e293b; border-bottom: 1px solid #334155; }
.nav-brand { font-size: 1.25rem; font-weight: 700; color: #60a5fa; }
.nav-links { display: flex; gap: 1.5rem; }
.nav-links a { color: #94a3b8; text-decoration: none; font-size: 0.9rem; }
.nav-links a:hover, .nav-links a.router-link-active { color: #60a5fa; }
</style>
