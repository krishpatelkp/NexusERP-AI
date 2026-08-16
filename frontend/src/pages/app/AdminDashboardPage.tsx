import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../../services/api'
import { ArrowRight, Check, X } from 'lucide-react'

export default function AdminDashboardPage() {
  const [empSummary, setEmpSummary] = useState<any>({ total_employees: 105, active_employees: 102 })
  const [attDashboard, setAttDashboard] = useState<any>({
    attendance_percentage: 94.2,
    present_count: 98,
    absent_count: 3,
    late_count: 4,
    on_leave_count: 2,
    not_marked_count: 0,
    total_employees: 105,
  })
  const [leaveSummary, setLeaveSummary] = useState<any>({ pending: 3 })
  const [payrollSummary, setPayrollSummary] = useState<any>({ total_net: 85000 })

  const [employees, setEmployees] = useState<any[]>([])
  const [pendingLeaves, setPendingLeaves] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  const loadData = async () => {
    try {
      const [empSum, attDash, leaveSum, paySum, empList, leaveReqs] = await Promise.all([
        api.getEmployeeSummary().catch(() => null),
        api.getAttendanceDashboard().catch(() => null),
        api.getLeaveSummary().catch(() => null),
        api.getPayrollSummary().catch(() => null),
        api.getEmployees().catch(() => []),
        api.getLeaveRequests().catch(() => []),
      ])

      if (empSum) setEmpSummary(empSum)
      if (attDash) setAttDashboard(attDash)
      if (leaveSum) setLeaveSummary(leaveSum)
      if (paySum) setPayrollSummary(paySum)
      if (empList) setEmployees(empList)

      if (leaveReqs) {
        const reqList = Array.isArray(leaveReqs) ? leaveReqs : leaveReqs.results || []
        setPendingLeaves(
          reqList.filter(
            (l: any) => {
              const st = (l.approval_status || l.leave_status || l.status || 'Pending').toUpperCase()
              return st === 'PENDING'
            }
          )
        )
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleApprove = async (id: number) => {
    setPendingLeaves((prev) => prev.filter((l) => l.id !== id))
    try {
      await api.approveLeave(id)
      await loadData()
    } catch {
      await loadData()
    }
  }

  const handleReject = async (id: number) => {
    setPendingLeaves((prev) => prev.filter((l) => l.id !== id))
    try {
      await api.rejectLeave(id, 'Not approved by Admin')
      await loadData()
    } catch {
      await loadData()
    }
  }

  const renderStatusBadge = (status?: string) => {
    const st = (status || 'Active').toLowerCase()
    if (st === 'active') {
      return (
        <span style={{ padding: '3px 8px', background: '#000000', color: '#ffffff', fontSize: 11, fontWeight: 700, borderRadius: 0 }}>
          Active
        </span>
      )
    }
    if (st === 'probation') {
      return (
        <span style={{ padding: '3px 8px', background: '#F1F3F4', color: '#3C4043', fontSize: 11, fontWeight: 700, borderRadius: 0 }}>
          Probation
        </span>
      )
    }
    return (
      <span style={{ padding: '3px 8px', background: '#FCE8E6', color: '#C5221F', fontSize: 11, fontWeight: 700, borderRadius: 0 }}>
        {status || 'Resigned'}
      </span>
    )
  }

  const calculateDays = (startStr: string, endStr: string): number => {
    if (!startStr || !endStr) return 1
    const s = new Date(startStr)
    const e = new Date(endStr)
    const diff = Math.ceil((e.getTime() - s.getTime()) / (1000 * 3600 * 24)) + 1
    return diff > 0 ? diff : 1
  }

  const totalEmp = attDashboard.total_employees || empSummary.total_employees || 105

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
      {/* SECTION 1 — KPI Summary Row (4 cards, no border radius) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 20 }}>
        {/* Card 1: Total Employees */}
        <div style={{ background: '#ffffff', border: '1px solid #E6E6E6', padding: 24, borderRadius: 0 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: '#767676', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>
            Total Employees
          </div>
          <div style={{ fontSize: 32, fontWeight: 700, color: '#000000', lineHeight: 1, marginBottom: 8, letterSpacing: '-0.02em' }}>
            {empSummary.total_employees || 105}
          </div>
          <div style={{ fontSize: 13, color: '#137333', fontWeight: 600 }}>
            {empSummary.active_employees || 102} Active Personnel
          </div>
        </div>

        {/* Card 2: Today's Attendance */}
        <div style={{ background: '#ffffff', border: '1px solid #E6E6E6', padding: 24, borderRadius: 0 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: '#767676', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>
            Today's Attendance
          </div>
          <div style={{ fontSize: 32, fontWeight: 700, color: '#000000', lineHeight: 1, marginBottom: 8, letterSpacing: '-0.02em' }}>
            {attDashboard.attendance_percentage ? `${attDashboard.attendance_percentage}%` : '94.2%'}
          </div>
          <div style={{ fontSize: 13, color: '#767676', fontWeight: 500 }}>
            {attDashboard.present_count || 98} / {totalEmp} Present Today
          </div>
        </div>

        {/* Card 3: Pending Leave Requests */}
        <div style={{ background: '#ffffff', border: '1px solid #E6E6E6', padding: 24, borderRadius: 0 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: '#767676', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>
            Pending Leave Requests
          </div>
          <div style={{ fontSize: 32, fontWeight: 700, color: '#000000', lineHeight: 1, marginBottom: 8, letterSpacing: '-0.02em' }}>
            {leaveSummary.pending ?? pendingLeaves.length}
          </div>
          <div style={{ fontSize: 13, color: leaveSummary.pending > 0 ? '#B06000' : '#767676', fontWeight: 600 }}>
            Requires Admin Review
          </div>
        </div>

        {/* Card 4: Payroll This Year */}
        <div style={{ background: '#ffffff', border: '1px solid #E6E6E6', padding: 24, borderRadius: 0 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: '#767676', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>
            Payroll Outflow
          </div>
          <div style={{ fontSize: 32, fontWeight: 700, color: '#000000', lineHeight: 1, marginBottom: 8, letterSpacing: '-0.02em' }}>
            ₹{(payrollSummary.total_net || 85000).toLocaleString()}
          </div>
          <div style={{ fontSize: 13, color: '#137333', fontWeight: 600 }}>
            Current Month Cycle
          </div>
        </div>
      </div>

      {/* SECTION 2 — Two Column Grid (Left 2/3, Right 1/3) */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 24 }} className="grid-cols-1 lg:grid-cols-[2fr_1fr]">
        {/* Left (2/3): Employee Table (first 10 rows) */}
        <div style={{ background: '#ffffff', border: '1px solid #E6E6E6', padding: 24, borderRadius: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
            <h3 style={{ fontSize: 16, fontWeight: 700, color: '#000000', margin: 0 }}>
              Employee Personnel Directory
            </h3>
            <Link
              to="/employees"
              style={{
                fontSize: 13, fontWeight: 600, color: '#000000', textDecoration: 'none',
                display: 'inline-flex', alignItems: 'center', gap: 4,
              }}
            >
              View All <ArrowRight size={14} />
            </Link>
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 13 }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #000000', color: '#767676', textTransform: 'uppercase', fontSize: 11, letterSpacing: '0.05em' }}>
                  <th style={{ padding: '10px 12px' }}>Emp ID</th>
                  <th style={{ padding: '10px 12px' }}>Name</th>
                  <th style={{ padding: '10px 12px' }}>Department</th>
                  <th style={{ padding: '10px 12px' }}>Designation</th>
                  <th style={{ padding: '10px 12px' }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {employees.slice(0, 10).map((emp, i) => (
                  <tr key={emp.id || i} style={{ borderBottom: '1px solid #E6E6E6' }}>
                    <td style={{ padding: '12px 12px', fontWeight: 600 }}>EMP-{emp.id || i + 101}</td>
                    <td style={{ padding: '12px 12px', fontWeight: 600, color: '#000000' }}>
                      {emp.first_name ? `${emp.first_name} ${emp.last_name || ''}` : emp.username || `Employee #${emp.id}`}
                    </td>
                    <td style={{ padding: '12px 12px', color: '#555' }}>{emp.department_name || emp.department || 'Engineering'}</td>
                    <td style={{ padding: '12px 12px', color: '#555' }}>{emp.designation_name || emp.designation || 'Software Engineer'}</td>
                    <td style={{ padding: '12px 12px' }}>
                      {renderStatusBadge(emp.status || (emp.is_active !== false ? 'Active' : 'Resigned'))}
                    </td>
                  </tr>
                ))}
                {employees.length === 0 && (
                  <tr>
                    <td colSpan={5} style={{ padding: 24, textAlign: 'center', color: '#767676' }}>
                      No employee records found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right (1/3): Today's Attendance Breakdown */}
        <div style={{ background: '#ffffff', border: '1px solid #E6E6E6', padding: 24, borderRadius: 0 }}>
          <h3 style={{ fontSize: 16, fontWeight: 700, color: '#000000', margin: '0 0 20px' }}>
            Today's Attendance Breakdown
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {[
              { label: 'Present', count: attDashboard.present_count ?? 98 },
              { label: 'Absent', count: attDashboard.absent_count ?? 3 },
              { label: 'Late', count: attDashboard.late_count ?? 4 },
              { label: 'On Leave', count: attDashboard.on_leave_count ?? 2 },
              { label: 'Not Marked', count: attDashboard.not_marked_count ?? 0 },
            ].map((item) => {
              const pct = totalEmp > 0 ? Math.min(100, Math.round((item.count / totalEmp) * 100)) : 0
              return (
                <div key={item.label}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, fontWeight: 600, marginBottom: 6 }}>
                    <span style={{ color: '#000000' }}>{item.label}</span>
                    <span style={{ color: '#767676' }}>{item.count} ({pct}%)</span>
                  </div>
                  <div style={{ height: 6, background: '#F7F6F3', border: '1px solid #E6E6E6' }}>
                    <div style={{ height: '100%', width: `${pct}%`, background: '#000000' }} />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* SECTION 3 — Leave Requests Pending Approval (Admin only) */}
      <div style={{ background: '#ffffff', border: '1px solid #E6E6E6', padding: 24, borderRadius: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
          <div>
            <h3 style={{ fontSize: 16, fontWeight: 700, color: '#000000', margin: 0 }}>
              Leave Requests Pending Approval
            </h3>
            <p style={{ fontSize: 13, color: '#767676', margin: '4px 0 0' }}>
              Action required on pending employee time-off submissions.
            </p>
          </div>
          <span style={{ padding: '4px 10px', background: '#FEF7E0', color: '#B06000', fontSize: 12, fontWeight: 700 }}>
            {pendingLeaves.length} Pending
          </span>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 13 }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #000000', color: '#767676', textTransform: 'uppercase', fontSize: 11, letterSpacing: '0.05em' }}>
                <th style={{ padding: '10px 12px' }}>Employee Name</th>
                <th style={{ padding: '10px 12px' }}>Leave Type</th>
                <th style={{ padding: '10px 12px' }}>From</th>
                <th style={{ padding: '10px 12px' }}>To</th>
                <th style={{ padding: '10px 12px' }}>Days</th>
                <th style={{ padding: '10px 12px', textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {pendingLeaves.map((leave, i) => {
                const days = calculateDays(leave.start_date, leave.end_date)
                return (
                  <tr key={leave.id || i} style={{ borderBottom: '1px solid #E6E6E6' }}>
                    <td style={{ padding: '12px 12px', fontWeight: 600, color: '#000000' }}>
                      {leave.employee_name || `Employee #${leave.employee}`}
                    </td>
                    <td style={{ padding: '12px 12px', color: '#555' }}>
                      {leave.leave_type_name || leave.leave_type || 'Casual Leave'}
                    </td>
                    <td style={{ padding: '12px 12px', color: '#555' }}>{leave.start_date}</td>
                    <td style={{ padding: '12px 12px', color: '#555' }}>{leave.end_date}</td>
                    <td style={{ padding: '12px 12px', fontWeight: 600 }}>{days} Day{days > 1 ? 's' : ''}</td>
                    <td style={{ padding: '12px 12px', textAlign: 'right' }}>
                      <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
                        {/* Approve Button (solid black) */}
                        <button
                          onClick={() => handleApprove(leave.id)}
                          style={{
                            padding: '6px 14px', background: '#000000', color: '#ffffff',
                            border: 'none', fontSize: 12, fontWeight: 700, cursor: 'pointer',
                            display: 'inline-flex', alignItems: 'center', gap: 4, borderRadius: 0,
                          }}
                        >
                          <Check size={14} /> Approve
                        </button>
                        {/* Reject Button (outline red) */}
                        <button
                          onClick={() => handleReject(leave.id)}
                          style={{
                            padding: '6px 14px', background: 'transparent', color: '#C5221F',
                            border: '1px solid #C5221F', fontSize: 12, fontWeight: 700, cursor: 'pointer',
                            display: 'inline-flex', alignItems: 'center', gap: 4, borderRadius: 0,
                          }}
                        >
                          <X size={14} /> Reject
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
              {pendingLeaves.length === 0 && (
                <tr>
                  <td colSpan={6} style={{ padding: 24, textAlign: 'center', color: '#767676' }}>
                    No pending leave requests requiring approval.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
