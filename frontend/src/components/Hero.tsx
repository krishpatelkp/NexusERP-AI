import { useEffect, useState } from 'react'
import { FadeIn } from './animations'
import { ArrowRight, CheckCircle2 } from 'lucide-react'
import { api } from '../services/api'

export default function Hero() {
  const [metrics, setMetrics] = useState({
    totalEmployees: '105',
    attendanceRate: '94.2%',
    payrollCost: '₹85.0K',
    activeAssets: '12',
  })

  useEffect(() => {
    async function loadLiveBackendData() {
      try {
        await api.autoLogin()
        const [employees, dash] = await Promise.all([
          api.getEmployees().catch(() => []),
          api.getAttendanceDashboard().catch(() => null),
        ])

        if (employees || dash) {
          setMetrics({
            totalEmployees: String(employees.length || 105),
            attendanceRate: dash?.attendance_percentage ? `${dash.attendance_percentage}%` : '94.2%',
            payrollCost: '₹85.0K',
            activeAssets: '12',
          })
        }
      } catch {
        // Fallback
      }
    }
    loadLiveBackendData()
  }, [])

  return (
    <section style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      textAlign: 'center',
      padding: '120px 24px 80px',
      background: '#F7F6F3',
    }}>
      <FadeIn>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6, marginBottom: 24 }}>
          <CheckCircle2 size={16} color="#000" />
          <p className="label" style={{ margin: 0, color: '#000' }}>
            AI-Powered Enterprise Platform
          </p>
        </div>
      </FadeIn>

      <FadeIn delay={100}>
        <h1 className="heading-xl" style={{ maxWidth: 900, marginBottom: 24 }}>
          A new way to manage your entire business
        </h1>
      </FadeIn>

      <FadeIn delay={200}>
        <p className="body-lg" style={{ maxWidth: 560, marginBottom: 40 }}>
          NexusERP brings HR, Payroll, Attendance, Inventory, and Payments together in one platform — with an AI Copilot that understands your data.
        </p>
      </FadeIn>

      <FadeIn delay={300}>
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', justifyContent: 'center' }}>
          <a href="#explorer" className="btn-primary">
            Get Started <ArrowRight size={16} />
          </a>
          <a href="#features" className="btn-secondary">
            See What's Included
          </a>
        </div>
      </FadeIn>

      {/* Dashboard Preview */}
      <FadeIn delay={500}>
        <div style={{
          marginTop: 80,
          width: '100%',
          maxWidth: 1000,
          background: '#fff',
          border: '1px solid #e6e6e6',
          overflow: 'hidden',
          boxShadow: '0 20px 60px rgba(0,0,0,0.08)',
        }}>
          {/* Browser header */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            padding: '12px 16px',
            borderBottom: '1px solid #e6e6e6',
            background: '#fafafa',
          }}>
            <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#FF5F57' }} />
            <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#FFBD2E' }} />
            <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#28C840' }} />
            <div style={{
              flex: 1, marginLeft: 16, height: 28, background: '#f0f0f0', borderRadius: 6,
              display: 'flex', alignItems: 'center', paddingLeft: 12,
              fontSize: 12, color: '#666', fontWeight: 500,
            }}>
              app.nexuserp.com/dashboard
            </div>
          </div>

          {/* Dashboard content */}
          <div style={{ padding: 32 }}>
            {/* KPI row */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
              gap: 16,
              marginBottom: 24,
            }}>
              {[
                { label: 'Total Employees', value: metrics.totalEmployees, change: '+12% this month' },
                { label: 'Attendance Rate', value: metrics.attendanceRate, change: 'Today' },
                { label: 'Payroll Cost', value: metrics.payrollCost, change: 'Current Cycle' },
                { label: 'Active Assets', value: metrics.activeAssets, change: 'In Service' },
              ].map((kpi) => (
                <div key={kpi.label} style={{
                  padding: 20,
                  background: '#F7F6F3',
                  textAlign: 'left',
                }}>
                  <div style={{ fontSize: 12, color: '#767676', marginBottom: 4 }}>{kpi.label}</div>
                  <div style={{ fontSize: 28, fontWeight: 700, letterSpacing: '-0.02em' }}>{kpi.value}</div>
                  <div style={{ fontSize: 12, color: '#000', fontWeight: 500, marginTop: 4 }}>{kpi.change}</div>
                </div>
              ))}
            </div>

            {/* Chart area */}
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16 }}>
              <div style={{ background: '#F7F6F3', padding: 24, minHeight: 180 }}>
                <div style={{ fontSize: 13, color: '#767676', marginBottom: 16 }}>Payroll & Headcount Trend</div>
                <div style={{ display: 'flex', alignItems: 'flex-end', gap: 6, height: 120 }}>
                  {[35, 50, 42, 60, 68, 55, 72, 80, 70, 88, 85, 92].map((h, i) => (
                    <div key={i} style={{
                      flex: 1, height: `${h}%`,
                      background: '#000', opacity: 0.8,
                      transition: 'height 0.5s ease',
                    }} />
                  ))}
                </div>
              </div>
              <div style={{ background: '#F7F6F3', padding: 24, minHeight: 180 }}>
                <div style={{ fontSize: 13, color: '#767676', marginBottom: 16 }}>Today's Attendance</div>
                <div style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  height: 120,
                }}>
                  <div style={{
                    width: 100, height: 100, borderRadius: '50%',
                    border: '6px solid #000',
                    borderTopColor: '#e6e6e6',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: 22, fontWeight: 700,
                  }}>
                    {metrics.attendanceRate}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </FadeIn>
    </section>
  )
}
