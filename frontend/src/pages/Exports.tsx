import React, { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import api from '../services/api'
import { Download } from 'lucide-react'
import './Exports.css'
import './shared.css'

const Exports: React.FC = () => {
  const [exportType, setExportType] = useState('devices')
  const [format, setFormat] = useState('csv')

  const exportData = useMutation({
    mutationFn: async ({ type, format }: { type: string; format: string }) => {
      const res = await api.get(`/exports/${type}`, {
        params: { format },
        responseType: 'blob',
      })
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `malsiftcnd-${type}-${new Date().toISOString()}.${format}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    },
    onError: (error: any) => {
      console.error('Failed to export data:', error)
      alert(`Failed to export data: ${error.response?.data?.detail || error.message}`)
    },
  })

  const handleExport = () => {
    exportData.mutate({ type: exportType, format })
  }

  return (
    <div className="exports-page">
      <div className="page-header">
        <h1>Data Exports</h1>
      </div>

      <div className="export-card">
        <h2>Export Configuration</h2>
        <div className="form-group">
          <label>Export Type</label>
          <select value={exportType} onChange={(e) => setExportType(e.target.value)}>
            <option value="devices">Devices</option>
            <option value="scans">Scans</option>
            <option value="new_devices">New Devices (Last 24h)</option>
          </select>
        </div>
        <div className="form-group">
          <label>Format</label>
          <select value={format} onChange={(e) => setFormat(e.target.value)}>
            <option value="csv">CSV</option>
            <option value="json">JSON</option>
          </select>
        </div>
        <button className="btn-primary" onClick={handleExport} disabled={exportData.isPending}>
          <Download size={20} />
          {exportData.isPending ? 'Exporting...' : 'Export Data'}
        </button>
        {exportData.isError && (
          <div className="error-message" style={{ marginTop: '1rem' }}>
            Export failed. Please try again.
          </div>
        )}
      </div>
    </div>
  )
}

export default Exports
