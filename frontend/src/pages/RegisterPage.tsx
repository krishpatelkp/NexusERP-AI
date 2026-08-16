import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { api } from '../services/api'
import { ArrowRight, Lock, Mail, User, Phone, Building2, AlertCircle, CheckCircle2 } from 'lucide-react'
import { FadeIn } from '../components/animations'

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    phone_number: '',
    company_name: '',
    password: '',
    confirm_password: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const navigate = useNavigate()

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    if (formData.password !== formData.confirm_password) {
      setError('Passwords do not match')
      setLoading(false)
      return
    }

    try {
      await api.register({
        email: formData.email,
        username: formData.username,
        phone_number: formData.phone_number,
        password: formData.password,
        confirm_password: formData.confirm_password,
      })
      setSuccess(true)
      setTimeout(() => {
        navigate('/dashboard')
      }, 800)
    } catch (err: any) {
      setError(err.message || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: '#F7F6F3',
      padding: '40px 24px',
    }}>
      <FadeIn>
        <div style={{
          width: '100%',
          maxWidth: 480,
          background: '#fff',
          border: '1px solid #E6E6E6',
          boxShadow: '0 20px 60px rgba(0,0,0,0.06)',
          padding: 40,
        }}>
          {/* Logo */}
          <div style={{ textAlign: 'center', marginBottom: 32 }}>
            <Link to="/" style={{ display: 'inline-flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
              <svg width="32" height="32" viewBox="0 0 28 28" fill="none">
                <rect width="28" height="28" fill="black" />
                <text x="6" y="20" fill="white" fontSize="16" fontWeight="700" fontFamily="Inter">N</text>
              </svg>
              <span style={{ fontSize: 20, fontWeight: 700, letterSpacing: '-0.02em', color: '#000' }}>NexusERP</span>
            </Link>
            <h1 className="heading-md" style={{ fontSize: 24, marginBottom: 8 }}>Register Company Workspace</h1>
            <p style={{ fontSize: 14, color: '#767676' }}>Create a new company account and start managing your enterprise.</p>
          </div>

          {error && (
            <div style={{
              padding: '12px 16px',
              background: '#FFF0F0',
              border: '1px solid #FFD0D0',
              color: '#D00000',
              fontSize: 13,
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              marginBottom: 20,
            }}>
              <AlertCircle size={16} />
              {error}
            </div>
          )}

          {success && (
            <div style={{
              padding: '12px 16px',
              background: '#E6F4EA',
              border: '1px solid #CEEAD6',
              color: '#137333',
              fontSize: 13,
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              marginBottom: 20,
            }}>
              <CheckCircle2 size={16} />
              Workspace created! Launching dashboard...
            </div>
          )}

          <form onSubmit={handleRegister} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div>
              <label style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6, color: '#000' }}>
                Company Name
              </label>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                background: '#F7F6F3',
                border: '1px solid #E6E6E6',
                padding: '10px 14px',
              }}>
                <Building2 size={16} color="#767676" />
                <input
                  type="text"
                  required
                  value={formData.company_name}
                  onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                  placeholder="Acme Corporation"
                  style={{
                    border: 'none',
                    background: 'transparent',
                    outline: 'none',
                    fontSize: 14,
                    width: '100%',
                    fontFamily: 'var(--font-body)',
                  }}
                />
              </div>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6, color: '#000' }}>
                Work Email
              </label>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                background: '#F7F6F3',
                border: '1px solid #E6E6E6',
                padding: '10px 14px',
              }}>
                <Mail size={16} color="#767676" />
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="admin@acme.com"
                  style={{
                    border: 'none',
                    background: 'transparent',
                    outline: 'none',
                    fontSize: 14,
                    width: '100%',
                    fontFamily: 'var(--font-body)',
                  }}
                />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div>
                <label style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6, color: '#000' }}>
                  Username
                </label>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  background: '#F7F6F3',
                  border: '1px solid #E6E6E6',
                  padding: '10px 14px',
                }}>
                  <User size={16} color="#767676" />
                  <input
                    type="text"
                    required
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    placeholder="admin_acme"
                    style={{
                      border: 'none',
                      background: 'transparent',
                      outline: 'none',
                      fontSize: 14,
                      width: '100%',
                      fontFamily: 'var(--font-body)',
                    }}
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6, color: '#000' }}>
                  Phone Number
                </label>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  background: '#F7F6F3',
                  border: '1px solid #E6E6E6',
                  padding: '10px 14px',
                }}>
                  <Phone size={16} color="#767676" />
                  <input
                    type="text"
                    value={formData.phone_number}
                    onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                    placeholder="+91 9876543210"
                    style={{
                      border: 'none',
                      background: 'transparent',
                      outline: 'none',
                      fontSize: 14,
                      width: '100%',
                      fontFamily: 'var(--font-body)',
                    }}
                  />
                </div>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div>
                <label style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6, color: '#000' }}>
                  Password
                </label>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  background: '#F7F6F3',
                  border: '1px solid #E6E6E6',
                  padding: '10px 14px',
                }}>
                  <Lock size={16} color="#767676" />
                  <input
                    type="password"
                    required
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    placeholder="••••••••"
                    style={{
                      border: 'none',
                      background: 'transparent',
                      outline: 'none',
                      fontSize: 14,
                      width: '100%',
                      fontFamily: 'var(--font-body)',
                    }}
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6, color: '#000' }}>
                  Confirm Password
                </label>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  background: '#F7F6F3',
                  border: '1px solid #E6E6E6',
                  padding: '10px 14px',
                }}>
                  <Lock size={16} color="#767676" />
                  <input
                    type="password"
                    required
                    value={formData.confirm_password}
                    onChange={(e) => setFormData({ ...formData, confirm_password: e.target.value })}
                    placeholder="••••••••"
                    style={{
                      border: 'none',
                      background: 'transparent',
                      outline: 'none',
                      fontSize: 14,
                      width: '100%',
                      fontFamily: 'var(--font-body)',
                    }}
                  />
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary"
              style={{ width: '100%', justifyContent: 'center', marginTop: 12 }}
            >
              {loading ? 'Creating Workspace...' : 'Register Company Account'} <ArrowRight size={16} />
            </button>
          </form>

          <div style={{ marginTop: 24, textAlign: 'center', fontSize: 13, color: '#767676' }}>
            Already have a workspace?{' '}
            <Link to="/login" style={{ color: '#000', fontWeight: 600, textDecoration: 'underline' }}>
              Sign In
            </Link>
          </div>
        </div>
      </FadeIn>
    </div>
  )
}
