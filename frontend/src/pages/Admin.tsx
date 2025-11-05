import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../services/api'
import { Save } from 'lucide-react'
import './Admin.css'
import './shared.css'

const Admin: React.FC = () => {
  const queryClient = useQueryClient()
  const [config, setConfig] = useState({
    scan_timeout: 300,
    max_concurrent_scans: 10,
    scan_throttle_rate: 100,
    ai_analysis_enabled: true,
    auto_sync_enabled: true,
    sync_interval: 3600,
  })

  const { data: systemConfig, isLoading: configLoading, error: configError } = useQuery({
    queryKey: ['system-config'],
    queryFn: async () => {
      try {
        const res = await api.get('/admin/system/config')
        return res.data
      } catch (error: any) {
        console.error('Failed to load system config:', error)
        throw error
      }
    },
    onSuccess: (data) => {
      if (data) setConfig(data)
    },
    retry: 1,
  })

  const { data: scanners = [], isLoading: scannersLoading, error: scannersError } = useQuery({
    queryKey: ['scanners'],
    queryFn: async () => {
      try {
        const res = await api.get('/admin/scanners')
        return res.data || []
      } catch (error: any) {
        console.error('Failed to load scanners:', error)
        // Return empty array instead of throwing to allow page to render
        return []
      }
    },
    retry: 1,
  })

  const updateSystemConfig = useMutation({
    mutationFn: async (data: any) => {
      const res = await api.put('/admin/system/config', data)
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['system-config'] })
      alert('Configuration saved successfully')
    },
    onError: (error: any) => {
      console.error('Failed to save config:', error)
      alert(`Failed to save configuration: ${error.response?.data?.detail || error.message}`)
    },
  })

  const updateScanner = useMutation({
    mutationFn: async ({ name, enabled }: { name: string; enabled: boolean }) => {
      const res = await api.put(`/admin/scanners/${name}`, { enabled })
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scanners'] })
    },
    onError: (error: any) => {
      console.error('Failed to update scanner:', error)
      alert(`Failed to update scanner: ${error.response?.data?.detail || error.message}`)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    updateSystemConfig.mutate(config)
  }

  if (configLoading || scannersLoading) {
    return (
      <div className="admin-page">
        <div className="page-header">
          <h1>Admin Panel</h1>
        </div>
        <div className="loading">Loading...</div>
      </div>
    )
  }

  return (
    <div className="admin-page">
      <div className="page-header">
        <h1>Admin Panel</h1>
      </div>

      {configError && (
        <div className="error-message">
          Failed to load system configuration: {configError instanceof Error ? configError.message : 'Unknown error'}
        </div>
      )}

      {scannersError && (
        <div className="error-message">
          Failed to load scanner configuration: {scannersError instanceof Error ? scannersError.message : 'Unknown error'}
        </div>
      )}

      <div className="admin-sections">
        <div className="admin-section">
          <h2>System Configuration</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Scan Timeout (seconds)</label>
              <input
                type="number"
                value={config.scan_timeout}
                onChange={(e) => setConfig({ ...config, scan_timeout: parseInt(e.target.value) })}
                min="60"
                max="3600"
              />
            </div>
            <div className="form-group">
              <label>Max Concurrent Scans</label>
              <input
                type="number"
                value={config.max_concurrent_scans}
                onChange={(e) => setConfig({ ...config, max_concurrent_scans: parseInt(e.target.value) })}
                min="1"
                max="100"
              />
            </div>
            <div className="form-group">
              <label>Scan Throttle Rate (requests/second)</label>
              <input
                type="number"
                value={config.scan_throttle_rate}
                onChange={(e) => setConfig({ ...config, scan_throttle_rate: parseInt(e.target.value) })}
                min="1"
                max="10000"
              />
            </div>
            <div className="form-group">
              <label>
                <input
                  type="checkbox"
                  checked={config.ai_analysis_enabled}
                  onChange={(e) => setConfig({ ...config, ai_analysis_enabled: e.target.checked })}
                />
                AI Analysis Enabled
              </label>
            </div>
            <div className="form-group">
              <label>
                <input
                  type="checkbox"
                  checked={config.auto_sync_enabled}
                  onChange={(e) => setConfig({ ...config, auto_sync_enabled: e.target.checked })}
                />
                Auto Sync Enabled
              </label>
            </div>
            <div className="form-group">
              <label>Sync Interval (seconds)</label>
              <input
                type="number"
                value={config.sync_interval}
                onChange={(e) => setConfig({ ...config, sync_interval: parseInt(e.target.value) })}
                min="60"
                max="86400"
              />
            </div>
            <button type="submit" className="btn-primary" disabled={updateSystemConfig.isPending}>
              <Save size={20} />
              {updateSystemConfig.isPending ? 'Saving...' : 'Save Configuration'}
            </button>
          </form>
        </div>

        <div className="admin-section">
          <h2>Scanner Configuration</h2>
          {scanners.length === 0 ? (
            <div className="empty-state">No scanners configured</div>
          ) : (
            <div className="scanners-list">
              {scanners.map((scanner: any) => (
                <div key={scanner.scanner_name} className="scanner-item">
                  <div className="scanner-info">
                    <h3>{scanner.scanner_name}</h3>
                    <span className={`status-badge status-${scanner.enabled ? 'enabled' : 'disabled'}`}>
                      {scanner.enabled ? 'Enabled' : 'Disabled'}
                    </span>
                  </div>
                  <button
                    className="btn-primary"
                    onClick={() => updateScanner.mutate({ name: scanner.scanner_name, enabled: !scanner.enabled })}
                    disabled={updateScanner.isPending}
                  >
                    {scanner.enabled ? 'Disable' : 'Enable'}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Admin
