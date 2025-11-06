import React, { useState } from 'react'
import { useNavigate, Link, Outlet } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { LogOut, Menu, X } from 'lucide-react'
import './Layout.css'

const Layout: React.FC = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const menuItems = [
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/scans', label: 'Scans', icon: '🔍' },
    { path: '/devices', label: 'Devices', icon: '🖥️' },
    { path: '/integrations', label: 'Integrations', icon: '🔗' },
    { path: '/edr', label: 'EDR', icon: '🛡️' },
    { path: '/scheduling', label: 'Scheduling', icon: '⏰' },
    { path: '/tagging', label: 'Tagging', icon: '🏷️' },
    { path: '/exports', label: 'Exports', icon: '📤' },
    { path: '/agents', label: 'Agents', icon: '🤖' },
    { path: '/agent-download', label: 'Download Agent', icon: '⬇️' },
    { path: '/accuracy', label: 'Accuracy', icon: '📈' },
  ]

  if (user?.is_admin) {
    menuItems.push({ path: '/admin', label: 'Admin', icon: '⚙️' })
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="layout">
      <nav className="navbar">
        <button className="menu-toggle" onClick={() => setSidebarOpen(!sidebarOpen)}>
          {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
        <div className="navbar-brand">MalsiftCND</div>
        <div className="navbar-user">
          <span>{user?.username}</span>
          <button onClick={handleLogout} className="btn-logout">
            <LogOut size={16} />
          </button>
        </div>
      </nav>

      <div className="layout-content">
        <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
          <nav className="sidebar-nav">
            {menuItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                className="nav-item"
              >
                <span className="nav-icon">{item.icon}</span>
                <span className="nav-label">{item.label}</span>
              </Link>
            ))}
          </nav>
        </aside>

        <main className="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default Layout

