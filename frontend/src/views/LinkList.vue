<template>
  <div class="link-list">
    <div class="header-row">
      <h2>链接管理</h2>
      <div class="header-btns">
        <input type="file" accept=".xlsx,.xls" @change="onFileChange" ref="fileInput" hidden />
        <button class="btn-upload" @click="pickFile">上传Excel</button>
        <button class="btn-batch" @click="showBatch=true">批量粘贴</button>
        <button class="btn-download" @click="downloadAll">下载三列</button>
        <button v-if="selectedIds.length" class="btn-export-sel" @click="exportSelected">
          导出选中({{ selectedIds.length }})
        </button>
      </div>
    </div>
    <div v-if="importedRows.length" class="import-section">
      <div class="import-header">
        <span>已解析 {{ importedRows.length }} 条数据</span>
        <button class="btn-generate" @click="doBatchGenerate" :disabled="generating">
          {{ generating ? '生成中...' : '批量生成短链' }}
        </button>
      </div>
      <table class="preview-table">
        <thead><tr><th>#</th><th>剧名</th><th>分销链接</th><th>状态</th></tr></thead>
        <tbody>
          <tr v-for="(row,i) in importedRows" :key="i">
            <td>{{ i+1 }}</td><td>{{ row.title || '-' }}</td>
            <td class="url-cell">{{ row.original_url }}</td>
            <td>待生成</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="create-box">
      <input v-model="newUrl" placeholder="分销链接" />
      <input v-model="newTitle" placeholder="剧名" />
      <button @click="create" :disabled="creating">{{ creating ? '...' : '生成' }}</button>
      <input v-model="search" placeholder="搜索剧名..." class="search-input" />
    </div>
    <p v-if="copied" class="copied">已复制到剪贴板！</p>
    <table>
      <thead><tr>
        <th><input type="checkbox" @change="toggleAll" v-model="allChecked" /></th>
        <th>短链</th><th>剧名</th><th>分销链接</th><th>点击</th>
        <th>最后点击</th><th>创建时间</th><th>操作</th>
      </tr></thead>
      <tbody><tr v-for="link in filteredLinks" :key="link.id">
        <td><input type="checkbox" :value="link.id" v-model="selectedIds" /></td>
        <td><a :href="'/s/'+link.short_code" target="_blank">/s/{{ link.short_code }}</a></td>
        <td>{{ link.title || '-' }}</td><td class="url-cell">{{ link.original_url }}</td>
        <td>{{ link.total_clicks }}</td><td>{{ formatTime(link.last_click_at) }}</td>
        <td>{{ formatTime(link.created_at) }}</td>
        <td>
          <button class="btn-copy" @click="copy(link.short_code)">复制</button>
          <button class="btn-detail" @click="goDetail(link.id)">详情</button>
          <button class="btn-export" @click="exportOne(link.id)">导出</button>
          <button class="btn-delete" @click="remove(link.id)">删除</button>
        </td>
      </tr></tbody>
    </table>
    <div v-if="showBatch" class="modal" @click.self="showBatch=false">
      <div class="modal-box">
        <h3>批量粘贴短链</h3><p class="hint">每行一个分销链接</p>
        <textarea v-model="batchText" rows="8"></textarea>
        <div class="modal-btns">
          <button class="btn-cancel" @click="showBatch=false">取消</button>
          <button class="btn-submit" @click="doBatch" :disabled="batching">{{ batching?'...':'批量生成' }}</button>
        </div>
        <p v-if="batchResult" class="batch-ok">完成！{{ batchResult }} 条</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import apiObj from '../api.js'
const router = useRouter()
const links = ref([])
const newUrl = ref(''), newTitle = ref(''), creating = ref(false), copied = ref(false)
const search = ref('')
const showBatch = ref(false), batchText = ref(''), batching = ref(false), batchResult = ref(0)
const importedRows = ref([]), generating = ref(false)
const selectedIds = ref([]), allChecked = ref(false)
const fileInput = ref(null)

onMounted(load)
async function load() { links.value = await apiObj.listLinks() || [] }

const filteredLinks = computed(() => {
  if (!search.value) return links.value
  return links.value.filter(l => (l.title||'').includes(search.value))
})

// 全选逻辑
const allLinkIds = computed(() => filteredLinks.value.map(l => l.id))
watch(allLinkIds, () => {
  allChecked.value = allLinkIds.value.length > 0 && 
    allLinkIds.value.every(id => selectedIds.value.includes(id))
})
function toggleAll() {
  if (allChecked.value) {
    selectedIds.value = [...allLinkIds.value]
  } else {
    selectedIds.value = []
  }
}

function formatTime(t) { return t ? t.slice(0,16).replace('T',' ') : '-' }
function goDetail(id) { router.push('/links/'+id) }

async function create() {
  if (!newUrl.value) return; creating.value = true
  await apiObj.createLink({ original_url: newUrl.value, title: newTitle.value })
  creating.value = false; newUrl.value = ''; newTitle.value = ''; await load()
}
function pickFile() { fileInput.value.click() }

