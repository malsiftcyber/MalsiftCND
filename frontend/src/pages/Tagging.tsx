import React from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '../services/api'
import './Tagging.css'

const Tagging: React.FC = () => {
  const { data: companies = [] } = useQuery({
    queryKey: ['companies'],
    queryFn: async () => {
      const res = await api.get('/tagging/companies')
      return res.data || []
    },
  })

  const { data: sites = [] } = useQuery({
    queryKey: ['sites'],
    queryFn: async () => {
      const res = await api.get('/tagging/sites')
      return res.data || []
    },
  })

  return (
    <div className="tagging-page">
      <div className="page-header">
        <h1>Company & Site Tagging</h1>
      </div>

      <div className="tagging-grid">
        <div className="tagging-section">
          <h2>Companies</h2>
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
                    <td>{company.name}</td>
                    <td>{company.description || 'N/A'}</td>
                    <td>{company.created_at ? new Date(company.created_at).toLocaleDateString() : 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="tagging-section">
          <h2>Sites</h2>
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
                    <td>{site.name}</td>
                    <td>{site.company_name || 'N/A'}</td>
                    <td>{site.description || 'N/A'}</td>
                    <td>{site.created_at ? new Date(site.created_at).toLocaleDateString() : 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Tagging
