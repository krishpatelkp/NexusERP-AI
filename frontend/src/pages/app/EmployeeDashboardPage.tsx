import React, { useEffect, useState } from 'react'
import { api } from '../../services/api'
import { useAuth } from '../../context/AuthContext'
import { Clock, CalendarDays, Wallet, LogIn, LogOut, CheckCircle2, ChevronDown, ChevronUp, AlertCircle } from 'lucide-react'

export default function EmployeeDashboardPage() {
  const { user } = useAuth()
  const [currentTime, setCurrentTime] = useState<string>(new Date().toLocaleTimeString())

  // Section 1 State
  const [attendanceToday, setAttendanceToday] = useState<{ check_in?: string; check_out?: string; status?: string } | null>(null)
  const [leaveBalance, setLeaveBalance] = useState<number>(12)
  const [lastPayslip, setLastPayslip] = useState<any>(null)

  // Section 2 State
  const [clockedIn, setClockedIn] = useState<boolean>(false)
  const [clockedOut, setClockedOut] = useState<boolean>(false)
  const [checkInTime, setCheckInTime] = useState<string | null>(null)
  const [checkOutTime, setCheckOutTime] = useState<string | null>(null)

  // Section 3 State
  const [myLeaves, setMyLeaves] = useState<any[]>([])

  // Section 4 State (Collapsible Form)
  const [isFormOpen, setIsFormOpen] = useState<boolean>(false)
  const [leaveTypes, setLeaveTypes] = useState<any[]>([])
  const [leaveForm, setLeaveForm] = useState({
    leave_type: 1,
    start_date: new Date().toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0],
    reason: '',
  })
  const [submitting, setSubmitting] = useState(false)
  const [successMsg, setSuccessMsg] = useState<string | null>(null)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  // Live timer update
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString())
    }, 1000)
    return () => clearInterval(timer)
  }, [])

  const loadEmployeeData = async () => {
    try {
      const empId = user?.employee_id_number || user?.id || 1
      const [historyData, attData, balances, payslips, leaves, types] = await Promise.all([
        api.getEmployeeAttendanceHistory(empId).catch(() => []),
        api.getDailyAttendance().catch(() => []),
        api.getLeaveBalances().catch(() => []),
        api.getPayslips().catch(() => []),
        api.getLeaveRequests().catch(() => []),
        api.getLeaveTypes().catch(() => []),
      ])

      // Check today's record for logged-in employee
      const attList = (historyData && historyData.length > 0) ? historyData : attData
      if (attList && attList.length > 0) {
        const todayRec = attList.find((r: any) => r.employee === user?.id || r.employee_id === user?.id) || attList[0]
        if (todayRec) {
          setAttendanceToday(todayRec)
          if (todayRec.check_in) {
            setClockedIn(true)
            setCheckInTime(todayRec.check_in)
          }
          if (todayRec.check_out) {
            setClockedOut(true)
            setCheckOutTime(todayRec.check_out)
          }
        }
      }

      // Calculate total available leave days
      const balList = Array.isArray(balances) ? balances : balances?.results || []
      if (balList && balList.length > 0) {
        const totalAvail = balList.reduce((sum: number, b: any) => sum + (Number(b.remaining_days ?? b.total_allocated ?? 12) || 0), 0)
        setLeaveBalance(totalAvail || 12)
      } else {
        setLeaveBalance(12)
      }

      // Latest payslip
      const slipList = Array.isArray(payslips) ? payslips : payslips?.results || []
      if (slipList && slipList.length > 0) {
        setLastPayslip(slipList[0])
      }

      // My leave applications
      const leaveList = Array.isArray(leaves) ? leaves : leaves?.results || []
      setMyLeaves(leaveList)

      // Leave types
      const typeList = Array.isArray(types) ? types : types?.results || []
      if (typeList && typeList.length > 0) {
        setLeaveTypes(typeList)
        setLeaveForm((prev) => ({ ...prev, leave_type: typeList[0].id }))
      }
    } catch {
      // Silent fallback
    }
  }

  useEffect(() => {
    loadEmployeeData()
  }, [])

  const handleCheckIn = async () => {
    try {
      const employeeId = user?.employee_id || user?.employee_id_number || user?.id
      const result = await api.checkIn(employeeId)
      if (result) {
        setClockedIn(true)
        setCheckInTime(new Date().toLocaleTimeString())
        setErrorMsg(null)
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Check-in failed. Please try again.')
    }
  }

  const handleCheckOut = async () => {
    try {
      const employeeId = user?.employee_id || user?.employee_id_number || user?.id
      const result = await api.checkOut(employeeId)
      if (result) {
        setClockedOut(true)
        setCheckOutTime(new Date().toLocaleTimeString())
        setErrorMsg(null)
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Check-out failed. Please try again.')
    }
  }

  const handleLeaveSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setSuccessMsg(null)
    setErrorMsg(null)

    try {
      await api.applyLeave({
        leave_type: Number(leaveForm.leave_type),
        start_date: leaveForm.start_date,
        end_date: leaveForm.end_date,
        reason: leaveForm.reason,
      })
      setSuccessMsg('Leave application submitted successfully for review.')
      setLeaveForm({
        leave_type: leaveTypes[0]?.id || 1,
        start_date: new Date().toISOString().split('T')[0],
        end_date: new Date().toISOString().split('T')[0],
        reason: '',
      })
      await loadEmployeeData()
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to submit leave application')
    } finally {
      setSubmitting(false)
    }
  }

  const calculateDays = (startStr: string, endStr: string): number => {
    if (!startStr || !endStr) return 1
    const s = new Date(startStr)
    const e = new Date(endStr)
    const diff = Math.ceil((e.getTime() - s.getTime()) / (1000 * 3600 * 24)) + 1
    return diff > 0 ? diff : 1
  }

  const renderLeaveBadge = (status?: string) => {
    const st = (status || 'Pending').toUpperCase()
    if (st === 'APPROVED') {
      return (
        <span style={{ padding: '3px 8px', background: '#E6F4EA', color: '#137333', fontSize: 11, fontWeight: 700 }}>
          Approved
        </span>
      )
    }
    if (st === 'REJECTED') {
      return (
        <span style={{ padding: '3px 8px', background: '#FCE8E6', color: '#C5221F', fontSize: 11, fontWeight: 700 }}>
          Rejected
        </span>
      )
    }
    return (
      <span style={{ padding: '3px 8px', background: '#F1F3F4', color: '#3C4043', fontSize: 11, fontWeight: 700 }}>
        Pending
      </span>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
      {/* SECTION 1 — Personal KPI Cards (3 Cards) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 20 }}>
        {/* Card 1: My Attendance */}
        <div style={{ background: '#ffffff', border: '1px solid #E6E6E6', padding: 24, borderRadius: 0 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: '#767676', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>
            My Attendance Today
          </div>
          <div style={{ fontSize: 24, fontWeight: 700, color: '#000000', lineHeight: 1.2, marginBottom: 8 }}>
            {checkInTime ? (
              <span style={{ color: '#137333' }}>In: {checkInTime}</span>
            ) : (
              <span style={{ color: '#767676' }}>Not Marked</span>
            )}
          </div>
          <div style={{ fontSize: 13, color: '#767676' }}>
            {checkOutTime ? `Out: ${checkOutTime}` : checkInTime ? 'Active Session' : 'Please check in when online'}
          </div>
        </div>

        {/* Card 2: My Leave Balance */}
        <div style={{ background: '#ffffff', border: '1px solid #E6E6E6', padding: 24, borderRadius: 0 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: '#767676', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>
            My Leave Balance
          </div>
          <div style={{ fontSize: 32, fontWeight: 700, color: '#000000', lineHeight: 1, marginBottom: 8, letterSpacing: '-0.02em' }}>
            {leaveBalance} Days
          </div>
          <div style={{ fontSize: 13, color: '#137333', fontWeight: 600 }}>
            Available Paid Allowance
          </div>
        </div>

        {/* Card 3: My Last Payslip */}
        <div style={{ background: '#ffffff', border: '1px solid #E6E6E6', padding: 24, borderRadius: 0 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: '#767676', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>
            My Last Payslip
          </div>
          <div style={{ fontSize: 32, fontWeight: 700, color: '#000000', lineHeight: 1, marginBottom: 8, letterSpacing: '-0.02em' }}>
            ₹{lastPayslip ? Number(lastPayslip.net_salary || 85000).toLocaleString() : '85,000'}
          </div>
          <div style={{ fontSize: 13, color: '#767676', fontWeight: 500 }}>
            {lastPayslip ? `${lastPayslip.month || 'July'} ${lastPayslip.year || 2026} Net Salary` : 'July 2026 Net Salary'}
          </div>
        </div>
      </div>

      {errorMsg && (
        <div style={{ background: '#FCE8E6', border: '1px solid #F5C2C7', color: '#C5221F', padding: '12px 16px', fontSize: 13, fontWeight: 600 }}>
          {errorMsg}
        </div>
      )}

      {/* SECTION 2 — Check In / Check Out Widget */}
      <div style={{ background: '#000000', color: '#ffffff', padding: 28, border: '1px solid #000000', borderRadius: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 20 }}>
          <div>
            <div style={{ fontSize: 12, textTransform: 'uppercase', letterSpacing: '0.05em', color: '#999999', marginBottom: 4 }}>
              Live System Time & Attendance Clock
            </div>
            <div style={{ fontSize: 32, fontWeight: 700, fontFamily: 'monospace', letterSpacing: '-0.02em', marginBottom: 6 }}>
              {currentTime}
            </div>
            <div style={{ fontSize: 13, color: '#cccccc', display: 'flex', alignItems: 'center', gap: 8 }}>
              {clockedIn && !clockedOut && (
                <>
                  <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#28C840' }} />
                  Session Active — Checked in at {checkInTime}
                </>
              )}
              {clockedIn && clockedOut && (
                <>
                  <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#1A73E8' }} />
                  Completed Working Hours — In: {checkInTime} | Out: {checkOutTime}
                </>
              )}
              {!clockedIn && (
                <>
                  <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#FF3B30' }} />
                  No Attendance Entry Recorded Today
                </>
              )}
            </div>
          </div>

          <div>
            {!clockedIn ? (
              <button
                onClick={handleCheckIn}
                style={{
                  padding: '14px 28px', background: '#137333', color: '#ffffff',
                  border: 'none', fontSize: 14, fontWeight: 700, cursor: 'pointer',
                  display: 'inline-flex', alignItems: 'center', gap: 8, borderRadius: 0,
                }}
              >
                <LogIn size={18} /> Mark Check In
              </button>
            ) : !clockedOut ? (
              <button
                onClick={handleCheckOut}
                style={{
                  padding: '14px 28px', background: '#C5221F', color: '#ffffff',
                  border: 'none', fontSize: 14, fontWeight: 700, cursor: 'pointer',
                  display: 'inline-flex', alignItems: 'center', gap: 8, borderRadius: 0,
                }}
              >
                <LogOut size={18} /> Mark Check Out
              </button>
            ) : (
              <div style={{
                padding: '12px 20px', background: 'rgba(255,255,255,0.1)', color: '#ffffff',
                fontSize: 13, fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: 8,
              }}>
                <CheckCircle2 size={18} color="#28C840" /> Attendance Completed for Today
              </div>
            )}
          </div>
        </div>
      </div>

      {/* SECTION 4 — Apply for Leave (Collapsible Form) */}
      <div style={{ background: '#ffffff', border: '1px solid #E6E6E6', padding: 24, borderRadius: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <h3 style={{ fontSize: 16, fontWeight: 700, color: '#000000', margin: 0 }}>
              Leave Application Portal
            </h3>
            <p style={{ fontSize: 13, color: '#767676', margin: '4px 0 0' }}>
              Submit a formal time-off request for manager approval.
            </p>
          </div>
          <button
            onClick={() => setIsFormOpen(!isFormOpen)}
            style={{
              padding: '8px 16px', background: '#000000', color: '#ffffff',
              border: 'none', fontSize: 13, fontWeight: 600, cursor: 'pointer',
              display: 'inline-flex', alignItems: 'center', gap: 6, borderRadius: 0,
            }}
          >
            {isFormOpen ? 'Close Form' : 'Apply for Leave'}
            {isFormOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
        </div>

        {/* Collapsible Form Body */}
        {isFormOpen && (
          <div style={{ marginTop: 24, paddingTop: 24, borderTop: '1px solid #E6E6E6' }}>
            {successMsg && (
              <div style={{ padding: '12px 16px', background: '#E6F4EA', border: '1px solid #CEEAD6', color: '#137333', fontSize: 13, fontWeight: 600, marginBottom: 20 }}>
                {successMsg}
              </div>
            )}
            {errorMsg && (
              <div style={{ padding: '12px 16px', background: '#FCE8E6', border: '1px solid #FAD2CF', color: '#C5221F', fontSize: 13, fontWeight: 600, marginBottom: 20 }}>
                {errorMsg}
              </div>
            )}

            <form onSubmit={handleLeaveSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div>
                <label style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6, color: '#000' }}>
                  Leave Type
                </label>
                <select
                  value={leaveForm.leave_type}
                  onChange={(e) => setLeaveForm({ ...leaveForm, leave_type: Number(e.target.value) })}
                  style={{ width: '100%', padding: '10px 14px', background: '#F7F6F3', border: '1px solid #E6E6E6', fontSize: 14, outline: 'none' }}
                >
                  {leaveTypes.length > 0 ? (
                    leaveTypes.map((t) => (
                      <option key={t.id} value={t.id}>
                        {t.name || t.leave_type_name || `Leave Type #${t.id}`}
                      </option>
                    ))
                  ) : (
                    <>
                      <option value={1}>Casual Leave</option>
                      <option value={2}>Sick Leave</option>
                      <option value={3}>Earned Paid Leave</option>
                    </>
                  )}
                </select>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                <div>
                  <label style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6, color: '#000' }}>
                    Start Date
                  </label>
                  <input
                    type="date"
                    required
                    value={leaveForm.start_date}
                    onChange={(e) => setLeaveForm({ ...leaveForm, start_date: e.target.value })}
                    style={{ width: '100%', padding: '10px 14px', background: '#F7F6F3', border: '1px solid #E6E6E6', fontSize: 14, outline: 'none' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6, color: '#000' }}>
                    End Date
                  </label>
                  <input
                    type="date"
                    required
                    value={leaveForm.end_date}
                    onChange={(e) => setLeaveForm({ ...leaveForm, end_date: e.target.value })}
                    style={{ width: '100%', padding: '10px 14px', background: '#F7F6F3', border: '1px solid #E6E6E6', fontSize: 14, outline: 'none' }}
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6, color: '#000' }}>
                  Reason for Leave
                </label>
                <textarea
                  required
                  rows={3}
                  value={leaveForm.reason}
                  onChange={(e) => setLeaveForm({ ...leaveForm, reason: e.target.value })}
                  placeholder="State brief reason for your leave request..."
                  style={{ width: '100%', padding: '10px 14px', background: '#F7F6F3', border: '1px solid #E6E6E6', fontSize: 14, outline: 'none', fontFamily: 'var(--font-body)' }}
                />
              </div>

              <button
                type="submit"
                disabled={submitting}
                style={{
                  padding: '12px 24px', background: '#000000', color: '#ffffff',
                  border: 'none', fontSize: 13, fontWeight: 700, cursor: 'pointer',
                  alignSelf: 'flex-start', borderRadius: 0,
                }}
              >
                {submitting ? 'Submitting Request...' : 'Submit Leave Request'}
              </button>
            </form>
          </div>
        )}
      </div>

      {/* SECTION 3 — My Recent Leave Requests (Last 5 Requests) */}
      <div style={{ background: '#ffffff', border: '1px solid #E6E6E6', padding: 24, borderRadius: 0 }}>
        <h3 style={{ fontSize: 16, fontWeight: 700, color: '#000000', margin: '0 0 16px' }}>
          My Recent Leave Requests History
        </h3>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 13 }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #000000', color: '#767676', textTransform: 'uppercase', fontSize: 11, letterSpacing: '0.05em' }}>
                <th style={{ padding: '10px 12px' }}>Leave Type</th>
                <th style={{ padding: '10px 12px' }}>From</th>
                <th style={{ padding: '10px 12px' }}>To</th>
                <th style={{ padding: '10px 12px' }}>Days</th>
                <th style={{ padding: '10px 12px' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {myLeaves.slice(0, 5).map((l, i) => {
                const days = calculateDays(l.start_date, l.end_date)
                return (
                  <tr key={l.id || i} style={{ borderBottom: '1px solid #E6E6E6' }}>
                    <td style={{ padding: '12px 12px', fontWeight: 600, color: '#000000' }}>
                      {l.leave_type_name || l.leave_type || 'Casual Leave'}
                    </td>
                    <td style={{ padding: '12px 12px', color: '#555' }}>{l.start_date}</td>
                    <td style={{ padding: '12px 12px', color: '#555' }}>{l.end_date}</td>
                    <td style={{ padding: '12px 12px', fontWeight: 600 }}>{days} Day{days > 1 ? 's' : ''}</td>
                    <td style={{ padding: '12px 12px' }}>
                      {renderLeaveBadge(l.approval_status || l.leave_status || l.status)}
                    </td>
                  </tr>
                )
              })}
              {myLeaves.length === 0 && (
                <tr>
                  <td colSpan={5} style={{ padding: 24, textAlign: 'center', color: '#767676' }}>
                    No leave requests submitted yet.
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
