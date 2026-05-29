const BASE = '/api'

async function request(url, opts = {}) {
  const token = localStorage.getItem('token')
  const headers = { ...opts.headers }
  if (token) headers['Authorization'] = `Bearer ${token}`
  if (!opts.raw) headers['Content-Type'] = 'application/json'
  const res = await fetch(BASE + url, { ...opts, headers })
  if (res.status === 401) {
    localStorage.removeItem('token')
    window.location.hash = '#/login'
    return
  }
  return res.json()
}

export default {
  login: (u, p) => request('/auth/login', { method: 'POST', body: JSON.stringify({ username: u, password: p }) }),
  createLink: (data) => request('/links', { method: 'POST', body: JSON.stringify(data) }),
  batchCreateLinks: (text) => request('/links/batch', { method: 'POST', body: JSON.stringify({ text }) }),
  batchGenerate: (links) => request('/links/batch-generate', { method: 'POST', body: JSON.stringify({ links }) }),
  listLinks: () => request('/links'),
  deleteLink: (id) => request(`/links/${id}`, { method: 'DELETE' }),
  getOverview: () => request('/stats/overview'),
  getStats: (id) => request(`/stats/${id}`),

  // Excel 上传
  uploadExcel: async (file) => {
    const token = localStorage.getItem('token')
    const fd = new FormData()
    fd.append('file', file)
    const res = await fetch(`${BASE}/links/import-excel`, {
      method: 'POST', headers: { Authorization: `Bearer ${token}` }, body: fd
    })
    return res.json()
  },

  // 下载全部短链三列
  downloadAllLinks: async () => {
    const token = localStorage.getItem('token')
    const res = await fetch(`${BASE}/links/download-all`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.ok) {
      const blob = await res.blob()
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = 'all_links.xlsx'
      a.click()
    }
  },

  exportLink: async (id) => {
    const token = localStorage.getItem('token')
    const res = await fetch(`${BASE}/links/${id}/export`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.ok) {
      const blob = await res.blob()
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = `link_${id}_export.xlsx`
      a.click()
    }
  },


  // 导出选中的多条
  exportSelected: async (ids) => {
    const token = localStorage.getItem('token')
    const res = await fetch(`${BASE}/links/export-selected`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ ids })
    })
    if (res.ok) {
      const blob = await res.blob()
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = 'selected_links.xlsx'
      a.click()
    }
  },
  exportStats: async (start, end) => {
    const token = localStorage.getItem('token')
    const res = await fetch(`${BASE}/stats/export?start=${start}&end=${end}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.ok) {
      const blob = await res.blob()
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = `export_${start}_${end}.xlsx`
      a.click()
    }
  },
}
