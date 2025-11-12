import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '../services/api'
import { Download, Copy, Check } from 'lucide-react'
import './shared.css'
import './AgentDownload.css'

const AgentDownload: React.FC = () => {
  const [copied, setCopied] = useState<string | null>(null)
  const [selectedPlatform, setSelectedPlatform] = useState<string>('')
  const [selectedArch, setSelectedArch] = useState<string>('')

  const { data: platforms, isLoading: platformsLoading, error: platformsError } = useQuery({
    queryKey: ['agent-platforms'],
    queryFn: async () => {
      try {
        const res = await api.get('/agents/platforms')
        return res.data.platforms || []
      } catch (error: any) {
        console.error('Failed to load platforms:', error)
        return []
      }
    },
    retry: 1,
  })

  const { data: installer, isLoading: installerLoading } = useQuery({
    queryKey: ['agent-installer', selectedPlatform, selectedArch],
    queryFn: async () => {
      if (!selectedPlatform || !selectedArch) return null
      try {
        const res = await api.get(`/agents/installers/${selectedPlatform}/${selectedArch}`)
        return res.data
      } catch (error: any) {
        console.error('Failed to load installer:', error)
        return null
      }
    },
    enabled: !!selectedPlatform && !!selectedArch,
    retry: 1,
  })

  const getFileExtension = (platform: string): string => {
    if (platform === 'windows') return '.exe'
    if (platform === 'linux') return '.tar.gz'
    if (platform === 'macos') return '.tar.gz'
    return ''
  }

  const handleDownload = (platform: string, architecture: string) => {
    const fileExt = getFileExtension(platform)
    const downloadUrl = `https://github.com/malsiftcyber/MalsiftCND/releases/latest/download/malsift-agent-${platform}-${architecture}${fileExt}`
    
    // Open in new tab - GitHub will handle the download
    // Using window.location would navigate away, so we use window.open
    const newWindow = window.open(downloadUrl, '_blank', 'noopener,noreferrer')
    
    // If popup was blocked, fall back to creating a link
    if (!newWindow || newWindow.closed || typeof newWindow.closed === 'undefined') {
      // Popup blocked - create a temporary link instead
      const link = document.createElement('a')
      link.href = downloadUrl
      link.target = '_blank'
      link.rel = 'noopener noreferrer'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text)
    setCopied(id)
    setTimeout(() => setCopied(null), 2000)
  }

  const handleGetInstaller = (platform: string, architecture: string) => {
    setSelectedPlatform(platform)
    setSelectedArch(architecture)
  }

  if (platformsLoading) {
    return (
      <div className="agent-download-page">
        <div className="page-header">
          <h1>Download Agent</h1>
        </div>
        <div className="loading">Loading...</div>
      </div>
    )
  }

  return (
    <div className="agent-download-page">
      <div className="page-header">
        <h1>Download Agent</h1>
        <p>Download and install the MalsiftCND Discovery Agent on your systems</p>
      </div>

      {platformsError && (
        <div className="error-message">
          Failed to load platform information: {platformsError instanceof Error ? platformsError.message : 'Unknown error'}
        </div>
      )}

      {platforms && platforms.length > 0 ? (
        <div className="platforms-grid">
          {platforms.map((platform: any) => (
            <div key={platform.platform} className="platform-card">
              <div className="platform-header">
                <h2>{platform.name}</h2>
                <span className="platform-badge">{platform.service_type}</span>
              </div>
              
              <div className="architectures">
                <h3>Available Architectures:</h3>
                {platform.architectures.map((arch: string) => (
                  <div key={arch} className="architecture-item">
                    <div className="arch-info">
                      <span className="arch-name">{arch.toUpperCase()}</span>
                      <span className="arch-installer-types">
                        {platform.installer_types.join(', ')}
                      </span>
                    </div>
                    <div className="arch-actions">
                      <button
                        className="btn-download"
                        onClick={() => handleDownload(platform.platform, arch)}
                      >
                        <Download size={16} />
                        Download
                      </button>
                      <button
                        className="btn-installer"
                        onClick={() => handleGetInstaller(platform.platform, arch)}
                      >
                        Get Installer Script
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-state">No platforms available</div>
      )}

      {selectedPlatform && selectedArch && (
        <div className="installer-modal">
          <div className="installer-content">
            <h2>
              Installer Script for {platforms?.find((p: any) => p.platform === selectedPlatform)?.name} {selectedArch.toUpperCase()}
            </h2>
            
            {installerLoading ? (
              <div className="loading">Loading installer script...</div>
            ) : installer ? (
              <>
                <div className="installer-instructions">
                  <p>{installer.instructions}</p>
                  <div className="download-url">
                    <strong>Download URL:</strong>
                    <div className="url-box">
                      <code>{installer.download_url}</code>
                      <button
                        className="btn-copy"
                        onClick={() => handleCopy(installer.download_url, 'url')}
                      >
                        {copied === 'url' ? <Check size={16} /> : <Copy size={16} />}
                      </button>
                    </div>
                  </div>
                </div>
                
                <div className="installer-script">
                  <div className="script-header">
                    <strong>Installer Script:</strong>
                    <button
                      className="btn-copy"
                      onClick={() => handleCopy(installer.installer_script, 'script')}
                    >
                      {copied === 'script' ? <Check size={16} /> : <Copy size={16} />}
                      {copied === 'script' ? 'Copied!' : 'Copy Script'}
                    </button>
                  </div>
                  <pre className="script-content">
                    <code>{installer.installer_script}</code>
                  </pre>
                </div>
                
                <button
                  className="btn-close"
                  onClick={() => {
                    setSelectedPlatform('')
                    setSelectedArch('')
                  }}
                >
                  Close
                </button>
              </>
            ) : (
              <div className="error-message">Failed to load installer script</div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default AgentDownload

