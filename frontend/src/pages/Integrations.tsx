import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../services/api'
import { Plus, RefreshCw } from 'lucide-react'
import './Integrations.css'
import './shared.css'

const Integrations: React.FC = () => {
  const queryClient = useQueryClient()
  const [showSyncModal, setShowSyncModal] = useState<string | null>(null)

  const { data: integrations = [], isLoading, error } = useQuery({
    queryKey: ['integrations'],
    queryFn: async () => {
      try {
        const res = await api.get('/integrations/')
        return res.data || []
      } catch (error: any) {
        console.error('Failed to load integrations:', error)
        return []
      }
    },
    retry: 1,
  })

  const syncIntegration = useMutation({
    mutationFn: async ({ name, force }: { name: string; force: boolean }) => {
      const res = await api.post(`/integrations/${name}/sync`, { force_full_sync: force })
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] })
      setShowSyncModal(null)
    },
    onError: (error: any) => {
      console.error('Failed to sync integration:', error)
      alert(`Failed to sync integration: ${error.response?.data?.detail || error.message}`)
    },
  })

  if (isLoading) {
    return (
      <div className="integrations-page">
        <div className="page-header">
          <h1>Integrations</h1>
        </div>
        <div className="loading">Loading...</div>
      </div>
    )
  }

  return (
    <div className="integrations-page">
      <div className="page-header">
        <h1>Integrations</h1>
      </div>

      {error && (
        <div className="error-message">
          Failed to load integrations: {error instanceof Error ? error.message : 'Unknown error'}
        </div>
      )}

      {integrations.length === 0 ? (
        <div className="empty-state">No integrations configured. Add an integration to get started.</div>
      ) : (
        <div className="integrations-grid">
          {integrations.map((integration: any) => (
            <div key={integration.name} className="integration-card">
              <div className="integration-header">
                <h3>{integration.name || 'Unnamed'}</h3>
                <span className={`status-badge status-${integration.status || 'unknown'}`}>
                  {integration.status || 'unknown'}
                </span>
              </div>
              <div className="integration-info">
                <div className="info-row">
                  <span className="info-label">Type:</span>
                  <span>{integration.integration_type || 'N/A'}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Last Sync:</span>
                  <span>{integration.last_sync ? new Date(integration.last_sync).toLocaleString() : 'Never'}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Devices Synced:</span>
                  <span>{integration.devices_synced || 0}</span>
                </div>
              </div>
              <div className="integration-actions">
                <button
                  className="btn-primary"
                  onClick={() => setShowSyncModal(integration.name)}
                  disabled={syncIntegration.isPending}
                >
                  <RefreshCw size={16} />
                  {syncIntegration.isPending ? 'Syncing...' : 'Sync Now'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showSyncModal && (
        <div className="modal-overlay" onClick={() => setShowSyncModal(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Sync Integration: {showSyncModal}</h2>
            <p>Choose sync type:</p>
            <div className="modal-actions">
              <button
                onClick={() => {
                  syncIntegration.mutate({ name: showSyncModal, force: false })
                }}
                className="btn-primary"
                disabled={syncIntegration.isPending}
              >
                Incremental Sync
              </button>
              <button
                onClick={() => {
                  syncIntegration.mutate({ name: showSyncModal, force: true })
                }}
                className="btn-primary"
                disabled={syncIntegration.isPending}
              >
                Full Sync
              </button>
              <button onClick={() => setShowSyncModal(null)} disabled={syncIntegration.isPending}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Integrations
