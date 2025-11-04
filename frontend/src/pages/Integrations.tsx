import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../services/api'
import { Plus, RefreshCw } from 'lucide-react'
import './Integrations.css'

const Integrations: React.FC = () => {
  const queryClient = useQueryClient()
  const [showSyncModal, setShowSyncModal] = useState<string | null>(null)

  const { data: integrations = [] } = useQuery({
    queryKey: ['integrations'],
    queryFn: async () => {
      const res = await api.get('/integrations/')
      return res.data
    },
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
  })

  return (
    <div className="integrations-page">
      <div className="page-header">
        <h1>Integrations</h1>
      </div>

      <div className="integrations-grid">
        {integrations.map((integration: any) => (
          <div key={integration.name} className="integration-card">
            <div className="integration-header">
              <h3>{integration.name}</h3>
              <span className={`status-badge status-${integration.status}`}>
                {integration.status}
              </span>
            </div>
            <div className="integration-info">
              <div className="info-row">
                <span className="info-label">Type:</span>
                <span>{integration.integration_type}</span>
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
              >
                <RefreshCw size={16} />
                Sync Now
              </button>
            </div>
          </div>
        ))}
      </div>

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
              >
                Incremental Sync
              </button>
              <button
                onClick={() => {
                  syncIntegration.mutate({ name: showSyncModal, force: true })
                }}
                className="btn-primary"
              >
                Full Sync
              </button>
              <button onClick={() => setShowSyncModal(null)}>
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
