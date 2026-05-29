<template>
  <div class="dashboard">
    <div class="header-row">
      <h2>仪表盘</h2>
      <div class="export-row">
        <input type="date" v-model="exportStart" /> ~ <input type="date" v-model="exportEnd" />
        <button @click="doExport" class="btn-export">导出Excel</button>
      </div>
    </div>
    <div class="stats-row">
      <div class="stat-card"><div class="stat-num">{{ stats.total_links }}</div><div class="stat-label">总链接数</div></div>
      <div class="stat-card"><div class="stat-num">{{ stats.total_clicks }}</div><div class="stat-label">总点击量</div></div>
      <div class="stat-card"><div class="stat-num">{{ stats.today_clicks }}</div><div class="stat-label">今日点击</div></div>
    </div>
    <div class="charts-row">
      <div class="chart-box"><h3>近7天点击趋势</h3><canvas id="trendChart" height="120"></canvas></div>
      <div class="chart-box"><h3>国家分布</h3><canvas id="countryChart" height="120"></canvas></div>
    </div>
    <div class="top-links">
      <h3>热门链接 Top 10</h3>
      <table><thead><tr><th>短链</th><th>名称</th><th>点击量</th></tr></thead>
        <tbody><tr v-for="link in stats.top_links" :key="link.id">
          <td><a :href="'/s/'+link.short_code" target="_blank">/s/{{ link.short_code }}</a></td>
          <td>{{ link.title || '-' }}</td><td>{{ link.total_clicks }}</td>
        </tr></tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import api from '../api.js'
const stats = ref({ total_links: 0, total_clicks: 0, today_clicks: 0, daily_trend: [], top_links: [], countries: [] })
const exportStart = ref(''), exportEnd = ref('')
let trendChart, countryChart

onMounted(async () => {
  const data = await api.getOverview()
  if (data) stats.value = data
  const now = new Date()
  exportEnd.value = now.toISOString().slice(0,10)
  now.setDate(now.getDate() - 7)
  exportStart.value = now.toISOString().slice(0,10)
  await nextTick()
  renderCharts()
})

function renderCharts() {
  const tc = document.getElementById('trendChart'), cc = document.getElementById('countryChart')
  if (!tc || !cc) return
  trendChart = new Chart(tc, { type: 'line',
    data: { labels: stats.value.daily_trend.map(d => d.day.slice(5)), datasets: [{ label: '点击量', data: stats.value.daily_trend.map(d => d.c), borderColor: '#60a5fa', backgroundColor: 'rgba(96,165,250,0.1)', fill: true, tension: 0.3 }] },
    options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { grid: { color: '#334155' } }, x: { grid: { color: '#334155' } } } }
  })
  countryChart = new Chart(cc, { type: 'doughnut',
    data: { labels: stats.value.countries.map(c => c.country), datasets: [{ data: stats.value.countries.map(c => c.c), backgroundColor: ['#60a5fa','#34d399','#fbbf24','#f87171','#a78bfa','#22d3ee'] }] },
    options: { responsive: true, plugins: { legend: { position: 'right', labels: { color: '#e2e8f0' } } } }
  })
}

function doExport() {
  if (exportStart.value && exportEnd.value) api.exportStats(exportStart.value, exportEnd.value)
}
</script>

<style scoped>
.dashboard { padding: 1.5rem; max-width: 1200px; margin: 0 auto; }
.header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 0.5rem; }
h2 { font-size: 1.25rem; }
.export-row { display: flex; align-items: center; gap: 0.4rem; font-size: 0.85rem; }
.export-row input { padding: 0.3rem 0.5rem; border: 1px solid #334155; border-radius: 6px; background: #0f172a; color: #e2e8f0; color-scheme: dark; width: 130px; }
.btn-export { padding: 0.35rem 0.8rem; background: #059669; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.8rem; white-space: nowrap; }
.btn-export:hover { background: #10b981; }
.stats-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
.stat-card { flex: 1; background: #1e293b; padding: 1.25rem; border-radius: 10px; text-align: center; }
.stat-num { font-size: 2rem; font-weight: 700; color: #60a5fa; }
.stat-label { font-size: 0.85rem; color: #94a3b8; margin-top: 0.25rem; }
.charts-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
.chart-box { flex: 1; background: #1e293b; padding: 1.25rem; border-radius: 10px; }
.chart-box h3 { font-size: 0.95rem; margin-bottom: 0.75rem; color: #cbd5e1; }
.top-links { background: #1e293b; padding: 1.25rem; border-radius: 10px; }
.top-links h3 { font-size: 0.95rem; margin-bottom: 0.75rem; color: #cbd5e1; }
table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
th, td { padding: 0.6rem; text-align: left; border-bottom: 1px solid #334155; }
th { color: #94a3b8; font-weight: 500; }
td a { color: #60a5fa; text-decoration: none; }
</style>
