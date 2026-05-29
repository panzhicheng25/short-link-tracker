<template>
  <div class="link-detail">
    <div class="header-row">
      <h2>链接详情</h2>
      <button @click="doExport" class="btn-export">导出Excel</button>
    </div>
    <div class="info-box">
      <p><b>短链：</b><a :href="'/s/'+link.short_code" target="_blank">/s/{{ link.short_code }}</a></p>
      <p><b>原始链接：</b>{{ link.original_url }}</p>
      <p><b>备注：</b>{{ link.title || '-' }}</p>
      <p><b>总点击：</b>{{ stats.total }}</p>
    </div>
    <div class="charts-row">
      <div class="chart-box"><h3>设备分布</h3><canvas id="deviceChart"></canvas></div>
      <div class="chart-box"><h3>浏览器分布</h3><canvas id="browserChart"></canvas></div>
    </div>
    <div class="clicks-table">
      <h3>点击明细</h3>
      <table><thead><tr><th>时间</th><th>国家</th><th>城市</th><th>设备</th><th>浏览器</th><th>来源</th></tr></thead>
        <tbody><tr v-for="c in clicks" :key="c.id">
          <td>{{ (c.clicked_at || '').slice(0,16).replace('T',' ') }}</td>
          <td>{{ c.country || '-' }}</td><td>{{ c.city || '-' }}</td>
          <td>{{ c.device || '-' }}</td><td>{{ c.browser || '-' }}</td>
          <td class="url-cell">{{ c.referrer || '-' }}</td>
        </tr></tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api.js'
const route = useRoute()
const link = ref({})
const stats = ref({ total: 0, devices: [], browsers: [], countries: [], referrers: [] })
const clicks = ref([])
let deviceChart, browserChart

onMounted(async () => {
  const id = route.params.id
  const linkData = await api.listLinks()
  link.value = (linkData || []).find(l => l.id == id) || {}
  const s = await api.getStats(id)
  if (s) stats.value = s
  await nextTick()
  renderCharts()
})

function renderCharts() {
  const dc = document.getElementById('deviceChart'), bc = document.getElementById('browserChart')
  if (!dc || !bc) return
  deviceChart = new Chart(dc, { type: 'doughnut',
    data: { labels: stats.value.devices.map(d => d.device), datasets: [{ data: stats.value.devices.map(d => d.c), backgroundColor: ['#60a5fa','#34d399','#fbbf24'] }] },
    options: { responsive: true, plugins: { legend: { position: 'right', labels: { color: '#e2e8f0' } } } }
  })
  browserChart = new Chart(bc, { type: 'bar',
    data: { labels: stats.value.browsers.map(b => b.browser), datasets: [{ label: '点击量', data: stats.value.browsers.map(b => b.c), backgroundColor: '#60a5fa' }] },
    options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { grid: { color: '#334155' } }, x: { grid: { display: false } } } }
  })
}

function doExport() { api.exportLink(route.params.id) }
</script>

<style scoped>
.link-detail { padding: 1.5rem; max-width: 1200px; margin: 0 auto; }
.header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
h2 { font-size: 1.25rem; }
.btn-export { padding: 0.35rem 0.8rem; background: #059669; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.8rem; }
.btn-export:hover { background: #10b981; }
.info-box { background: #1e293b; padding: 1rem 1.5rem; border-radius: 10px; margin-bottom: 1.5rem; }
.info-box p { margin: 0.4rem 0; font-size: 0.9rem; }
.info-box a { color: #60a5fa; }
.charts-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
.chart-box { flex: 1; background: #1e293b; padding: 1.25rem; border-radius: 10px; }
.chart-box h3 { font-size: 0.9rem; margin-bottom: 0.75rem; color: #cbd5e1; }
.clicks-table { background: #1e293b; padding: 1.25rem; border-radius: 10px; }
.clicks-table h3 { font-size: 0.9rem; margin-bottom: 0.75rem; color: #cbd5e1; }
table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
th, td { padding: 0.5rem; text-align: left; border-bottom: 1px solid #334155; }
th { color: #94a3b8; font-weight: 500; }
.url-cell { max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
</style>
