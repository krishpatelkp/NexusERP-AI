import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import {
  LayoutDashboard, Users, Clock, CalendarDays, Wallet, Package, CreditCard,
  BarChart3, Bot, Settings, LogOut, Bell
} from 'lucide-react'

const getPageTitle = (pathname: string, isAdmin: boolean): string => {
  switch (pathname) {
    case '/dashboard':
      return isAdmin ? 'Enterprise Dashboard' : 'My Dashboard'
    case '/employees':
      return 'Employees Directory'
    case '/attendance':
      return isAdmin ? 'Attendance Tracker' : 'My Attendance'
    case '/leave':
      return isAdmin ? 'Leave Management' : 'My Leave'
    case '/payroll':
      return isAdmin ? 'Payroll Management' : 'My Payslips'
    case '/inventory':
      return isAdmin ? 'Inventory & Assets' : 'My Assets'
    case '/payments':
      return 'Payments Hub'
    case '/reports':
      return 'Reports & Analytics'
    case '/settings':
      return 'Company Settings'
    case '/ai':
      return 'AI Copilot'
    default:
      return 'Dashboard'
  }
}

export const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, isAdmin, logout } = useAuth()
  const location = useLocation()

  const adminNav = [
    { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { label: 'Employees', path: '/employees', icon: Users },
    { label: 'Attendance', path: '/attendance', icon: Clock },
    { label: 'Leave Management', path: '/leave', icon: CalendarDays },
    { label: 'Payroll', path: '/payroll', icon: Wallet },
    { label: 'Inventory', path: '/inventory', icon: Package },
    { label: 'Payments', path: '/payments', icon: CreditCard },
    { label: 'Reports', path: '/reports', icon: BarChart3 },
    { label: 'AI Copilot', path: '/ai', icon: Bot },
    { label: 'Settings', path: '/settings', icon: Settings },
  ]

  const employeeNav = [
    { label: 'My Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { label: 'My Attendance', path: '/attendance', icon: Clock },
    { label: 'My Leave', path: '/leave', icon: CalendarDays },
    { label: 'My Payslips', path: '/payroll', icon: Wallet },
    { label: 'My Assets', path: '/inventory', icon: Package },
    { label: 'AI Assistant', path: '/ai', icon: Bot },
  ]

  const navItems = isAdmin ? adminNav : employeeNav
  const title = getPageTitle(location.pathname, isAdmin)

  const getInitials = (name?: string, email?: string): string => {
    if (name && name.trim()) {
      const parts = name.trim().split(' ')
      return parts.length > 1 ? `${parts[0][0]}${parts[1][0]}`.toUpperCase() : parts[0][0].toUpperCase()
    }
    return (email || 'U')[0].toUpperCase()
  }

  const initials = getInitials(user?.first_name ? `${user.first_name} ${user.last_name || ''}` : undefined, user?.email)

  return (
    <div style={{ minHeight: '100vh', display: 'flex', background: '#F7F6F3' }}>
      {/* 240px Sidebar */}
      <aside style={{
        width: 240,
        background: '#ffffff',
        borderRight: '1px solid #E6E6E6',
        display: 'flex',
        flexDirection: 'column',
        position: 'fixed',
        top: 0, bottom: 0, left: 0,
        zIndex: 90,
      }}>
        {/* Top Section */}
        <div style={{
          padding: '20px 20px',
          borderBottom: '1px solid #E6E6E6',
          display: 'flex',
          flexDirection: 'column',
          gap: 12,
        }}>
          {/* Logo & Company Name */}
          <Link to="/dashboard" style={{ display: 'flex', alignItems: 'center', gap: 10, textDecoration: 'none', color: 'inherit', cursor: 'pointer' }}>
            <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
              <rect width="28" height="28" fill="black" />
              <text x="6" y="20" fill="white" fontSize="16" fontWeight="700" fontFamily="Inter">N</text>
            </svg>
            <span style={{ fontSize: 16, fontWeight: 700, letterSpacing: '-0.02em', color: '#000' }}>NexusERP</span>
          </Link>

          <div>
            <div style={{ fontSize: 13, fontWeight: 600, color: '#000', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {user?.company_name || 'Acme Corp'}
            </div>
            <div style={{ marginTop: 4 }}>
              <span style={{
                fontSize: 10,
                fontWeight: 700,
                padding: '2px 6px',
                background: isAdmin ? '#000' : '#E6E6E6',
                color: isAdmin ? '#fff' : '#000',
                borderRadius: 2,
                letterSpacing: '0.05em',
                textTransform: 'uppercase',
              }}>
                {user?.role_name || (isAdmin ? 'Admin' : 'Employee')}
              </span>
            </div>
          </div>
        </div>

        {/* Navigation Items */}
        <nav style={{ flex: 1, padding: '16px 12px', display: 'flex', flexDirection: 'column', gap: 4, overflowY: 'auto' }}>
          {navItems.map((item) => {
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                  padding: '10px 14px',
                  fontSize: 13,
                  fontWeight: isActive ? 600 : 500,
                  color: isActive ? '#ffffff' : '#333333',
                  background: isActive ? '#000000' : 'transparent',
                  borderRadius: 4,
                  textDecoration: 'none',
                  transition: 'all 0.15s ease',
                }}
              >
                <item.icon size={16} color={isActive ? '#ffffff' : '#767676'} />
                {item.label}
              </Link>
            )
          })}
        </nav>

        {/* Bottom Section */}
        <div style={{ padding: 16, borderTop: '1px solid #E6E6E6', background: '#fafafa' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
            <div style={{
              width: 34, height: 34, background: '#000000', color: '#ffffff',
              display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: 13,
              borderRadius: 4, flexShrink: 0,
            }}>
              {initials}
            </div>
            <div style={{ flex: 1, overflow: 'hidden' }}>
              <div style={{ fontSize: 13, fontWeight: 600, color: '#000', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {user?.first_name ? `${user.first_name} ${user.last_name || ''}` : user?.username || 'User'}
              </div>
              <div style={{ fontSize: 11, color: '#767676', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {user?.email}
              </div>
            </div>
          </div>

          <button
            onClick={logout}
            style={{
              width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
              padding: '8px 12px', background: '#ffffff', border: '1px solid #E6E6E6', fontSize: 12,
              fontWeight: 600, cursor: 'pointer', color: '#000000', fontFamily: 'var(--font-body)',
              borderRadius: 4, transition: 'background 0.2s',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.background = '#F7F6F3')}
            onMouseLeave={(e) => (e.currentTarget.style.background = '#ffffff')}
          >
            <LogOut size={14} /> Log Out
          </button>
        </div>
      </aside>

      {/* Main Container */}
      <div style={{ flex: 1, marginLeft: 240, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        {/* Top Bar (72px tall) */}
        <header style={{
          height: 72, background: '#ffffff', borderBottom: '1px solid #E6E6E6',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '0 32px', position: 'sticky', top: 0, zIndex: 80,
        }}>
          <h2 style={{ fontSize: 20, fontWeight: 700, letterSpacing: '-0.02em', color: '#000000', margin: 0 }}>
            {title}
          </h2>

          <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
            {/* Notification Bell */}
            <div style={{ position: 'relative', cursor: 'pointer' }}>
              <Bell size={18} color="#000000" />
              <span style={{
                position: 'absolute', top: -2, right: -2, width: 8, height: 8,
                background: '#FF3B30', borderRadius: '50%', border: '2px solid #ffffff',
              }} />
            </div>

            <span style={{ color: '#E6E6E6' }}>|</span>

            {/* User Name Display */}
            <div style={{ fontSize: 13, fontWeight: 600, color: '#000000' }}>
              {user?.first_name ? `${user.first_name} ${user.last_name || ''}` : user?.email}
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <main style={{ padding: 32, flex: 1, background: '#F7F6F3', overflowY: 'auto' }}>
          {children}
        </main>
      </div>
    </div>
  )
}
