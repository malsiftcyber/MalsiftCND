import React, { useEffect, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../services/api'
import { RefreshCw, Settings } from 'lucide-react'
import './Integrations.css'
import './shared.css'

type IntegrationSummary = {
  key: string
  name: string
  description?: string
  integration_type?: string
  enabled: boolean
  configured?: boolean
  connected: boolean
  last_sync?: string | null
  error?: string | null
}

type IntegrationField = {
  key: string
  label: string
  type: string
  required?: boolean
  placeholder?: string
  help_text?: string
}

type IntegrationDetails = {
  key: string
  name: string
  description?: string
  integration_type?: string
  enabled: boolean
  configured?: boolean
  connected: boolean
  fields: IntegrationField[]
  config: Record<string, string>
}

const Integrations: React.FC = () => {
  const queryClient = useQueryClient()
  const [showSyncModal, setShowSyncModal] = useState<string | null>(null)
  const [selectedIntegrationKey, setSelectedIntegrationKey] = useState<string | null>(null)
  const [formValues, setFormValues] = useState<Record<string, string>>({})
  const [modalEnabled, setModalEnabled] = useState<boolean>(true)

  const maskValue = '********'

  const { data: integrations = [], isLoading, error } = useQuery<IntegrationSummary[]>({
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

  const { data: integrationDetails, isLoading: detailsLoading } = useQuery<IntegrationDetails>({
    queryKey: ['integration-details', selectedIntegrationKey],
    queryFn: async () => {
      const res = await api.get(`/integrations/${selectedIntegrationKey}`)
      return res.data
    },
    enabled: !!selectedIntegrationKey,
    staleTime: 0,
  })

  useEffect(() => {
    if (integrationDetails) {
      const initialForm: Record<string, string> = {}
      integrationDetails.fields.forEach((field) => {
        const value = integrationDetails.config?.[field.key] ?? ''
        initialForm[field.key] = value
      })
      setFormValues(initialForm)
      setModalEnabled(integrationDetails.enabled)
    } else if (!selectedIntegrationKey) {
      setFormValues({})
      setModalEnabled(true)
    }
  }, [integrationDetails, selectedIntegrationKey])

  const syncIntegration = useMutation({
    mutationFn: async ({ key, force }: { key: string; force: boolean }) => {
      const res = await api.post(`/integrations/${key}/sync`, { force_full_sync: force, integration_name: key })
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

  const updateIntegrationConfig = useMutation({
    mutationFn: async ({ key, enabled, config }: { key: string; enabled: boolean; config: Record<string, string> }) => {
      const res = await api.put(`/integrations/${key}/config`, {
        enabled,
        config,
      })
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] })
      queryClient.invalidateQueries({ queryKey: ['integration-details', selectedIntegrationKey] })
      setSelectedIntegrationKey(null)
    },
    onError: (error: any) => {
      console.error('Failed to update integration config:', error)
      alert(`Failed to update integration: ${error.response?.data?.detail || error.message}`)
    },
  })

  const handleConfigChange = (fieldKey: string, value: string) => {
    setFormValues((prev) => ({ ...prev, [fieldKey]: value }))
  }

  const handleConfigSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedIntegrationKey) return

    // Ensure we do not send mask placeholder back to the API unnecessarily
    const cleanedConfig: Record<string, string> = {}
    Object.entries(formValues).forEach(([key, value]) => {
      cleanedConfig[key] = value
    })

    updateIntegrationConfig.mutate({ key: selectedIntegrationKey, enabled: modalEnabled, config: cleanedConfig })
  }

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
        <p className="page-subtitle">Configure external data sources and directory services.</p>
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
          {integrations.map((integration) => (
            <div key={integration.key} className="integration-card">
              <div className="integration-header">
                <div>
                  <h3>{integration.name}</h3>
                  {integration.description && <p className="integration-description">{integration.description}</p>}
                </div>
                <div className="integration-statuses">
                  <span className={`status-badge ${integration.connected ? 'status-online' : 'status-offline'}`}>
                    {integration.connected ? 'Connected' : 'Not Connected'}
                  </span>
                  <span className={`status-pill ${integration.configured ? 'pill-configured' : 'pill-missing'}`}>
                    {integration.configured ? 'Configured' : 'Missing Configuration'}
                  </span>
                  <span className={`status-pill ${integration.enabled ? 'pill-enabled' : 'pill-disabled'}`}>
                    {integration.enabled ? 'Enabled' : 'Disabled'}
                  </span>
                </div>
              </div>

              <div className="integration-info">
                <div className="info-row">
                  <span className="info-label">Type</span>
                  <span>{integration.integration_type || 'N/A'}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Last Sync</span>
                  <span>{integration.last_sync ? new Date(integration.last_sync).toLocaleString() : 'Never'}</span>
                </div>
                {integration.error && (
                  <div className="info-row warning">
                    <span className="info-label">Error</span>
                    <span>{integration.error}</span>
                  </div>
                )}
              </div>

              <div className="integration-actions">
                <button
                  className="btn-secondary"
                  onClick={() => setSelectedIntegrationKey(integration.key)}
                  disabled={detailsLoading && selectedIntegrationKey === integration.key}
                >
                  <Settings size={16} /> Configure
                </button>
                <button
                  className="btn-primary"
                  onClick={() => setShowSyncModal(integration.key)}
                  disabled={syncIntegration.isPending || !integration.configured}
                  title={!integration.configured ? 'Configure before syncing' : undefined}
                >
                  <RefreshCw size={16} />
                  {syncIntegration.isPending && showSyncModal === integration.key ? 'Syncing...' : 'Sync Now'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showSyncModal && (
        <div className="modal-overlay" onClick={() => setShowSyncModal(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Sync Integration</h2>
            <p>Choose sync type for <strong>{showSyncModal}</strong>.</p>
            <div className="modal-actions">
              <button
                onClick={() => syncIntegration.mutate({ key: showSyncModal, force: false })}
                className="btn-primary"
                disabled={syncIntegration.isPending}
              >
                Incremental Sync
              </button>
              <button
                onClick={() => syncIntegration.mutate({ key: showSyncModal, force: true })}
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

      {selectedIntegrationKey && integrationDetails && (
        <div className="modal-overlay" onClick={() => setSelectedIntegrationKey(null)}>
          <div className="modal-content wide" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Configure {integrationDetails.name}</h2>
              {integrationDetails.description && <p>{integrationDetails.description}</p>}
            </div>

            <form onSubmit={handleConfigSubmit} className="integration-form">
              <div className="toggle-row">
                <label htmlFor="integration-enabled">
                  <input
                    id="integration-enabled"
                    type="checkbox"
                    checked={modalEnabled}
                    onChange={(e) => setModalEnabled(e.target.checked)}
                  />
                  Enable integration
                </label>
                {!integrationDetails.configured && (
                  <span className="warning-text">Required fields must be populated before enabling.</span>
                )}
              </div>

              <div className="fields-grid">
                {integrationDetails.fields.map((field) => (
                  <div key={field.key} className="form-group">
                    <label htmlFor={`field-${field.key}`}>
                      {field.label}
                      {field.required && <span className="required">*</span>}
                    </label>
                    <input
                      id={`field-${field.key}`}
                      type={field.type === 'password' ? 'password' : 'text'}
                      value={formValues[field.key] ?? ''}
                      placeholder={field.placeholder || ''}
                      onChange={(e) => handleConfigChange(field.key, e.target.value)}
                      required={field.required}
                    />
                    {field.help_text && <small>{field.help_text}</small>}
                    {field.type === 'password' && integrationDetails.config?.[field.key] === maskValue && (
                      <small>Leave as {maskValue} to keep the existing secret.</small>
                    )}
                  </div>
                ))}
              </div>

              <div className="modal-actions">
                <button type="button" onClick={() => setSelectedIntegrationKey(null)} disabled={updateIntegrationConfig.isPending}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary" disabled={updateIntegrationConfig.isPending}>
                  {updateIntegrationConfig.isPending ? 'Saving...' : 'Save Configuration'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Integrations
