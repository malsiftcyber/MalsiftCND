import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../services/api'
import { Plus, Trash2, RefreshCw } from 'lucide-react'
import './EDR.css'
import './shared.css'

const EDR: React.FC = () => {
  const queryClient = useQueryClient()
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [formData, setFormData] = useState({
    provider: 'crowdstrike',
    name: '',
    api_key: '',
    api_secret: '',
    base_url: '',
  })

  const { data: integrations = [], isLoading, error } = useQuery({
    queryKey: ['edr-integrations'],
    queryFn: async () => {
      try {
        const res = await api.get('/edr/integrations')
        return res.data || []
      } catch (error: any) {
        console.error('Failed to load EDR integrations:', error)
        return []
      }
    },
    retry: 1,
  })

  const createIntegration = useMutation({
    mutationFn: async (data: any) => {
      const res = await api.post('/edr/integrations', data)
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['edr-integrations'] })
      setShowCreateModal(false)
      setFormData({ provider: 'crowdstrike', name: '', api_key: '', api_secret: '', base_url: '' })
    },
    onError: (error: any) => {
      console.error('Failed to create EDR integration:', error)
      alert(`Failed to create integration: ${error.response?.data?.detail || error.message}`)
    },
  })

  const deleteIntegration = useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/edr/integrations/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['edr-integrations'] })
    },
    onError: (error: any) => {
      console.error('Failed to delete integration:', error)
      alert(`Failed to delete integration: ${error.response?.data?.detail || error.message}`)
    },
  })

  const syncIntegration = useMutation({
    mutationFn: async (id: string) => {
      const res = await api.post(`/edr/integrations/${id}/sync`)
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['edr-integrations'] })
    },
    onError: (error: any) => {
      console.error('Failed to sync integration:', error)
      alert(`Failed to sync integration: ${error.response?.data?.detail || error.message}`)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createIntegration.mutate(formData)
  }

  if (isLoading) {
    return (
      <div className="edr-page">
        <div className="page-header">
          <h1>EDR Integrations</h1>
        </div>
        <div className="loading">Loading...</div>
      </div>
    )
  }

  return (
    <div className="edr-page">
      <div className="page-header">
        <h1>EDR Integrations</h1>
        <button className="btn-primary" onClick={() => setShowCreateModal(true)}>
          <Plus size={20} />
          Add Integration
        </button>
      </div>

      {error && (
        <div className="error-message">
          Failed to load EDR integrations: {error instanceof Error ? error.message : 'Unknown error'}
        </div>
      )}

      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Create EDR Integration</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Provider</label>
                <select
                  value={formData.provider}
                  onChange={(e) => setFormData({ ...formData, provider: e.target.value })}
                >
                  <option value="crowdstrike">CrowdStrike Falcon</option>
                  <option value="microsoft_defender">Microsoft Defender</option>
                  <option value="sentinelone">SentinelOne</option>
                  <option value="trendmicro">TrendMicro Vision One</option>
                </select>
              </div>
              <div className="form-group">
                <label>Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>API Key</label>
                <input
                  type="password"
                  value={formData.api_key}
                  onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>API Secret</label>
                <input
                  type="password"
                  value={formData.api_secret}
                  onChange={(e) => setFormData({ ...formData, api_secret: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Base URL</label>
                <input
                  type="text"
                  value={formData.base_url}
                  onChange={(e) => setFormData({ ...formData, base_url: e.target.value })}
                  placeholder="https://api.example.com"
                />
              </div>
              <div className="modal-actions">
                <button type="button" onClick={() => setShowCreateModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary" disabled={createIntegration.isPending}>
                  {createIntegration.isPending ? 'Creating...' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {integrations.length === 0 ? (
        <div className="empty-state">No EDR integrations configured. Add an integration to get started.</div>
      ) : (
        <div className="integrations-grid">
          {integrations.map((integration: any) => (
            <div key={integration.id} className="integration-card">
              <div className="integration-header">
                <h3>{integration.name || 'Unnamed'}</h3>
                <span className={`status-badge status-${integration.status || 'unknown'}`}>
                  {integration.status || 'unknown'}
                </span>
              </div>
              <div className="integration-info">
                <div className="info-row">
                  <span className="info-label">Provider:</span>
                  <span>{integration.provider || 'N/A'}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Last Sync:</span>
                  <span>{integration.last_sync ? new Date(integration.last_sync).toLocaleString() : 'Never'}</span>
                </div>
              </div>
              <div className="integration-actions">
                <button
                  className="btn-primary"
                  onClick={() => syncIntegration.mutate(integration.id)}
                  disabled={syncIntegration.isPending}
                >
                  <RefreshCw size={16} />
                  {syncIntegration.isPending ? 'Syncing...' : 'Sync'}
                </button>
                <button
                  className="btn-danger"
                  onClick={() => deleteIntegration.mutate(integration.id)}
                  disabled={deleteIntegration.isPending}
                >
                  <Trash2 size={16} />
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default EDR
