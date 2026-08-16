import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { api, type UserProfile } from '../services/api'
import LiveExplorer from '../components/LiveExplorer'
import {
  Users, Clock, CalendarDays, Wallet, Package, CreditCard,
  Bot, LogOut, Building2, ShieldCheck, ArrowRight, Bell
} from 'lucide-react'

export default function DashboardPage() {
  const [user, setUser] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    async function loadUserSession() {
      try {
        await api.autoLogin()
        const me = await api.getMe()
        setUser(me)
      } catch {
        // If unauthenticated, redirect to login
        navigate('/login')
      } finally {
        setLoading(false)
      }
    }
    loadUserSession()
  }, [navigate])

  const handleLogout = () => {
    api.clearToken()
    navigate('/login')
  }

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#F7F6F3',
        fontSize: 14,
        color: '#767676',
      }}>
        Loading enterprise session...
      </div>
    )
  }

  return (
    <div style={{ minHeight: '100vh', background: '#F7F6F3' }}>
      {/* Dashboard App Top Bar */}
      <header style={{
        height: 72,
        background: '#fff',
        borderBottom: '1px solid #E6E6E6',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 32px',
        position: 'sticky',
        top: 0,
        zIndex: 100,
      }}>
        {/* Brand */}
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 8, textDecoration: 'none', color: '#000' }}>
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <rect width="28" height="28" fill="black" />
            <text x="6" y="20" fill="white" fontSize="16" fontWeight="700" fontFamily="Inter">N</text>
          </svg>
          <span style={{ fontSize: 18, fontWeight: 700, letterSpacing: '-0.02em' }}>NexusERP</span>
          <span style={{
            fontSize: 11,
            fontWeight: 600,
            background: '#F7F6F3',
            border: '1px solid #E6E6E6',
            padding: '2px 8px',
            marginLeft: 8,
          }}>
            WORKSPACE
          </span>
        </Link>

        {/* Quick App Navigation */}
        <nav style={{ display: 'flex', gap: 8 }}>
          <Link to="/dashboard" style={{ padding: '8px 16px', fontSize: 14, fontWeight: 600, color: '#000', textDecoration: 'none' }}>Dashboard</Link>
          <Link to="/ai" style={{ padding: '8px 16px', fontSize: 14, fontWeight: 500, color: '#555', textDecoration: 'none' }}>AI Assistant</Link>
          <Link to="/" style={{ padding: '8px 16px', fontSize: 14, fontWeight: 500, color: '#555', textDecoration: 'none' }}>Public Site</Link>
        </nav>

        {/* User Session & Logout */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          {user && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, fontSize: 13 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#333', fontWeight: 500 }}>
                <Building2 size={16} color="#000" />
                {user.company_name || 'Test Company'}
              </div>
              <span style={{ color: '#ccc' }}>|</span>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#333', fontWeight: 500 }}>
                <ShieldCheck size={16} color="#28C840" />
                {user.email}
              </div>
            </div>
          )}

          <button
            onClick={handleLogout}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              padding: '8px 16px',
              background: 'none',
              border: '1px solid #E6E6E6',
              fontSize: 13,
              fontWeight: 500,
              cursor: 'pointer',
              color: '#000',
              fontFamily: 'var(--font-body)',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.background = '#F7F6F3')}
            onMouseLeave={(e) => (e.currentTarget.style.background = 'none')}
          >
            <LogOut size={14} /> Log Out
          </button>
        </div>
      </header>

      {/* Main Dashboard Workspace Content */}
      <main style={{ padding: '40px 0' }}>
        <div className="container">
          {/* Welcome Header */}
          <div style={{ marginBottom: 32 }}>
            <h1 className="heading-lg" style={{ fontSize: 32, marginBottom: 8 }}>
              Welcome back, {user?.first_name || user?.username || 'Admin'}
            </h1>
            <p className="body-md">Here is your live enterprise summary and active operations.</p>
          </div>

          {/* Module Action Cards Grid */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: 16,
            marginBottom: 40,
          }}>
            {[
              { label: 'Employees Directory', desc: '105 Personnel', icon: Users, link: '/dashboard' },
              { label: 'Attendance Tracker', desc: '94.2% Attendance', icon: Clock, link: '/dashboard' },
              { label: 'Leave Requests', desc: '3 Active Requests', icon: CalendarDays, link: '/dashboard' },
              { label: 'Payroll Payslips', desc: '₹85,000 Disbursement', icon: Wallet, link: '/dashboard' },
              { label: 'Inventory Assets', desc: '2 Tracked Assets', icon: Package, link: '/dashboard' },
              { label: 'Payments Hub', desc: '2 Disbursements', icon: CreditCard, link: '/dashboard' },
              { label: 'System Alerts', desc: '4 Unread Alerts', icon: Bell, link: '/dashboard' },
              { label: 'AI Copilot', desc: '20 Enterprise Tools', icon: Bot, link: '/ai' },
            ].map((mod) => (
              <div key={mod.label} style={{
                background: '#fff',
                border: '1px solid #E6E6E6',
                padding: 20,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                  <div style={{
                    width: 36, height: 36, background: '#F7F6F3',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                  }}>
                    <mod.icon size={18} color="#000" />
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: 15, fontWeight: 600, color: '#000', marginBottom: 4 }}>{mod.label}</div>
                  <div style={{ fontSize: 12, color: '#767676' }}>{mod.desc}</div>
                </div>
              </div>
            ))}
          </div>

          {/* Interactive Live Data Explorer Table Section */}
          <LiveExplorer />
        </div>
      </main>
    </div>
  )
}
