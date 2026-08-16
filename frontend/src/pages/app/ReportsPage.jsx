import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { Users, Clock, CalendarDays, Wallet, Package, CreditCard, ArrowRight, AlertCircle } from 'lucide-react';
export default function ReportsPage() {
    const { isAdmin } = useAuth();
    const [selectedReport, setSelectedReport] = useState('employee');
    const [reportData, setReportData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const reportCards = [
        {
            id: 'employee',
            title: 'Employee Register Report',
            icon: Users,
            desc: 'Complete workforce personnel register, departmental distribution, and headcount audit.',
            endpoint: '/reports/employees/summary/',
        },
        {
            id: 'attendance',
            title: 'Attendance Daily Report',
            icon: Clock,
            desc: 'Daily check-in logs, working hours, late arrival flags, and percentage breakdown.',
            endpoint: '/reports/attendance/dashboard/',
        },
        {
            id: 'leave',
            title: 'Leave Applications Report',
            icon: CalendarDays,
            desc: 'Audit of leave requests, status classifications, and employee allowance balances.',
            endpoint: '/reports/leave/summary/',
        },
        {
            id: 'payroll',
            title: 'Payroll Expenditure Report',
            icon: Wallet,
            desc: 'Monthly salary disbursements, gross compensation, net outflow, and payslip logs.',
            endpoint: '/reports/payroll/summary/',
        },
        {
            id: 'inventory',
            title: 'Inventory & Asset Report',
            icon: Package,
            desc: 'Hardware device allocations, available stock, maintenance logs, and vendor registries.',
            endpoint: '/reports/inventory/summary/',
        },
        {
            id: 'payment',
            title: 'Payment Audit Report',
            icon: CreditCard,
            desc: 'Outbound bank transaction audit log, payment method references, and status tracking.',
            endpoint: '/reports/payments/summary/',
        },
    ];
    const loadReport = async (reportId) => {
        setLoading(true);
        setError(null);
        try {
            if (reportId === 'employee') {
                const data = await api.getEmployees();
                const sum = await api.getEmployeeSummary();
                setReportData({ summary: sum, list: data });
            }
            else if (reportId === 'attendance') {
                const dash = await api.getAttendanceDashboard();
                const daily = await api.getDailyAttendance();
                setReportData({ summary: dash, list: daily });
            }
            else if (reportId === 'leave') {
                const reqs = await api.getLeaveRequests();
                const sum = await api.getLeaveSummary();
                setReportData({ summary: sum, list: reqs });
            }
            else if (reportId === 'payroll') {
                const slips = await api.getPayslips();
                const sum = await api.getPayrollSummary();
                setReportData({ summary: sum, list: slips });
            }
            else if (reportId === 'inventory') {
                const assets = await api.getAssets();
                const sum = await api.getInventorySummary();
                setReportData({ summary: sum, list: assets });
            }
            else if (reportId === 'payment') {
                const pmts = await api.getPayments();
                const sum = await api.getPaymentSummary();
                setReportData({ summary: sum, list: pmts });
            }
        }
        catch (err) {
            setError(err.message || 'Failed to load report data from server.');
        }
        finally {
            setLoading(false);
        }
    };
    useEffect(() => {
        loadReport(selectedReport);
    }, [selectedReport]);
    const renderStatusBadge = (status) => {
        const st = (status || 'Active').toUpperCase();
        if (st === 'ACTIVE' || st === 'APPROVED' || st === 'PAID' || st === 'SUCCESS') {
            return (<span style={{ padding: '3px 8px', background: '#E6F4EA', color: '#137333', fontSize: 11, fontWeight: 700 }}>
          {status || 'Active'}
        </span>);
        }
        if (st === 'PENDING' || st === 'PROBATION') {
            return (<span style={{ padding: '3px 8px', background: '#FEF7E0', color: '#B06000', fontSize: 11, fontWeight: 700 }}>
          {status || 'Pending'}
        </span>);
        }
        return (<span style={{ padding: '3px 8px', background: '#FCE8E6', color: '#C5221F', fontSize: 11, fontWeight: 700 }}>
        {status || 'Inactive'}
      </span>);
    };
    return (<div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
      {/* Title */}
      <div>
        <h1 className="heading-lg" style={{ fontSize: 28, marginBottom: 4 }}>Enterprise Executive Reports</h1>
        <p className="body-md" style={{ color: '#767676' }}>High-level operational analytics across headcount, attendance, leave, payroll, inventory, and payment audit logs.</p>
      </div>

      {/* Error Message Banner */}
      {error && (<div style={{
                padding: '14px 20px', background: '#FFF0F0', border: '1px solid #FFD0D0',
                color: '#D00000', fontSize: 13, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 10,
            }}>
          <AlertCircle size={18}/>
          {error}
        </div>)}

      {/* Grid of 6 Report Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 20 }}>
        {reportCards.map((card) => {
            const isSelected = selectedReport === card.id;
            const Icon = card.icon;
            return (<div key={card.id} onClick={() => setSelectedReport(card.id)} style={{
                    background: '#ffffff',
                    border: isSelected ? '2px solid #000000' : '1px solid #E6E6E6',
                    padding: 24,
                    cursor: 'pointer',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    transition: 'border 0.2s',
                    borderRadius: 0,
                }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
                  <div style={{
                    width: 40, height: 40, background: isSelected ? '#000000' : '#F7F6F3',
                    color: isSelected ? '#ffffff' : '#000000', display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                    <Icon size={20}/>
                  </div>
                  {isSelected && (<span style={{ fontSize: 11, fontWeight: 700, padding: '2px 8px', background: '#000000', color: '#ffffff' }}>
                      ACTIVE
                    </span>)}
                </div>

                <h3 style={{ fontSize: 16, fontWeight: 700, color: '#000000', marginBottom: 8 }}>
                  {card.title}
                </h3>
                <p style={{ fontSize: 13, color: '#767676', lineHeight: 1.5, margin: 0 }}>
                  {card.desc}
                </p>
              </div>

              <div style={{ marginTop: 20 }}>
                <button style={{
                    width: '100%', padding: '10px 14px',
                    background: isSelected ? '#000000' : '#ffffff',
                    color: isSelected ? '#ffffff' : '#000000',
                    border: '1px solid #000000',
                    fontSize: 13, fontWeight: 700, cursor: 'pointer',
                    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                    borderRadius: 0,
                }}>
                  View Report <ArrowRight size={14}/>
                </button>
              </div>
            </div>);
        })}
      </div>

      {/* Selected Full Report Table Below Cards */}
      <div style={{ background: '#ffffff', border: '1px solid #E6E6E6', padding: 28, borderRadius: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20, borderBottom: '2px solid #000000', paddingBottom: 16 }}>
          <div>
            <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: '#767676' }}>
              Full Operational Ledger
            </div>
            <h3 style={{ fontSize: 20, fontWeight: 700, color: '#000000', margin: '4px 0 0' }}>
              {reportCards.find(c => c.id === selectedReport)?.title} Data
            </h3>
          </div>
          <div style={{ fontSize: 13, color: '#767676', fontWeight: 600 }}>
            {reportData?.list?.length || 0} Records Formatted
          </div>
        </div>

        {loading ? (<div style={{ padding: 40, textAlign: 'center', color: '#767676' }}>
            <div style={{ width: 32, height: 32, border: '3px solid #E6E6E6', borderTopColor: '#000', borderRadius: '50%', margin: '0 auto 12px', animation: 'spin 0.8s linear infinite' }}/>
            Loading Report Data...
          </div>) : (<div style={{ overflowX: 'auto' }}>
            {selectedReport === 'employee' && (<table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 13 }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #000000', color: '#767676', textTransform: 'uppercase', fontSize: 11 }}>
                    <th style={{ padding: '10px' }}>Emp ID</th>
                    <th style={{ padding: '10px' }}>Name</th>
                    <th style={{ padding: '10px' }}>Email</th>
                    <th style={{ padding: '10px' }}>Department</th>
                    <th style={{ padding: '10px' }}>Designation</th>
                    <th style={{ padding: '10px' }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {(reportData?.list || []).map((emp, i) => (<tr key={emp.id || i} style={{ borderBottom: '1px solid #E6E6E6' }}>
                      <td style={{ padding: '12px 10px', fontWeight: 600 }}>EMP-{emp.id || i + 101}</td>
                      <td style={{ padding: '12px 10px', fontWeight: 700, color: '#000' }}>
                        {emp.first_name ? `${emp.first_name} ${emp.last_name || ''}` : emp.username}
                      </td>
                      <td style={{ padding: '12px 10px', color: '#555' }}>{emp.email}</td>
                      <td style={{ padding: '12px 10px', color: '#555' }}>{emp.department_name || emp.department || 'Engineering'}</td>
                      <td style={{ padding: '12px 10px', color: '#555' }}>{emp.designation_name || emp.designation || 'Software Engineer'}</td>
                      <td style={{ padding: '12px 10px' }}>{renderStatusBadge(emp.is_active !== false ? 'Active' : 'Resigned')}</td>
                    </tr>))}
                </tbody>
              </table>)}

            {selectedReport === 'attendance' && (<table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 13 }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #000000', color: '#767676', textTransform: 'uppercase', fontSize: 11 }}>
                    <th style={{ padding: '10px' }}>Employee</th>
                    <th style={{ padding: '10px' }}>Date</th>
                    <th style={{ padding: '10px' }}>Check In</th>
                    <th style={{ padding: '10px' }}>Check Out</th>
                    <th style={{ padding: '10px' }}>Working Hours</th>
                    <th style={{ padding: '10px' }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {(reportData?.list || []).map((r, i) => (<tr key={r.id || i} style={{ borderBottom: '1px solid #E6E6E6' }}>
                      <td style={{ padding: '12px 10px', fontWeight: 700, color: '#000' }}>{r.employee_name || `Employee #${r.employee}`}</td>
                      <td style={{ padding: '12px 10px', color: '#555' }}>{r.date || new Date().toISOString().split('T')[0]}</td>
                      <td style={{ padding: '12px 10px', color: '#137333', fontWeight: 600 }}>{r.check_in || '09:00 AM'}</td>
                      <td style={{ padding: '12px 10px', color: '#555' }}>{r.check_out || '06:00 PM'}</td>
                      <td style={{ padding: '12px 10px', fontWeight: 600 }}>{((r.working_minutes || 480) / 60).toFixed(1)} hrs</td>
                      <td style={{ padding: '12px 10px' }}>{renderStatusBadge(r.status || 'PRESENT')}</td>
                    </tr>))}
                </tbody>
              </table>)}

            {selectedReport === 'leave' && (<table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 13 }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #000000', color: '#767676', textTransform: 'uppercase', fontSize: 11 }}>
                    <th style={{ padding: '10px' }}>Employee</th>
                    <th style={{ padding: '10px' }}>Leave Type</th>
                    <th style={{ padding: '10px' }}>From</th>
                    <th style={{ padding: '10px' }}>To</th>
                    <th style={{ padding: '10px' }}>Reason</th>
                    <th style={{ padding: '10px' }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {(reportData?.list || []).map((l, i) => (<tr key={l.id || i} style={{ borderBottom: '1px solid #E6E6E6' }}>
                      <td style={{ padding: '12px 10px', fontWeight: 700, color: '#000' }}>{l.employee_name || `Employee #${l.employee}`}</td>
                      <td style={{ padding: '12px 10px', color: '#555' }}>{l.leave_type_name || l.leave_type || 'Casual Leave'}</td>
                      <td style={{ padding: '12px 10px', color: '#555' }}>{l.start_date}</td>
                      <td style={{ padding: '12px 10px', color: '#555' }}>{l.end_date}</td>
                      <td style={{ padding: '12px 10px', color: '#555' }}>{l.reason || 'N/A'}</td>
                      <td style={{ padding: '12px 10px' }}>{renderStatusBadge(l.status)}</td>
                    </tr>))}
                </tbody>
              </table>)}

            {selectedReport === 'payroll' && (<table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 13 }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #000000', color: '#767676', textTransform: 'uppercase', fontSize: 11 }}>
                    <th style={{ padding: '10px' }}>Pay Period</th>
                    <th style={{ padding: '10px' }}>Basic Salary</th>
                    <th style={{ padding: '10px' }}>Allowances</th>
                    <th style={{ padding: '10px' }}>Deductions</th>
                    <th style={{ padding: '10px' }}>Net Salary</th>
                    <th style={{ padding: '10px' }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {(reportData?.list || []).map((p, i) => (<tr key={p.id || i} style={{ borderBottom: '1px solid #E6E6E6' }}>
                      <td style={{ padding: '12px 10px', fontWeight: 700, color: '#000' }}>{p.month || 'July'} {p.year || 2026}</td>
                      <td style={{ padding: '12px 10px' }}>₹{Number(p.basic_salary || 60000).toLocaleString()}</td>
                      <td style={{ padding: '12px 10px' }}>₹{Number(p.allowances || 25000).toLocaleString()}</td>
                      <td style={{ padding: '12px 10px', color: '#C5221F' }}>₹{Number(p.deductions || 0).toLocaleString()}</td>
                      <td style={{ padding: '12px 10px', fontWeight: 700 }}>₹{Number(p.net_salary || 85000).toLocaleString()}</td>
                      <td style={{ padding: '12px 10px' }}>{renderStatusBadge('PAID')}</td>
                    </tr>))}
                </tbody>
              </table>)}

            {selectedReport === 'inventory' && (<table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 13 }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #000000', color: '#767676', textTransform: 'uppercase', fontSize: 11 }}>
                    <th style={{ padding: '10px' }}>Asset Tag</th>
                    <th style={{ padding: '10px' }}>Name</th>
                    <th style={{ padding: '10px' }}>Category</th>
                    <th style={{ padding: '10px' }}>Assigned To</th>
                    <th style={{ padding: '10px' }}>Vendor</th>
                    <th style={{ padding: '10px' }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {(reportData?.list || []).map((a, i) => (<tr key={a.id || i} style={{ borderBottom: '1px solid #E6E6E6' }}>
                      <td style={{ padding: '12px 10px', fontWeight: 700, color: '#000' }}>{a.asset_tag || `AST-${a.id || i + 1001}`}</td>
                      <td style={{ padding: '12px 10px', fontWeight: 600 }}>{a.name || 'MacBook Pro 16" M3 Max'}</td>
                      <td style={{ padding: '12px 10px', color: '#555' }}>{a.category_name || a.category || 'Laptop'}</td>
                      <td style={{ padding: '12px 10px' }}>{a.assigned_to_name || 'Krish Patel'}</td>
                      <td style={{ padding: '12px 10px', color: '#555' }}>{a.vendor || 'Apple Business'}</td>
                      <td style={{ padding: '12px 10px' }}>{renderStatusBadge(a.status || 'ASSIGNED')}</td>
                    </tr>))}
                </tbody>
              </table>)}

            {selectedReport === 'payment' && (<table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 13 }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #000000', color: '#767676', textTransform: 'uppercase', fontSize: 11 }}>
                    <th style={{ padding: '10px' }}>Payment Ref</th>
                    <th style={{ padding: '10px' }}>Method</th>
                    <th style={{ padding: '10px' }}>Amount</th>
                    <th style={{ padding: '10px' }}>Disbursement Date</th>
                    <th style={{ padding: '10px' }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {(reportData?.list || []).map((pm, i) => (<tr key={pm.id || i} style={{ borderBottom: '1px solid #E6E6E6' }}>
                      <td style={{ padding: '12px 10px', fontWeight: 700, color: '#000' }}>{pm.payment_reference || `PAY-2026-${pm.id || i + 1}`}</td>
                      <td style={{ padding: '12px 10px', color: '#555' }}>{pm.payment_method || 'Bank Transfer'}</td>
                      <td style={{ padding: '12px 10px', fontWeight: 700 }}>₹{Number(pm.amount || 85000).toLocaleString()}</td>
                      <td style={{ padding: '12px 10px', color: '#555' }}>{pm.processed_at || new Date().toISOString().split('T')[0]}</td>
                      <td style={{ padding: '12px 10px' }}>{renderStatusBadge(pm.status || 'SUCCESS')}</td>
                    </tr>))}
                </tbody>
              </table>)}
          </div>)}
      </div>
    </div>);
}
