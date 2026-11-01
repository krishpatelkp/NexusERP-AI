import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { FadeIn } from './animations';
import { 
    Users, Clock, CalendarDays, Wallet, Package, CreditCard, BarChart3, Bot, ArrowRight,
    CheckCircle2, Search, Download, Terminal, Sparkles, UserCheck, Shield, FileText
} from 'lucide-react';

const modules = [
    {
        id: 'hr',
        icon: Users,
        title: 'HR Management',
        subtitle: 'Your people, organized.',
        body: 'Complete employee lifecycle management. Departments, designations, shifts, bank details, documents, and emergency contacts — all in one unified directory.',
        points: ['Employee Directory', 'Department & Designation Cards', 'Shift Scheduling', 'Document Vault'],
        link: '/register',
    },
    {
        id: 'attendance',
        icon: Clock,
        title: 'Attendance Tracker',
        subtitle: "Know who's where, in real time.",
        body: 'Real-time check-in and check-out tracking with a color-coded monthly heatmap. Identify patterns, track exceptions, and surface top absentees automatically.',
        points: ['Live Clock In / Clock Out', 'Calendar Heatmap', 'Absentee Leaderboard', 'Exception Alerts'],
        link: '/register',
    },
    {
        id: 'leave',
        icon: CalendarDays,
        title: 'Leave Management',
        subtitle: 'Approve in seconds, not days.',
        body: 'Visual leave balance progress bars, instant request submission, and one-click HR approvals. Track Paid, Casual, and Sick Leave across the organization.',
        points: ['Balance Progress Bars', 'Quick Apply Modal', 'Approve / Reject Actions', 'Department Summaries'],
        link: '/register',
    },
    {
        id: 'payroll',
        icon: Wallet,
        title: 'Payroll & Payslips',
        subtitle: 'Every rupee, accounted for.',
        body: 'Gross-to-net salary breakdowns, downloadable PDF payslips, department cost analysis, and top earner leaderboards.',
        points: ['Financial Summary', 'PDF Payslip Download', 'Cost Breakdown', 'Top Earner Leaderboard'],
        link: '/register',
    },
    {
        id: 'inventory',
        icon: Package,
        title: 'Inventory & Assets',
        subtitle: 'Track every asset, everywhere.',
        body: 'Manage the full asset lifecycle — from procurement to retirement. Assign to employees, schedule maintenance, and monitor vendor relationships.',
        points: ['Asset Status Cards', 'Assign to Employee', 'Schedule Maintenance', 'Retire / Decommission'],
        link: '/register',
    },
    {
        id: 'payments',
        icon: CreditCard,
        title: 'Payments Hub',
        subtitle: 'Salaries, on time. Every time.',
        body: 'View pending salary disbursements, process payments, and track payment history with full audit trails.',
        points: ['Pending Payments', 'Process Payment Action', 'Payment Audit Trail', 'Failed Payment Alerts'],
        link: '/register',
    },
    {
        id: 'reports',
        icon: BarChart3,
        title: 'Reports & Analytics',
        subtitle: 'Data-driven decisions, instantly.',
        body: 'Cross-module reporting spanning HR, Attendance, Leave, Payroll, Inventory, and Payments. Export any report as an Excel file.',
        points: ['6 Report Categories', 'Interactive Charts', 'Excel Export', 'Trend Analytics'],
        link: '/register',
    },
    {
        id: 'ai',
        icon: Bot,
        title: 'AI Copilot',
        subtitle: 'Ask anything about your business.',
        body: 'A domain-aware AI assistant that queries your live ERP data using 20 integrated tools. Natural language in, structured answers out.',
        points: ['Natural Language Queries', '20 AI Tools', 'Tool Execution Badges', 'Domain Guardrails'],
        link: '/register',
    },
];

