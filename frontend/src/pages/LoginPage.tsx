import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { api } from '../services/api'
import { ArrowRight, Lock, Mail, AlertCircle, CheckCircle2 } from 'lucide-react'
import { FadeIn } from '../components/animations'

export default function LoginPage() {
  const [email, setEmail] = useState('Krish@gmail.com')
  const [password, setPassword] = useState('password123')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const navigate = useNavigate()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      await api.login(email, password)
      setSuccess(true)
      setTimeout(() => {
        navigate('/dashboard')
      }, 600)
    } catch (err: any) {
      setError(err.message || 'Invalid email or password')
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
      padding: 24,
    }}>
      <FadeIn>
        <div style={{
          width: '100%',
          maxWidth: 440,
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
            <h1 className="heading-md" style={{ fontSize: 24, marginBottom: 8 }}>Sign in to your workspace</h1>
            <p style={{ fontSize: 14, color: '#767676' }}>Enter your credentials to access your enterprise dashboard.</p>
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
              Login successful! Redirecting to dashboard...
            </div>
          )}

          <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
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
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
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
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
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

            <button
              type="submit"
              disabled={loading}
              className="btn-primary"
              style={{ width: '100%', justifyContent: 'center', marginTop: 8 }}
            >
              {loading ? 'Authenticating...' : 'Sign In'} <ArrowRight size={16} />
            </button>
          </form>

          <div style={{ marginTop: 24, textAlign: 'center', fontSize: 13, color: '#767676' }}>
            Need a new company workspace?{' '}
            <Link to="/register" style={{ color: '#000', fontWeight: 600, textDecoration: 'underline' }}>
              Register Company
            </Link>
          </div>
        </div>
      </FadeIn>
    </div>
  )
}