async function onFileChange(e) {
  const file = e.target.files[0]; if (!file) return
  const res = await apiObj.uploadExcel(file)
  if (res && res.rows) importedRows.value = res.rows
  e.target.value = ''
}
async function doBatchGenerate() {
  if (!importedRows.value.length) return; generating.value = true
  const res = await apiObj.batchGenerate(importedRows.value)
  generating.value = false
  if (res && res.results) { importedRows.value = []; await load() }
}
async function doBatch() {
  if (!batchText.value.trim()) return; batching.value = true
  const res = await apiObj.batchCreateLinks(batchText.value)
  batching.value = false
  if (res) { batchResult.value = res.count; batchText.value = ''; await load() }
}
async function remove(id) {
  if (!confirm('确定删除？')) return
  await apiObj.deleteLink(id); await load()
}
function copy(code) {
  navigator.clipboard.writeText(location.origin+'/s/'+code)
  copied.value = true; setTimeout(() => copied.value = false, 2000)
}
function exportOne(id) { apiObj.exportLink(id) }
function downloadAll() { apiObj.downloadAllLinks() }
function exportSelected() {
  if (selectedIds.value.length) apiObj.exportSelected(selectedIds.value)
}
</script>

<style scoped>
.link-list { padding: 1.5rem; max-width: 1300px; margin: 0 auto; }
.header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; }
h2 { font-size: 1.25rem; }
.header-btns { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.header-btns button { padding: 0.45rem 0.9rem; border: none; border-radius: 8px; cursor: pointer; font-size: 0.8rem; color: white; }
.btn-upload { background: #7c3aed; }
.btn-batch { background: #059669; }
.btn-download { background: #2563eb; }
.btn-export-sel { background: #f59e0b; }
.import-section { background: #1e293b; padding: 1rem; border-radius: 10px; margin-bottom: 1rem; }
.import-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
.import-header span { color: #94a3b8; font-size: 0.85rem; }
.btn-generate { padding: 0.45rem 1rem; background: #2563eb; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.8rem; }
.preview-table { width: 100%; font-size: 0.78rem; }
.preview-table th, .preview-table td { padding: 0.4rem; text-align: left; border-bottom: 1px solid #334155; }
.preview-table th { color: #94a3b8; }
.create-box { display: flex; gap: 0.5rem; margin-bottom: 1rem; flex-wrap: wrap; }
.create-box input { padding: 0.6rem; border: 1px solid #334155; border-radius: 8px; background: #0f172a; color: #e2e8f0; }
.create-box input:first-child { flex: 2; min-width: 200px; }
.create-box input:nth-child(2) { flex: 1; min-width: 100px; }
.search-input { flex: 1; min-width: 120px; }
.create-box button { padding: 0.6rem 1rem; background: #2563eb; color: white; border: none; border-radius: 8px; cursor: pointer; white-space: nowrap; }
.copied { color: #34d399; margin-bottom: 0.5rem; font-size: 0.85rem; }
table { width: 100%; border-collapse: collapse; font-size: 0.78rem; background: #1e293b; border-radius: 10px; overflow: hidden; }
th, td { padding: 0.55rem; text-align: left; border-bottom: 1px solid #334155; }
th { color: #94a3b8; font-weight: 500; white-space: nowrap; }
td a { color: #60a5fa; text-decoration: none; }
.url-cell { max-width: 240px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
input[type="checkbox"] { width: 15px; height: 15px; cursor: pointer; accent-color: #2563eb; }
button[class^="btn-"] { padding: 0.25rem 0.5rem; border: none; border-radius: 4px; font-size: 0.72rem; cursor: pointer; margin-right: 0.2rem; }
.btn-copy { background: #2563eb; color: white; }
.btn-detail { background: #475569; color: white; }
.btn-export { background: #059669; color: white; }
.btn-delete { background: #ef4444; color: white; }
.modal { position: fixed; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.6); display:flex; justify-content:center; align-items:center; z-index:100; }
.modal-box { background: #1e293b; padding: 2rem; border-radius: 12px; width: 500px; max-width: 90vw; }
.modal-box h3 { margin-bottom: 0.5rem; }
.hint { color: #94a3b8; font-size: 0.8rem; margin-bottom: 0.75rem; }
textarea { width:100%; padding:0.75rem; border:1px solid #334155; border-radius:8px; background:#0f172a; color:#e2e8f0; font-size:0.85rem; resize:vertical; }
.modal-btns { display:flex; gap:0.5rem; margin-top:1rem; justify-content:flex-end; }
.modal-btns button { padding:0.5rem 1.2rem; border:none; border-radius:8px; cursor:pointer; }
.btn-cancel { background:#475569; color:white; }
.btn-submit { background:#2563eb; color:white; }
.batch-ok { color:#34d399; margin-top:0.75rem; font-size:0.85rem; }
</style>