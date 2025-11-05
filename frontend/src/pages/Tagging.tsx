import React from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '../services/api'
import './Tagging.css'
import './shared.css'

const Tagging: React.FC = () => {
  const { data: companies = [], isLoading: companiesLoading, error: companiesError } = useQuery({
    queryKey: ['companies'],
    queryFn: async () => {
      try {
        const res = await api.get('/tagging/companies')
        return res.data || []
      } catch (error: any) {
        console.error('Failed to load companies:', error)
        return []
      }
    },
    retry: 1,
  })

  const { data: sites = [], isLoading: sitesLoading, error: sitesError } = useQuery({
    queryKey: ['sites'],
    queryFn: async () => {
      try {
        const res = await api.get('/tagging/sites')
        return res.data || []
      } catch (error: any) {
        console.error('Failed to load sites:', error)
        return []
      }
    },
    retry: 1,
  })

  const isLoading = companiesLoading || sitesLoading

  if (isLoading) {
    return (
      <div className="tagging-page">
        <div className="page-header">
          <h1>Company & Site Tagging</h1>
        </div>
        <div className="loading">Loading...</div>
      </div>
    )
  }

  return (
    <div className="tagging-page">
      <div className="page-header">
        <h1>Company & Site Tagging</h1>
      </div>

      {(companiesError || sitesError) && (
        <div className="error-message">
          {companiesError && <div>Failed to load companies: {companiesError instanceof Error ? companiesError.message : 'Unknown error'}</div>}
          {sitesError && <div>Failed to load sites: {sitesError instanceof Error ? sitesError.message : 'Unknown error'}</div>}
        </div>
      )}

      <div className="tagging-grid">
        <div className="tagging-section">
          <h2>Companies</h2>
          {companies.length === 0 ? (
            <div className="empty-state">No companies configured.</div>
          ) : (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Company Name</th>
                    <th>Description</th>
                    <th>Created</th>
                  </tr>
                </thead>
                <tbody>
                  {companies.map((company: any) => (
                    <tr key={company.id}>
                      <td>{company.name || 'Unnamed'}</td>
                      <td>{company.description || 'N/A'}</td>
                      <td>{company.created_at ? new Date(company.created_at).toLocaleDateString() : 'N/A'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="tagging-section">
          <h2>Sites</h2>
          {sites.length === 0 ? (
            <div className="empty-state">No sites configured.</div>
          ) : (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Site Name</th>
                    <th>Company</th>
                    <th>Description</th>
                    <th>Created</th>
                  </tr>
                </thead>
                <tbody>
                  {sites.map((site: any) => (
                    <tr key={site.id}>
                      <td>{site.name || 'Unnamed'}</td>
                      <td>{site.company_name || 'N/A'}</td>
                      <td>{site.description || 'N/A'}</td>
                      <td>{site.created_at ? new Date(site.created_at).toLocaleDateString() : 'N/A'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Tagging
