import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { Check, X, Send, Loader2 } from 'lucide-react';
export default function LeavePage() {
    const { isAdmin } = useAuth();
    // Admin State
    const [activeTab, setActiveTab] = useState('requests');
    const [filterStatus, setFilterStatus] = useState('ALL');
    const [allRequests, setAllRequests] = useState([]);
    const [balances, setBalances] = useState([]);
    // Employee State
    const [myRequests, setMyRequests] = useState([]);
    const [leaveTypes, setLeaveTypes] = useState([]);
    const [form, setForm] = useState({
        leave_type: 1,
        start_date: new Date().toISOString().split('T')[0],
        end_date: new Date().toISOString().split('T')[0],
        reason: '',
    });
    const [submitting, setSubmitting] = useState(false);
    const [successMsg, setSuccessMsg] = useState(null);
    const [errorMsg, setErrorMsg] = useState(null);
    const loadData = async () => {
        try {
            const [reqs, balList, types] = await Promise.all([
                api.getLeaveRequests().catch(() => []),
                api.getLeaveBalances().catch(() => []),
                api.getLeaveTypes().catch(() => []),
            ]);
            if (reqs) {
                const list = Array.isArray(reqs) ? reqs : reqs.results || [];
                setAllRequests(list);
                setMyRequests(list);
            }
            if (balList) {
                const bl = Array.isArray(balList) ? balList : balList.results || [];
                setBalances(bl);
            }
            if (types && types.length > 0) {
                setLeaveTypes(types);
                setForm((prev) => ({ ...prev, leave_type: types[0].id }));
            }
        }
        catch {
            // Fallback
        }
    };
    useEffect(() => {
        loadData();
    }, []);
    const handleApprove = async (id) => {
        setAllRequests((prev) => prev.map((r) => r.id === id ? { ...r, status: 'APPROVED', approval_status: 'Approved', leave_status: 'Approved' } : r));
        setMyRequests((prev) => prev.map((r) => r.id === id ? { ...r, status: 'APPROVED', approval_status: 'Approved', leave_status: 'Approved' } : r));
        try {
            await api.approveLeave(id, 'Approved by Admin');
            await loadData();
        }
        catch {
            await loadData();
        }
    };
    const handleReject = async (id) => {
        setAllRequests((prev) => prev.map((r) => r.id === id ? { ...r, status: 'REJECTED', approval_status: 'Rejected', leave_status: 'Rejected' } : r));
        setMyRequests((prev) => prev.map((r) => r.id === id ? { ...r, status: 'REJECTED', approval_status: 'Rejected', leave_status: 'Rejected' } : r));
        try {
            await api.rejectLeave(id, 'Not approved by Admin');
            await loadData();
        }
        catch {
            await loadData();
        }
    };
    const handleApply = async (e) => {
        e.preventDefault();
        setSubmitting(true);
        setSuccessMsg(null);
        setErrorMsg(null);
        try {
            const res = await api.applyLeave({
                leave_type: Number(form.leave_type),
                start_date: form.start_date,
                end_date: form.end_date,
                reason: form.reason,
            });
            setSuccessMsg('Leave request submitted successfully.');
            if (res?.leave_request) {
                setMyRequests((prev) => [res.leave_request, ...prev]);
                setAllRequests((prev) => [res.leave_request, ...prev]);
            }
            setForm((prev) => ({
                ...prev,
                reason: '',
            }));
            await loadData();
        }
        catch (err) {
            setErrorMsg(err.message || 'Submission failed. Please check leave balance or dates.');
        }
        finally {
            setSubmitting(false);
        }
    };
    const calculateDays = (startStr, endStr) => {
        if (!startStr || !endStr)
            return 1;
        const s = new Date(startStr);
        const e = new Date(endStr);
        const diff = Math.ceil((e.getTime() - s.getTime()) / (1000 * 3600 * 24)) + 1;
        return diff > 0 ? diff : 1;
    };
    const getStatusString = (req) => {
        return (req.approval_status || req.leave_status || req.status || 'Pending').toUpperCase();
    };
    const renderStatusBadge = (status) => {
        const st = (status || 'PENDING').toUpperCase();
        if (st === 'APPROVED') {
            return (<span style={{ padding: '3px 8px', background: '#E6F4EA', color: '#137333', fontSize: 11, fontWeight: 700 }}>
          Approved
        </span>);
        }
        if (st === 'REJECTED') {
            return (<span style={{ padding: '3px 8px', background: '#FCE8E6', color: '#C5221F', fontSize: 11, fontWeight: 700 }}>
          Rejected
        </span>);
        }
        return (<span style={{ padding: '3px 8px', background: '#FEF7E0', color: '#B06000', fontSize: 11, fontWeight: 700 }}>
        Pending
      </span>);
    };
    const filteredRequests = allRequests.filter((r) => {
        if (filterStatus === 'ALL')
            return true;
        return getStatusString(r) === filterStatus;
    });
    // ─────────────────────────────────────────
    // ADMIN / HR VIEW
    // ─────────────────────────────────────────
    if (isAdmin) {
        return (<div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
        {/* Title */}
        <div>
          <h1 className="heading-lg" style={{ fontSize: 28, marginBottom: 4 }}>Leave Management Studio</h1>
          <p className="body-md" style={{ color: '#767676' }}>Review employee leave applications, execute approvals, and audit company leave balances.</p>
        </div>

        {/* Tabs Header */}
        <div style={{ display: 'flex', gap: 8, borderBottom: '1px solid #E6E6E6', paddingBottom: 12 }}>
          <button onClick={() => setActiveTab('requests')} style={{
                padding: '10px 20px',
                background: activeTab === 'requests' ? '#000000' : 'transparent',
                color: activeTab === 'requests' ? '#ffffff' : '#000000',
                border: activeTab === 'requests' ? 'none' : '1px solid #E6E6E6',
                fontSize: 13, fontWeight: 700, cursor: 'pointer', borderRadius: 0,
            }}>
            Tab 1 — All Requests ({allRequests.length})
          </button>
          <button onClick={() => setActiveTab('balances')} style={{
                padding: '10px 20px',
                background: activeTab === 'balances' ? '#000000' : 'transparent',
                color: activeTab === 'balances' ? '#ffffff' : '#000000',
                border: activeTab === 'balances' ? 'none' : '1px solid #E6E6E6',
                fontSize: 13, fontWeight: 700, cursor: 'pointer', borderRadius: 0,
            }}>
            Tab 2 — Leave Balances Audit
          </button>
        </div>

        {/* TAB 1: ALL REQUESTS */}
        {activeTab === 'requests' && (<div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {/* Filter Buttons */}
            <div style={{ background: '#ffffff', border: '1px solid #E6E6E6', padding: 16, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {['ALL', 'PENDING', 'APPROVED', 'REJECTED'].map((st) => (<button key={st} onClick={() => setFilterStatus(st)} style={{
                        padding: '8px 16px',
                        background: filterStatus === st ? '#000000' : '#F7F6F3',
                        color: filterStatus === st ? '#ffffff' : '#000000',
                        border: '1px solid #E6E6E6',
                        fontSize: 12, fontWeight: 700, cursor: 'pointer', borderRadius: 0,
                    }}>
                  {st} ({st === 'ALL' ? allRequests.length : allRequests.filter(r => getStatusString(r) === st).length})
                </button>))}
            </div>

            {/* Requests Table */}
            <div style={{ background: '#ffffff', border: '1px solid #E6E6E6', padding: 24 }}>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 13 }}>
                  <thead>
                    <tr style={{ borderBottom: '2px solid #000000', color: '#767676', textTransform: 'uppercase', fontSize: 11, letterSpacing: '0.05em' }}>
                      <th style={{ padding: '12px' }}>Employee</th>
                      <th style={{ padding: '12px' }}>Leave Type</th>
                      <th style={{ padding: '12px' }}>From</th>
                      <th style={{ padding: '12px' }}>To</th>
                      <th style={{ padding: '12px' }}>Days</th>
                      <th style={{ padding: '12px' }}>Reason</th>
                      <th style={{ padding: '12px' }}>Status</th>
                      <th style={{ padding: '12px', textAlign: 'right' }}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredRequests.map((l, i) => {
                    const days = l.total_days ? Number(l.total_days) : calculateDays(l.start_date, l.end_date);
                    const st = getStatusString(l);
                    const isPending = st === 'PENDING';
                    return (<tr key={l.id || i} style={{ borderBottom: '1px solid #E6E6E6' }}>
                          <td style={{ padding: '14px 12px', fontWeight: 700, color: '#000000' }}>
                            {l.employee_name || (l.employee_id ? `EMP-${l.employee_id}` : `Employee #${l.employee}`)}
                          </td>
                          <td style={{ padding: '14px 12px', color: '#555' }}>
                            {l.leave_type_name || l.leave_type_snapshot || l.leave_type || 'Casual Leave'}
                          </td>
                          <td style={{ padding: '14px 12px', color: '#555' }}>{l.start_date}</td>
                          <td style={{ padding: '14px 12px', color: '#555' }}>{l.end_date}</td>
                          <td style={{ padding: '14px 12px', fontWeight: 600 }}>{days} Day{days > 1 ? 's' : ''}</td>
                          <td style={{ padding: '14px 12px', color: '#666', maxWidth: 200, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                            {l.reason || '—'}
                          </td>
                          <td style={{ padding: '14px 12px' }}>{renderStatusBadge(st)}</td>
                          <td style={{ padding: '14px 12px', textAlign: 'right' }}>
                            {isPending ? (<div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
                                <button onClick={() => handleApprove(l.id)} style={{
                                padding: '6px 14px', background: '#000000', color: '#ffffff',
                                border: 'none', fontSize: 12, fontWeight: 700, cursor: 'pointer',
                                display: 'inline-flex', alignItems: 'center', gap: 4, borderRadius: 0,
                            }}>
                                  <Check size={14}/> Approve
                                </button>
                                <button onClick={() => handleReject(l.id)} style={{
                                padding: '6px 14px', background: 'transparent', color: '#C5221F',
                                border: '1px solid #C5221F', fontSize: 12, fontWeight: 700, cursor: 'pointer',
                                display: 'inline-flex', alignItems: 'center', gap: 4, borderRadius: 0,
                            }}>
                                  <X size={14}/> Reject
                                </button>
                              </div>) : (<span style={{ fontSize: 12, color: '#767676' }}>
                                {st === 'APPROVED' ? 'Approved' : 'Rejected'}
                              </span>)}
                          </td>
                        </tr>);
                })}
                    {filteredRequests.length === 0 && (<tr>
                        <td colSpan={8} style={{ padding: 40, textAlign: 'center', color: '#767676' }}>
                          No leave applications found matching the selected filter.
                        </td>
                      </tr>)}
                  </tbody>
                </table>
              </div>
            </div>
          </div>)}

        {/* TAB 2: LEAVE BALANCES AUDIT */}
        {activeTab === 'balances' && (<div style={{ background: '#ffffff', border: '1px solid #E6E6E6', padding: 24 }}>
            <h3 style={{ fontSize: 16, fontWeight: 700, color: '#000000', margin: '0 0 16px' }}>
              Employee Leave Balances & Allocation Ledger
            </h3>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 13 }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #000000', color: '#767676', textTransform: 'uppercase', fontSize: 11, letterSpacing: '0.05em' }}>
                    <th style={{ padding: '12px' }}>Employee</th>
                    <th style={{ padding: '12px' }}>Leave Type</th>
                    <th style={{ padding: '12px' }}>Total Days Allocated</th>
                    <th style={{ padding: '12px' }}>Used Days</th>
                    <th style={{ padding: '12px' }}>Remaining Days Available</th>
                  </tr>
                </thead>
                <tbody>
                  {balances.map((b, i) => (<tr key={b.id || i} style={{ borderBottom: '1px solid #E6E6E6' }}>
                      <td style={{ padding: '14px 12px', fontWeight: 700, color: '#000000' }}>
                        {b.employee_name || `Employee #${b.employee}`}
                      </td>
                      <td style={{ padding: '14px 12px', color: '#555' }}>{b.leave_type_name || b.leave_type || 'Casual Leave'}</td>
                      <td style={{ padding: '14px 12px', fontWeight: 600 }}>{b.allocated_days || 12} Days</td>
                      <td style={{ padding: '14px 12px', color: '#C5221F', fontWeight: 600 }}>{b.used_days || 0} Days</td>
                      <td style={{ padding: '14px 12px', color: '#137333', fontWeight: 700 }}>{b.remaining_days || 12} Days</td>
                    </tr>))}
                  {balances.length === 0 && (<tr>
                      <td colSpan={5} style={{ padding: 32, textAlign: 'center', color: '#767676' }}>
                        No balance records found.
                      </td>
                    </tr>)}
                </tbody>
              </table>
            </div>
          </div>)}
      </div>);
    }
    // ─────────────────────────────────────────
    // EMPLOYEE VIEW
    // ─────────────────────────────────────────
    return (<div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
      <div>
        <h1 className="heading-lg" style={{ fontSize: 28, marginBottom: 4 }}>My Leave Portal</h1>
        <p className="body-md" style={{ color: '#767676' }}>Review leave allowances, submit time-off applications, and track approval status.</p>
      </div>

      {/* Leave Balance Cards (1 card per leave balance) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 20 }}>
        {balances.length > 0 ? (balances.map((b, idx) => (<div key={b.id || idx} style={{ background: '#ffffff', border: '1px solid #E6E6E6', padding: 24 }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: '#767676', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>
                {b.leave_type_name || b.leave_type || 'Leave Balance'}
              </div>
              <div style={{ fontSize: 32, fontWeight: 700, color: '#000000', lineHeight: 1, marginBottom: 8, letterSpacing: '-0.02em' }}>
                {b.remaining_days ?? 12} Days
              </div>
              <div style={{ fontSize: 13, color: '#767676' }}>
                {b.used_days ?? 0} used of {b.allocated_days ?? 12} total days
              </div>
            </div>))) : ([
            { type: 'Casual Leave', total: 12, used: 0, remaining: 12 },
            { type: 'Sick Leave', total: 10, used: 0, remaining: 10 },
            { type: 'Earned Paid Leave', total: 15, used: 0, remaining: 15 },
        ].map((c) => (<div key={c.type} style={{ background: '#ffffff', border: '1px solid #E6E6E6', padding: 24 }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: '#767676', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>
                {c.type}
              </div>
              <div style={{ fontSize: 32, fontWeight: 700, color: '#000000', lineHeight: 1, marginBottom: 8, letterSpacing: '-0.02em' }}>
                {c.remaining} Days
              </div>
              <div style={{ fontSize: 13, color: '#767676' }}>
                {c.used} used of {c.total} total days
              </div>
            </div>)))}
      </div>

      {/* Apply Leave Form */}
      <div style={{ background: '#ffffff', border: '1px solid #E6E6E6', padding: 28 }}>
        <h3 style={{ fontSize: 16, fontWeight: 700, color: '#000000', margin: '0 0 16px' }}>
          Submit New Leave Application
        </h3>

        {successMsg && (<div style={{ padding: '12px 16px', background: '#E6F4EA', border: '1px solid #CEEAD6', color: '#137333', fontSize: 13, fontWeight: 600, marginBottom: 20 }}>
            {successMsg}
          </div>)}
        {errorMsg && (<div style={{ padding: '12px 16px', background: '#FCE8E6', border: '1px solid #FAD2CF', color: '#C5221F', fontSize: 13, fontWeight: 600, marginBottom: 20 }}>
            {errorMsg}
          </div>)}

        <form onSubmit={handleApply} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div>
            <label style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6, color: '#000' }}>
              Leave Type
            </label>
            <select value={form.leave_type} onChange={(e) => setForm({ ...form, leave_type: Number(e.target.value) })} style={{ width: '100%', padding: '10px 14px', background: '#F7F6F3', border: '1px solid #E6E6E6', fontSize: 14, outline: 'none' }}>
              {leaveTypes.length > 0 ? (leaveTypes.map((t) => (<option key={t.id} value={t.id}>
                    {t.name || t.leave_name || t.leave_type_name || `Leave Type #${t.id}`}
                  </option>))) : (<>
                  <option value={1}>Casual Leave</option>
                  <option value={2}>Sick Leave</option>
                  <option value={3}>Earned Paid Leave</option>
                </>)}
            </select>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div>
              <label style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6, color: '#000' }}>
                Start Date
              </label>
              <input type="date" required value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} style={{ width: '100%', padding: '10px 14px', background: '#F7F6F3', border: '1px solid #E6E6E6', fontSize: 14, outline: 'none' }}/>
            </div>
            <div>
              <label style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6, color: '#000' }}>
                End Date
              </label>
              <input type="date" required value={form.end_date} onChange={(e) => setForm({ ...form, end_date: e.target.value })} style={{ width: '100%', padding: '10px 14px', background: '#F7F6F3', border: '1px solid #E6E6E6', fontSize: 14, outline: 'none' }}/>
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6, color: '#000' }}>
              Reason for Leave
            </label>
            <textarea required rows={3} value={form.reason} onChange={(e) => setForm({ ...form, reason: e.target.value })} placeholder="State clear reason for your leave request..." style={{ width: '100%', padding: '10px 14px', background: '#F7F6F3', border: '1px solid #E6E6E6', fontSize: 14, outline: 'none', fontFamily: 'inherit' }}/>
          </div>

          <button type="submit" disabled={submitting} style={{
            padding: '12px 24px', background: '#000000', color: '#ffffff',
            border: 'none', fontSize: 13, fontWeight: 700, cursor: submitting ? 'not-allowed' : 'pointer',
            alignSelf: 'flex-start', borderRadius: 0, display: 'inline-flex', alignItems: 'center', gap: 8,
        }}>
            {submitting ? <><Loader2 size={16} className="animate-spin"/> Submitting...</> : <><Send size={16}/> Submit Application</>}
          </button>
        </form>
      </div>

      {/* My Leave Requests List */}
      <div style={{ background: '#ffffff', border: '1px solid #E6E6E6', padding: 24 }}>
        <h3 style={{ fontSize: 16, fontWeight: 700, color: '#000000', margin: '0 0 16px' }}>
          My Recent Leave Requests ({myRequests.length})
        </h3>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 13 }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #000000', color: '#767676', textTransform: 'uppercase', fontSize: 11, letterSpacing: '0.05em' }}>
                <th style={{ padding: '10px 12px' }}>Leave Type</th>
                <th style={{ padding: '10px 12px' }}>From</th>
                <th style={{ padding: '10px 12px' }}>To</th>
                <th style={{ padding: '10px 12px' }}>Days</th>
                <th style={{ padding: '10px 12px' }}>Reason</th>
                <th style={{ padding: '10px 12px' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {myRequests.slice(0, 15).map((l, i) => {
            const days = l.total_days ? Number(l.total_days) : calculateDays(l.start_date, l.end_date);
            const st = getStatusString(l);
            return (<tr key={l.id || i} style={{ borderBottom: '1px solid #E6E6E6' }}>
                    <td style={{ padding: '12px 12px', fontWeight: 600, color: '#000000' }}>
                      {l.leave_type_name || l.leave_type_snapshot || l.leave_type || 'Casual Leave'}
                    </td>
                    <td style={{ padding: '12px 12px', color: '#555' }}>{l.start_date}</td>
                    <td style={{ padding: '12px 12px', color: '#555' }}>{l.end_date}</td>
                    <td style={{ padding: '12px 12px', fontWeight: 600 }}>{days} Day{days > 1 ? 's' : ''}</td>
                    <td style={{ padding: '12px 12px', color: '#666', maxWidth: 200, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {l.reason || '—'}
                    </td>
                    <td style={{ padding: '12px 12px' }}>{renderStatusBadge(st)}</td>
                  </tr>);
        })}
              {myRequests.length === 0 && (<tr>
                  <td colSpan={6} style={{ padding: 24, textAlign: 'center', color: '#767676' }}>
                    No leave requests submitted yet.
                  </td>
                </tr>)}
            </tbody>
          </table>
        </div>
      </div>
    </div>);
}