function ModulePreviewVisual({ id }) {
    switch (id) {
        case 'hr':
            return (
                <div style={{ background: '#ffffff', border: '1px solid #e6e6e6', padding: 24, borderRadius: 8, boxShadow: '0 10px 30px rgba(0,0,0,0.04)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20, paddingBottom: 12, borderBottom: '1px solid #f0f0f0' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            <Search size={16} color="#767676" />
                            <span style={{ fontSize: 13, color: '#767676', fontWeight: 500 }}>Search 105 active employees...</span>
                        </div>
                        <span style={{ fontSize: 11, padding: '3px 8px', background: '#E6F4EA', color: '#137333', fontWeight: 700, borderRadius: 4 }}>
                            All Departments
                        </span>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                        {[
                            { name: 'Krish Patel', role: 'Senior Software Engineer', dept: 'Engineering', status: 'Active' },
                            { name: 'Aarav Sharma', role: 'Product Manager', dept: 'Product', status: 'Active' },
                            { name: 'Ananya Verma', role: 'UI/UX Design Lead', dept: 'Design', status: 'Active' },
                        ].map((emp, i) => (
                            <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 14px', background: '#F7F6F3', border: '1px solid #E6E6E6' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                                    <div style={{ width: 32, height: 32, borderRadius: '50%', background: '#000', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 12, fontWeight: 700 }}>
                                        {emp.name.split(' ').map(n => n[0]).join('')}
                                    </div>
                                    <div>
                                        <div style={{ fontSize: 13, fontWeight: 700, color: '#000' }}>{emp.name}</div>
                                        <div style={{ fontSize: 11, color: '#767676' }}>{emp.role}</div>
                                    </div>
                                </div>
                                <span style={{ fontSize: 11, fontWeight: 600, padding: '2px 8px', background: '#ffffff', border: '1px solid #e6e6e6' }}>
                                    {emp.dept}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            );
        case 'attendance':
            return (
                <div style={{ background: '#ffffff', border: '1px solid #e6e6e6', padding: 24, borderRadius: 8, boxShadow: '0 10px 30px rgba(0,0,0,0.04)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
                        <div>
                            <div style={{ fontSize: 12, fontWeight: 600, color: '#767676' }}>Daily Attendance Status</div>
                            <div style={{ fontSize: 22, fontWeight: 800, color: '#000' }}>94.2% Present Today</div>
                        </div>
                        <span style={{ fontSize: 11, padding: '4px 10px', background: '#E6F4EA', color: '#137333', fontWeight: 700, borderRadius: 4, display: 'flex', alignItems: 'center', gap: 4 }}>
                            <UserCheck size={14} /> 99 On Time
                        </span>
                    </div>
                    <div style={{ padding: 16, background: '#F7F6F3', border: '1px solid #E6E6E6', marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                            <div style={{ fontSize: 11, color: '#767676', fontWeight: 600 }}>CLOCK IN</div>
                            <div style={{ fontSize: 15, fontWeight: 700, color: '#000' }}>09:15 AM</div>
                        </div>
                        <div style={{ height: 24, width: 1, background: '#e6e6e6' }} />
                        <div>
                            <div style={{ fontSize: 11, color: '#767676', fontWeight: 600 }}>CLOCK OUT</div>
                            <div style={{ fontSize: 15, fontWeight: 700, color: '#000' }}>06:30 PM</div>
                        </div>
                        <span style={{ fontSize: 11, padding: '4px 10px', background: '#000', color: '#fff', fontWeight: 700 }}>
                            Recorded
                        </span>
                    </div>
                </div>
            );
        case 'leave':
            return (
                <div style={{ background: '#ffffff', border: '1px solid #e6e6e6', padding: 24, borderRadius: 8, boxShadow: '0 10px 30px rgba(0,0,0,0.04)' }}>
                    <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 16, color: '#000' }}>Leave Balance Breakdown</div>
                    {[
                        { type: 'Casual Leave', used: 5, total: 7, pct: 71 },
                        { type: 'Sick Leave', used: 2, total: 5, pct: 40 },
                        { type: 'Paid Vacation', used: 10, total: 15, pct: 66 },
                    ].map((item, i) => (
                        <div key={i} style={{ marginBottom: 14 }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, fontWeight: 600, marginBottom: 6 }}>
                                <span>{item.type}</span>
                                <span style={{ color: '#767676' }}>{item.used} / {item.total} days</span>
                            </div>
                            <div style={{ height: 8, background: '#F7F6F3', overflow: 'hidden', border: '1px solid #e6e6e6' }}>
                                <div style={{ height: '100%', width: `${item.pct}%`, background: '#000' }} />
                            </div>
                        </div>
                    ))}
                    <div style={{ marginTop: 20, paddingTop: 12, borderTop: '1px solid #f0f0f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: 12, color: '#137333', fontWeight: 700 }}>1 Request Pending Approval</span>
                        <span style={{ fontSize: 11, textDecoration: 'underline', fontWeight: 700, color: '#000', cursor: 'pointer' }}>Review Request</span>
                    </div>
                </div>
            );
        case 'payroll':
            return (
                <div style={{ background: '#ffffff', border: '1px solid #e6e6e6', padding: 24, borderRadius: 8, boxShadow: '0 10px 30px rgba(0,0,0,0.04)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                        <div>
                            <div style={{ fontSize: 11, color: '#767676', fontWeight: 600 }}>MONTHLY PAYROLL SUMMARY</div>
                            <div style={{ fontSize: 22, fontWeight: 800, color: '#000' }}>₹85,000.00</div>
                        </div>
                        <FileText size={24} color="#767676" />
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: 12, marginBottom: 16 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: '#F7F6F3' }}>
                            <span style={{ color: '#767676' }}>Basic Salary</span>
                            <span style={{ fontWeight: 700 }}>₹65,000.00</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: '#F7F6F3' }}>
                            <span style={{ color: '#767676' }}>Allowances & HRA</span>
                            <span style={{ fontWeight: 700 }}>₹20,000.00</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: '#FFF0F0', color: '#D00000' }}>
                            <span>Statutory Deductions (PF/TDS)</span>
                            <span style={{ fontWeight: 700 }}>-₹5,000.00</span>
                        </div>
                    </div>
                    <button style={{ width: '100%', padding: '10px', background: '#000', color: '#fff', border: 'none', fontSize: 12, fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}>
                        <Download size={14} /> Download Verified PDF Payslip
                    </button>
                </div>
            );
        case 'inventory':
            return (
                <div style={{ background: '#ffffff', border: '1px solid #e6e6e6', padding: 24, borderRadius: 8, boxShadow: '0 10px 30px rgba(0,0,0,0.04)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                        <div style={{ fontSize: 13, fontWeight: 700 }}>Hardware & Software Assets</div>
                        <span style={{ fontSize: 11, fontWeight: 700, padding: '2px 8px', background: '#000', color: '#fff' }}>142 Total Assets</span>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                        {[
                            { name: 'Apple MacBook Pro M3', tag: 'AST-8901', status: 'Assigned (Krish P.)' },
                            { name: 'Dell UltraSharp 27" Monitor', tag: 'AST-4412', status: 'Available in Storage' },
                            { name: 'Logitech MX Master 3S', tag: 'AST-1102', status: 'Assigned (Aarav S.)' },
                        ].map((asset, i) => (
                            <div key={i} style={{ padding: '10px 12px', border: '1px solid #e6e6e6', background: '#F7F6F3', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <div>
                                    <div style={{ fontSize: 12, fontWeight: 700 }}>{asset.name}</div>
                                    <div style={{ fontSize: 10, color: '#767676', fontFamily: 'monospace' }}>{asset.tag}</div>
                                </div>
                                <span style={{ fontSize: 10, fontWeight: 700, padding: '2px 6px', background: '#fff', border: '1px solid #ccc' }}>
                                    {asset.status}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            );
        case 'payments':
            return (
                <div style={{ background: '#ffffff', border: '1px solid #e6e6e6', padding: 24, borderRadius: 8, boxShadow: '0 10px 30px rgba(0,0,0,0.04)' }}>
                    <div style={{ fontSize: 12, fontWeight: 600, color: '#767676' }}>TOTAL DISBURSEMENTS</div>
                    <div style={{ fontSize: 22, fontWeight: 800, color: '#000', marginBottom: 16 }}>₹4,50,000.00</div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                        <div style={{ padding: '12px', background: '#E6F4EA', border: '1px solid #CEEAD6', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                <CheckCircle2 size={16} color="#137333" />
                                <div>
                                    <div style={{ fontSize: 12, fontWeight: 700, color: '#137333' }}>September Salary Batch</div>
                                    <div style={{ fontSize: 10, color: '#137333' }}>Processed to 105 Accounts</div>
                                </div>
                            </div>
                            <span style={{ fontSize: 11, fontWeight: 700, color: '#137333' }}>SUCCESS</span>
                        </div>
                    </div>
                </div>
            );
        case 'reports':
            return (
                <div style={{ background: '#ffffff', border: '1px solid #e6e6e6', padding: 24, borderRadius: 8, boxShadow: '0 10px 30px rgba(0,0,0,0.04)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                        <div style={{ fontSize: 13, fontWeight: 700 }}>Executive Analytics Engine</div>
                        <span style={{ fontSize: 11, padding: '2px 8px', background: '#000', color: '#fff', fontWeight: 700 }}>Excel Export</span>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
                        <div style={{ padding: 12, background: '#F7F6F3', border: '1px solid #e6e6e6' }}>
                            <div style={{ fontSize: 10, color: '#767676', fontWeight: 600 }}>HEADCOUNT GROWTH</div>
                            <div style={{ fontSize: 18, fontWeight: 800 }}>+14.5%</div>
                        </div>
                        <div style={{ padding: 12, background: '#F7F6F3', border: '1px solid #e6e6e6' }}>
                            <div style={{ fontSize: 10, color: '#767676', fontWeight: 600 }}>ATTENDANCE RATE</div>
                            <div style={{ fontSize: 18, fontWeight: 800 }}>94.2%</div>
                        </div>
                    </div>
                </div>
            );
        case 'ai':
            return (
                <div style={{ background: '#000000', border: '1px solid rgba(255,255,255,0.2)', padding: 24, color: '#fff', borderRadius: 8, boxShadow: '0 10px 30px rgba(0,0,0,0.5)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16, paddingBottom: 12, borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                        <Sparkles size={18} color="#fff" />
                        <span style={{ fontSize: 13, fontWeight: 700 }}>NexusERP AI Copilot</span>
                        <span style={{ marginLeft: 'auto', fontSize: 10, padding: '2px 6px', background: '#137333', color: '#fff', fontWeight: 700 }}>ONLINE</span>
                    </div>
                    <div style={{ fontSize: 12, background: 'rgba(255,255,255,0.1)', padding: '10px 14px', marginBottom: 12, borderRadius: 4, fontStyle: 'italic' }}>
                        "How many active employees do we have in Engineering?"
                    </div>
                    <div style={{ fontSize: 12, padding: '10px 14px', background: '#ffffff', color: '#000', fontWeight: 600 }}>
                        Company has 3 active employees in Engineering department.
                    </div>
                    <div style={{ marginTop: 10, display: 'flex', alignItems: 'center', gap: 6 }}>
                        <Terminal size={12} color="#888" />
                        <span style={{ fontSize: 10, color: '#888', fontFamily: 'monospace' }}>Executed: employee_register_tool</span>
                    </div>
                </div>
            );
        default:
            return null;
    }
}

export default function Features() {
    const { user, isAdmin } = useAuth();
    const [active, setActive] = useState(0);
    const mod = modules[active];

    const getModuleLink = (mId) => {
        if (!user) return '/register';
        switch (mId) {
            case 'hr': return isAdmin ? '/employees' : '/dashboard';
            case 'attendance': return '/attendance';
            case 'leave': return '/leave';
            case 'payroll': return '/payroll';
            case 'inventory': return '/inventory';
            case 'payments': return '/payments';
            case 'reports': return isAdmin ? '/reports' : '/dashboard';
            case 'ai': return '/ai';
            default: return '/dashboard';
        }
    };

    return (
        <section id="features" className="section" style={{ background: '#fff' }}>
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
                        {modules.map((m, i) => (
                            <button
                                key={m.id}
                                onClick={() => setActive(i)}
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: 6,
                                    padding: '12px 20px',
                                    fontSize: 14,
                                    fontWeight: 500,
                                    background: 'none',
                                    border: 'none',
                                    borderBottom: active === i ? '2px solid #000' : '2px solid transparent',
                                    color: active === i ? '#000' : '#767676',
                                    cursor: 'pointer',
                                    transition: 'all 0.3s ease',
                                    fontFamily: 'var(--font-body)',
                                    marginBottom: -1,
                                    borderRadius: 0,
                                }}
                            >
                                <m.icon size={16} />
                                <span className="hidden sm:inline">{m.title}</span>
                            </button>
                        ))}
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
                                width: 48,
                                height: 48,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                background: '#F7F6F3',
                                marginBottom: 24,
                            }}>
                                <mod.icon size={22} />
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
                                {mod.points.map((p) => (
                                    <div key={p} style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: 8,
                                        fontSize: 14,
                                        color: '#000',
                                    }}>
                                        <div style={{
                                            width: 6,
                                            height: 6,
                                            background: '#000',
                                            borderRadius: '50%',
                                            flexShrink: 0,
                                        }} />
                                        {p}
                                    </div>
                                ))}
                            </div>

                            <Link to={getModuleLink(mod.id)} className="btn-primary" style={{ display: 'inline-flex', textDecoration: 'none' }}>
                                {user ? 'Open in Workspace' : 'Get Started Free'} <ArrowRight size={14} />
                            </Link>
                        </div>

                        {/* Right — Visual Interactive Module Card */}
                        <div>
                            <ModulePreviewVisual id={mod.id} />
                        </div>
                    </div>
                </FadeIn>
            </div>
        </section>
    );
}
