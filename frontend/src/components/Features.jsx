import { useState } from 'react';
import { FadeIn } from './animations';
import { Users, Clock, CalendarDays, Wallet, Package, CreditCard, BarChart3, Bot, ArrowRight } from 'lucide-react';
const modules = [
    {
        id: 'hr',
        icon: Users,
        title: 'HR Management',
        subtitle: 'Your people, organized.',
        body: 'Complete employee lifecycle management. Departments, designations, shifts, bank details, documents, and emergency contacts — all in one unified directory.',
        points: ['Employee Directory', 'Department & Designation Cards', 'Shift Scheduling', 'Document Vault'],
    },
    {
        id: 'attendance',
        icon: Clock,
        title: 'Attendance Tracker',
        subtitle: "Know who's where, in real time.",
        body: 'Real-time check-in and check-out tracking with a color-coded monthly heatmap. Identify patterns, track exceptions, and surface top absentees automatically.',
        points: ['Live Clock In / Clock Out', 'Calendar Heatmap', 'Absentee Leaderboard', 'Exception Alerts'],
    },
    {
        id: 'leave',
        icon: CalendarDays,
        title: 'Leave Management',
        subtitle: 'Approve in seconds, not days.',
        body: 'Visual leave balance progress bars, instant request submission, and one-click HR approvals. Track Paid, Casual, and Sick Leave across the organization.',
        points: ['Balance Progress Bars', 'Quick Apply Modal', 'Approve / Reject Actions', 'Department Summaries'],
    },
    {
        id: 'payroll',
        icon: Wallet,
        title: 'Payroll & Payslips',
        subtitle: 'Every rupee, accounted for.',
        body: 'Gross-to-net salary breakdowns, downloadable PDF payslips, department cost analysis, and top earner leaderboards.',
        points: ['Financial Summary', 'PDF Payslip Download', 'Cost Breakdown', 'Top Earner Leaderboard'],
    },
    {
        id: 'inventory',
        icon: Package,
        title: 'Inventory & Assets',
        subtitle: 'Track every asset, everywhere.',
        body: 'Manage the full asset lifecycle — from procurement to retirement. Assign to employees, schedule maintenance, and monitor vendor relationships.',
        points: ['Asset Status Cards', 'Assign to Employee', 'Schedule Maintenance', 'Retire / Decommission'],
    },
    {
        id: 'payments',
        icon: CreditCard,
        title: 'Payments Hub',
        subtitle: 'Salaries, on time. Every time.',
        body: 'View pending salary disbursements, process payments, and track payment history with full audit trails.',
        points: ['Pending Payments', 'Process Payment Action', 'Payment Audit Trail', 'Failed Payment Alerts'],
    },
    {
        id: 'reports',
        icon: BarChart3,
        title: 'Reports & Analytics',
        subtitle: 'Data-driven decisions, instantly.',
        body: 'Cross-module reporting spanning HR, Attendance, Leave, Payroll, Inventory, and Payments. Export any report as an Excel file.',
        points: ['6 Report Categories', 'Interactive Charts', 'Excel Export', 'Trend Analytics'],
    },
    {
        id: 'ai',
        icon: Bot,
        title: 'AI Copilot',
        subtitle: 'Ask anything about your business.',
        body: 'A domain-aware AI assistant that queries your live ERP data using 20 integrated tools. Natural language in, structured answers out.',
        points: ['Natural Language Queries', '20 AI Tools', 'Tool Execution Badges', 'Domain Guardrails'],
    },
];
export default function Features() {
    const [active, setActive] = useState(0);
    const mod = modules[active];
    return (<section id="features" className="section" style={{ background: '#fff' }}>
      <div className="container">
        <FadeIn>
          <div style={{ textAlign: 'center', marginBottom: 64 }}>
            <p className="label" style={{ marginBottom: 16 }}>What's Included</p>
            <h2 className="heading-lg">Everything your business needs</h2>
          </div>
        </FadeIn>

        {/* Tab buttons */}
        <FadeIn delay={100}>
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            flexWrap: 'wrap',
            gap: 4,
            marginBottom: 56,
            borderBottom: '1px solid #e6e6e6',
            paddingBottom: 0,
        }}>
            {modules.map((m, i) => (<button key={m.id} onClick={() => setActive(i)} style={{
                display: 'flex', alignItems: 'center', gap: 6,
                padding: '12px 20px',
                fontSize: 14, fontWeight: 500,
                background: 'none', border: 'none',
                borderBottom: active === i ? '2px solid #000' : '2px solid transparent',
                color: active === i ? '#000' : '#767676',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                fontFamily: 'var(--font-body)',
                marginBottom: -1,
            }}>
                <m.icon size={16}/>
                <span className="hidden sm:inline">{m.title}</span>
              </button>))}
          </div>
        </FadeIn>

        {/* Active module content */}
        <FadeIn key={mod.id}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: 48,
            alignItems: 'center',
        }}>
            {/* Left — Text */}
            <div>
              <div style={{
            width: 48, height: 48,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            background: '#F7F6F3',
            marginBottom: 24,
        }}>
                <mod.icon size={22}/>
              </div>

              <h3 className="heading-md" style={{ marginBottom: 8 }}>{mod.title}</h3>
              <p style={{ fontSize: 16, fontWeight: 500, color: '#767676', marginBottom: 16 }}>{mod.subtitle}</p>
              <p className="body-md" style={{ marginBottom: 32 }}>{mod.body}</p>

              <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '12px 24px',
            marginBottom: 32,
        }}>
                {mod.points.map((p) => (<div key={p} style={{
                display: 'flex', alignItems: 'center', gap: 8,
                fontSize: 14, color: '#000',
            }}>
                    <div style={{
                width: 6, height: 6, background: '#000', borderRadius: '50%', flexShrink: 0,
            }}/>
                    {p}
                  </div>))}
              </div>

              <a href={`#${mod.id}`} className="btn-primary" style={{ display: 'inline-flex' }}>
                Learn More <ArrowRight size={14}/>
              </a>
            </div>

            {/* Right — Visual */}
            <div style={{
            background: '#F7F6F3',
            aspectRatio: '4 / 3',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            padding: 40,
        }}>
              <div style={{
            display: 'flex', alignItems: 'center', gap: 8, marginBottom: 24,
        }}>
                <div style={{ width: 8, height: 8, background: '#000', borderRadius: '50%' }}/>
                <div style={{ height: 10, width: 120, background: '#e6e6e6' }}/>
              </div>
              {[1, 2, 3, 4].map((i) => (<div key={i} style={{
                display: 'flex', alignItems: 'center', gap: 16,
                padding: '16px 0',
                borderBottom: '1px solid #e6e6e6',
            }}>
                  <div style={{ width: 40, height: 40, background: '#e6e6e6', flexShrink: 0 }}/>
                  <div style={{ flex: 1 }}>
                    <div style={{ height: 10, width: `${80 - i * 10}%`, background: '#d4d4d4', marginBottom: 8 }}/>
                    <div style={{ height: 8, width: `${60 - i * 8}%`, background: '#e6e6e6' }}/>
                  </div>
                </div>))}
            </div>
          </div>
        </FadeIn>
      </div>
    </section>);
}
