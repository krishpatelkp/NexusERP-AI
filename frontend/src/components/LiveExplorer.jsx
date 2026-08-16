import { useState, useEffect } from 'react';
import { FadeIn } from './animations';
import { api } from '../services/api';
import { Users, Clock, CalendarDays, Wallet, Package, CreditCard, Bell, Search, RefreshCw, CheckCircle2, AlertCircle, Building2, ShieldCheck } from 'lucide-react';
export default function LiveExplorer() {
    const [activeTab, setActiveTab] = useState('employees');
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    // Module state data
    const [employees, setEmployees] = useState([]);
    const [attendance, setAttendance] = useState(null);
    const [leaves, setLeaves] = useState([]);
    const [payslips, setPayslips] = useState([]);
    const [assets, setAssets] = useState([]);
    const [payments, setPayments] = useState([]);
    const [notifications, setNotifications] = useState([]);
    const [search, setSearch] = useState('');
    useEffect(() => {
        loadLiveData();
    }, [activeTab]);
    async function loadLiveData() {
        setLoading(true);
        setError(null);
        try {
            const userData = await api.getMe().catch(() => null);
            if (userData)
                setUser(userData);
            switch (activeTab) {
                case 'employees': {
                    const data = await api.getEmployees();
                    setEmployees(data);
                    break;
                }
                case 'attendance': {
                    const data = await api.getAttendanceDashboard();
                    setAttendance(data);
                    break;
                }
                case 'leave': {
                    const data = await api.getLeaveRequests();
                    setLeaves(data);
                    break;
                }
                case 'payroll': {
                    const data = await api.getPayslips();
                    setPayslips(data);
                    break;
                }
                case 'inventory': {
                    const data = await api.getAssets();
                    setAssets(data);
                    break;
                }
                case 'payments': {
                    const data = await api.getPayments();
                    setPayments(data);
                    break;
                }
                case 'notifications': {
                    const data = await api.getNotifications();
                    setNotifications(data);
                    break;
                }
            }
        }
        catch (err) {
            setError(err.message || 'Error loading enterprise data');
        }
        finally {
            setLoading(false);
        }
    }
    const tabs = [
        { id: 'employees', label: 'Employees', icon: Users, count: employees.length },
        { id: 'attendance', label: 'Attendance', icon: Clock },
        { id: 'leave', label: 'Leave Requests', icon: CalendarDays, count: leaves.length },
        { id: 'payroll', label: 'Payroll', icon: Wallet, count: payslips.length },
        { id: 'inventory', label: 'Inventory Assets', icon: Package, count: assets.length },
        { id: 'payments', label: 'Payments', icon: CreditCard, count: payments.length },
        { id: 'notifications', label: 'Notifications', icon: Bell, count: notifications.length },
    ];
    const filteredEmployees = employees.filter((e) => {
        const q = search.toLowerCase();
        const name = `${e.first_name || ''} ${e.last_name || ''}`.toLowerCase();
        const code = (e.employee_code || '').toLowerCase();
        const dept = (e.department_name || e.department || '').toLowerCase();
        return name.includes(q) || code.includes(q) || dept.includes(q);
    });
    return (<section id="explorer" className="section" style={{ background: '#F7F6F3', borderTop: '1px solid #E6E6E6' }}>
      <div className="container">
        <FadeIn>
          <div style={{ textAlign: 'center', marginBottom: 48 }}>
            <p className="label" style={{ marginBottom: 12, display: 'inline-flex', alignItems: 'center', gap: 6 }}>
              <CheckCircle2 size={14} color="#000"/>
              Enterprise Operating System
            </p>
            <h2 className="heading-lg" style={{ marginBottom: 16 }}>
              Interactive Platform Preview
            </h2>
            <p className="body-lg" style={{ maxWidth: 600, margin: '0 auto' }}>
              All-in-one suite for workforce, payroll, inventory, and financial operations.
            </p>

            {/* User Session Bar */}
            {user && (<div style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 16,
                marginTop: 20,
                padding: '8px 20px',
                background: '#fff',
                border: '1px solid #E6E6E6',
                fontSize: 13,
                color: '#000',
                fontWeight: 500,
            }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <ShieldCheck size={16} color="#000"/>
                  Account: <strong>{user.email}</strong>
                </span>
                <span style={{ color: '#ccc' }}>|</span>
                <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <Building2 size={16} color="#000"/>
                  Organization: <strong>{user.company_name || 'Test Company'}</strong>
                </span>
              </div>)}
          </div>
        </FadeIn>

        {/* Explorer Container Card */}
        <FadeIn delay={100}>
          <div style={{
            background: '#fff',
            border: '1px solid #E6E6E6',
            boxShadow: '0 20px 60px rgba(0,0,0,0.06)',
            overflow: 'hidden',
        }}>
            {/* Header Tabs */}
            <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: '1px solid #E6E6E6',
            background: '#fafafa',
            padding: '0 16px',
            overflowX: 'auto',
        }}>
              <div style={{ display: 'flex', gap: 4 }}>
                {tabs.map((tab) => (<button key={tab.id} onClick={() => setActiveTab(tab.id)} style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                padding: '16px 20px',
                background: 'none',
                border: 'none',
                borderBottom: activeTab === tab.id ? '2px solid #000' : '2px solid transparent',
                color: activeTab === tab.id ? '#000' : '#767676',
                fontWeight: activeTab === tab.id ? 600 : 500,
                fontSize: 14,
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                fontFamily: 'var(--font-body)',
                marginBottom: -1,
                whiteSpace: 'nowrap',
            }}>
                    <tab.icon size={16}/>
                    {tab.label}
                    {'count' in tab && tab.count !== undefined && tab.count > 0 && (<span style={{
                    padding: '2px 8px',
                    background: activeTab === tab.id ? '#000' : '#E6E6E6',
                    color: activeTab === tab.id ? '#fff' : '#000',
                    fontSize: 11,
                    fontWeight: 600,
                    borderRadius: 10,
                }}>
                        {tab.count}
                      </span>)}
                  </button>))}
              </div>

              <button onClick={loadLiveData} disabled={loading} title="Refresh Data" style={{
            padding: 8,
            background: 'none',
            border: 'none',
            cursor: loading ? 'not-allowed' : 'pointer',
            color: '#767676',
        }}>
                <RefreshCw size={16} className={loading ? 'animate-spin' : ''}/>
              </button>
            </div>

            {/* Sub-header Controls */}
            {activeTab === 'employees' && (<div style={{
                padding: '16px 24px',
                borderBottom: '1px solid #E6E6E6',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                background: '#fff',
            }}>
                <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                background: '#F7F6F3',
                padding: '8px 16px',
                border: '1px solid #E6E6E6',
                width: 320,
            }}>
                  <Search size={16} color="#767676"/>
                  <input type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Filter employees by name or code..." style={{
                border: 'none',
                background: 'transparent',
                outline: 'none',
                fontSize: 14,
                width: '100%',
                fontFamily: 'var(--font-body)',
            }}/>
                </div>
                <div style={{ fontSize: 13, color: '#767676' }}>
                  Showing <strong>{filteredEmployees.length}</strong> of <strong>{employees.length}</strong> employees
                </div>
              </div>)}

            {/* Content Area */}
            <div style={{ padding: 24, minHeight: 380, maxHeight: 520, overflowY: 'auto' }}>
              {error && (<div style={{
                padding: 16,
                background: '#FFF0F0',
                border: '1px solid #FFD0D0',
                color: '#D00000',
                fontSize: 14,
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                marginBottom: 20,
            }}>
                  <AlertCircle size={18}/>
                  {error}
                </div>)}

              {/* 1. EMPLOYEES TAB */}
              {activeTab === 'employees' && (<table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 14 }}>
                  <thead>
                    <tr style={{ borderBottom: '2px solid #000', color: '#767676', fontSize: 12, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                      <th style={{ padding: '12px 16px' }}>Employee Code</th>
                      <th style={{ padding: '12px 16px' }}>Full Name</th>
                      <th style={{ padding: '12px 16px' }}>Department</th>
                      <th style={{ padding: '12px 16px' }}>Designation</th>
                      <th style={{ padding: '12px 16px' }}>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredEmployees.length > 0 ? (filteredEmployees.slice(0, 15).map((emp) => (<tr key={emp.id} style={{ borderBottom: '1px solid #E6E6E6' }}>
                          <td style={{ padding: '14px 16px', fontWeight: 600, fontFamily: 'monospace' }}>
                            {emp.employee_code || `EMP-${emp.id}`}
                          </td>
                          <td style={{ padding: '14px 16px', fontWeight: 500 }}>
                            {emp.first_name} {emp.last_name}
                          </td>
                          <td style={{ padding: '14px 16px', color: '#555' }}>
                            {emp.department_name || emp.department || 'General'}
                          </td>
                          <td style={{ padding: '14px 16px', color: '#555' }}>
                            {emp.designation_name || emp.designation || 'Staff'}
                          </td>
                          <td style={{ padding: '14px 16px' }}>
                            <span style={{
                    padding: '3px 10px',
                    fontSize: 12,
                    fontWeight: 600,
                    background: emp.is_active !== false ? '#E6F4EA' : '#FCE8E6',
                    color: emp.is_active !== false ? '#137333' : '#C5221F',
                }}>
                              {emp.is_active !== false ? 'Active' : 'Inactive'}
                            </span>
                          </td>
                        </tr>))) : (<tr>
                        <td colSpan={5} style={{ padding: 40, textAlign: 'center', color: '#767676' }}>
                          {loading ? 'Loading employee directory...' : 'No employees found.'}
                        </td>
                      </tr>)}
                  </tbody>
                </table>)}

              {/* 2. ATTENDANCE TAB */}
              {activeTab === 'attendance' && (<div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 24 }}>
                    <div style={{ padding: 20, background: '#F7F6F3' }}>
                      <div style={{ fontSize: 12, color: '#767676' }}>Total Employees</div>
                      <div style={{ fontSize: 32, fontWeight: 700 }}>{attendance?.total_employees ?? employees.length ?? 105}</div>
                    </div>
                    <div style={{ padding: 20, background: '#F7F6F3' }}>
                      <div style={{ fontSize: 12, color: '#767676' }}>Present Today</div>
                      <div style={{ fontSize: 32, fontWeight: 700, color: '#137333' }}>{attendance?.present_count ?? 98}</div>
                    </div>
                    <div style={{ padding: 20, background: '#F7F6F3' }}>
                      <div style={{ fontSize: 12, color: '#767676' }}>Absent Today</div>
                      <div style={{ fontSize: 32, fontWeight: 700, color: '#C5221F' }}>{attendance?.absent_count ?? 7}</div>
                    </div>
                    <div style={{ padding: 20, background: '#F7F6F3' }}>
                      <div style={{ fontSize: 12, color: '#767676' }}>Attendance Rate</div>
                      <div style={{ fontSize: 32, fontWeight: 700 }}>{attendance?.attendance_percentage ?? 94.2}%</div>
                    </div>
                  </div>
                </div>)}

              {/* 3. LEAVE TAB */}
              {activeTab === 'leave' && (<table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 14 }}>
                  <thead>
                    <tr style={{ borderBottom: '2px solid #000', color: '#767676', fontSize: 12, textTransform: 'uppercase' }}>
                      <th style={{ padding: '12px 16px' }}>Employee</th>
                      <th style={{ padding: '12px 16px' }}>Leave Type</th>
                      <th style={{ padding: '12px 16px' }}>Start Date</th>
                      <th style={{ padding: '12px 16px' }}>End Date</th>
                      <th style={{ padding: '12px 16px' }}>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {leaves.length > 0 ? (leaves.map((l) => (<tr key={l.id} style={{ borderBottom: '1px solid #E6E6E6' }}>
                          <td style={{ padding: '14px 16px', fontWeight: 500 }}>{l.employee_name || `Employee #${l.employee}`}</td>
                          <td style={{ padding: '14px 16px' }}>{l.leave_type || 'Casual'}</td>
                          <td style={{ padding: '14px 16px' }}>{l.start_date}</td>
                          <td style={{ padding: '14px 16px' }}>{l.end_date}</td>
                          <td style={{ padding: '14px 16px' }}>
                            <span style={{
                    padding: '3px 10px',
                    fontSize: 12,
                    fontWeight: 600,
                    background: l.status === 'APPROVED' ? '#E6F4EA' : l.status === 'REJECTED' ? '#FCE8E6' : '#FEF7E0',
                    color: l.status === 'APPROVED' ? '#137333' : l.status === 'REJECTED' ? '#C5221F' : '#B06000',
                }}>
                              {l.status}
                            </span>
                          </td>
                        </tr>))) : (<tr>
                        <td colSpan={5} style={{ padding: 40, textAlign: 'center', color: '#767676' }}>
                          {loading ? 'Loading leave requests...' : 'No leave requests recorded.'}
                        </td>
                      </tr>)}
                  </tbody>
                </table>)}

              {/* 4. PAYROLL TAB */}
              {activeTab === 'payroll' && (<table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 14 }}>
                  <thead>
                    <tr style={{ borderBottom: '2px solid #000', color: '#767676', fontSize: 12, textTransform: 'uppercase' }}>
                      <th style={{ padding: '12px 16px' }}>Payslip Code</th>
                      <th style={{ padding: '12px 16px' }}>Employee</th>
                      <th style={{ padding: '12px 16px' }}>Gross Salary</th>
                      <th style={{ padding: '12px 16px' }}>Deductions</th>
                      <th style={{ padding: '12px 16px' }}>Net Pay</th>
                    </tr>
                  </thead>
                  <tbody>
                    {payslips.length > 0 ? (payslips.map((p) => (<tr key={p.id} style={{ borderBottom: '1px solid #E6E6E6' }}>
                          <td style={{ padding: '14px 16px', fontFamily: 'monospace', fontWeight: 600 }}>{p.payslip_number || `PAY-${p.id}`}</td>
                          <td style={{ padding: '14px 16px', fontWeight: 500 }}>{p.employee_name || `Employee #${p.employee}`}</td>
                          <td style={{ padding: '14px 16px' }}>₹{Number(p.gross_salary || 0).toLocaleString()}</td>
                          <td style={{ padding: '14px 16px', color: '#C5221F' }}>₹{Number(p.total_deductions || 0).toLocaleString()}</td>
                          <td style={{ padding: '14px 16px', fontWeight: 700, color: '#137333' }}>₹{Number(p.net_salary || 0).toLocaleString()}</td>
                        </tr>))) : (<tr>
                        <td colSpan={5} style={{ padding: 40, textAlign: 'center', color: '#767676' }}>
                          {loading ? 'Loading payslips...' : 'No payslips found.'}
                        </td>
                      </tr>)}
                  </tbody>
                </table>)}

              {/* 5. INVENTORY TAB */}
              {activeTab === 'inventory' && (<table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 14 }}>
                  <thead>
                    <tr style={{ borderBottom: '2px solid #000', color: '#767676', fontSize: 12, textTransform: 'uppercase' }}>
                      <th style={{ padding: '12px 16px' }}>Asset Tag</th>
                      <th style={{ padding: '12px 16px' }}>Asset Name</th>
                      <th style={{ padding: '12px 16px' }}>Category</th>
                      <th style={{ padding: '12px 16px' }}>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {assets.length > 0 ? (assets.map((a) => (<tr key={a.id} style={{ borderBottom: '1px solid #E6E6E6' }}>
                          <td style={{ padding: '14px 16px', fontFamily: 'monospace', fontWeight: 600 }}>{a.asset_tag || `AST-${a.id}`}</td>
                          <td style={{ padding: '14px 16px', fontWeight: 500 }}>{a.asset_name || a.name}</td>
                          <td style={{ padding: '14px 16px' }}>{a.category_name || 'General'}</td>
                          <td style={{ padding: '14px 16px' }}>
                            <span style={{ padding: '3px 10px', fontSize: 12, fontWeight: 600, background: '#E6F4EA', color: '#137333' }}>
                              {a.status || 'AVAILABLE'}
                            </span>
                          </td>
                        </tr>))) : (<tr>
                        <td colSpan={4} style={{ padding: 40, textAlign: 'center', color: '#767676' }}>
                          {loading ? 'Loading inventory assets...' : 'No inventory assets recorded.'}
                        </td>
                      </tr>)}
                  </tbody>
                </table>)}

              {/* 6. PAYMENTS TAB */}
              {activeTab === 'payments' && (<table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 14 }}>
                  <thead>
                    <tr style={{ borderBottom: '2px solid #000', color: '#767676', fontSize: 12, textTransform: 'uppercase' }}>
                      <th style={{ padding: '12px 16px' }}>Reference</th>
                      <th style={{ padding: '12px 16px' }}>Amount</th>
                      <th style={{ padding: '12px 16px' }}>Payment Date</th>
                      <th style={{ padding: '12px 16px' }}>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {payments.length > 0 ? (payments.map((p) => (<tr key={p.id} style={{ borderBottom: '1px solid #E6E6E6' }}>
                          <td style={{ padding: '14px 16px', fontFamily: 'monospace', fontWeight: 600 }}>{p.reference_number || `PAY-${p.id}`}</td>
                          <td style={{ padding: '14px 16px', fontWeight: 700 }}>₹{Number(p.amount || 0).toLocaleString()}</td>
                          <td style={{ padding: '14px 16px' }}>{p.payment_date || 'Today'}</td>
                          <td style={{ padding: '14px 16px' }}>
                            <span style={{
                    padding: '3px 10px',
                    fontSize: 12,
                    fontWeight: 600,
                    background: p.status === 'COMPLETED' ? '#E6F4EA' : '#FEF7E0',
                    color: p.status === 'COMPLETED' ? '#137333' : '#B06000',
                }}>
                              {p.status || 'PAID'}
                            </span>
                          </td>
                        </tr>))) : (<tr>
                        <td colSpan={4} style={{ padding: 40, textAlign: 'center', color: '#767676' }}>
                          {loading ? 'Loading payments...' : 'No payments found.'}
                        </td>
                      </tr>)}
                  </tbody>
                </table>)}

              {/* 7. NOTIFICATIONS TAB */}
              {activeTab === 'notifications' && (<div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  {notifications.length > 0 ? (notifications.map((n) => (<div key={n.id} style={{ padding: 16, background: n.is_read ? '#fff' : '#F7F6F3', border: '1px solid #E6E6E6', display: 'flex', justifyContent: 'space-between' }}>
                        <div>
                          <div style={{ fontWeight: 600, fontSize: 14 }}>{n.title || n.notification_type}</div>
                          <div style={{ fontSize: 13, color: '#555', marginTop: 4 }}>{n.message}</div>
                        </div>
                        <div style={{ fontSize: 12, color: '#767676' }}>{n.created_at ? new Date(n.created_at).toLocaleDateString() : 'Recent'}</div>
                      </div>))) : (<div style={{ padding: 40, textAlign: 'center', color: '#767676' }}>
                      {loading ? 'Loading notifications...' : 'No unread notifications.'}
                    </div>)}
                </div>)}
            </div>
          </div>
        </FadeIn>
      </div>
    </section>);
}
