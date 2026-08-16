import React, { useEffect, useState } from 'react'
import { api } from '../../services/api'
import { Search, Eye, X, ChevronLeft, ChevronRight, UserPlus, Mail, Phone, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'

export default function EmployeesPage() {
  const [employees, setEmployees] = useState<any[]>([])
  const [departments, setDepartments] = useState<any[]>([])
  const [designations, setDesignations] = useState<any[]>([])
  const [search, setSearch] = useState('')
  const [selectedDept, setSelectedDept] = useState('ALL')
  const [selectedStatus, setSelectedStatus] = useState('ALL')
  const [loading, setLoading] = useState(true)

  // Detail Panel Drawer State
  const [selectedEmp, setSelectedEmp] = useState<any | null>(null)
  const [panelOpen, setPanelOpen] = useState(false)

  // Add Employee Modal State
  const [addModalOpen, setAddModalOpen] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [formSuccess, setFormSuccess] = useState<string | null>(null)
  const [formError, setFormError] = useState<string | null>(null)
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    gender: 'Male',
    marital_status: 'Single',
    blood_group: 'O+',
    date_of_birth: '1998-01-01',
    joining_date: new Date().toISOString().split('T')[0],
    department: 1,
    designation: 1,
    employment_type: 'Full-Time',
    basic_salary: 50000,
  })

  // Pagination State
  const [currentPage, setCurrentPage] = useState(1)
  const pageSize = 20

  const loadData = async () => {
    try {
      const [empData, deptData, desigData] = await Promise.all([
        api.getEmployees().catch(() => []),
        api.getDepartments().catch(() => []),
        api.getDesignations().catch(() => []),
      ])
      setEmployees(empData)
      setDepartments(deptData)
      setDesignations(desigData)
      if (deptData && deptData.length > 0) {
        setFormData((prev) => ({ ...prev, department: deptData[0].id }))
      }
      if (desigData && desigData.length > 0) {
        setFormData((prev) => ({ ...prev, designation: desigData[0].id }))
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  // Filtering Logic
  const filtered = employees.filter((emp) => {
    const term = search.toLowerCase()
    const name = `${emp.first_name || ''} ${emp.last_name || ''} ${emp.username || ''}`.toLowerCase()
    const empId = `EMP-${emp.id || ''}`.toLowerCase()
    const matchesSearch = name.includes(term) || empId.includes(term)

    const deptName = (emp.department_name || emp.department || '').toString()
    const matchesDept = selectedDept === 'ALL' || deptName === selectedDept

    const statusStr = (emp.status || (emp.is_active !== false ? 'Active' : 'Resigned')).toUpperCase()
    const matchesStatus =
      selectedStatus === 'ALL' ||
      (selectedStatus === 'Active' && (statusStr === 'ACTIVE' || emp.is_active !== false)) ||
      (selectedStatus === 'Probation' && statusStr === 'PROBATION') ||
      (selectedStatus === 'Resigned' && (statusStr === 'RESIGNED' || emp.is_active === false))

    return matchesSearch && matchesDept && matchesStatus
  })

  // Pagination Math
  const totalPages = Math.ceil(filtered.length / pageSize) || 1
  const paginatedData = filtered.slice((currentPage - 1) * pageSize, currentPage * pageSize)

  const handleOpenDetail = (emp: any) => {
    setSelectedEmp(emp)
    setPanelOpen(true)
  }

  const handleAddSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setFormError(null)
    setFormSuccess(null)

    try {
      const payload = {
        first_name: formData.first_name,
        last_name: formData.last_name,
        email: formData.email,
        phone: formData.phone || '+919876543210',
        gender: formData.gender,
        marital_status: formData.marital_status,
        blood_group: formData.blood_group,
        date_of_birth: formData.date_of_birth,
        joining_date: formData.joining_date,
        employment_type: formData.employment_type,
        employee_status: 'Active',
        basic_salary: Number(formData.basic_salary) || 50000,
        department: Number(formData.department) || 1,
        designation: Number(formData.designation) || 1,
      }

      await api.createEmployee(payload)
      setFormSuccess('Employee onboarded successfully!')
      await loadData()
      setTimeout(() => {
        setAddModalOpen(false)
        setFormSuccess(null)
        setFormData({
          first_name: '',
          last_name: '',
          email: '',
          phone: '',
          gender: 'Male',
          marital_status: 'Single',
          blood_group: 'O+',
          date_of_birth: '1998-01-01',
          joining_date: new Date().toISOString().split('T')[0],
          department: departments[0]?.id || 1,
          designation: designations[0]?.id || 1,
          employment_type: 'Full-Time',
          basic_salary: 50000,
        })
      }, 1200)
    } catch (err: any) {
      setFormError(err.message || 'Failed to add employee. Please verify required fields.')
    } finally {
      setSubmitting(false)
    }
  }

  const renderStatusBadge = (status?: string) => {
    const st = (status || 'Active').toLowerCase()
    if (st === 'active') {
      return (
        <span style={{ padding: '3px 8px', background: '#000000', color: '#ffffff', fontSize: 11, fontWeight: 700 }}>
          Active
        </span>
      )
    }
    if (st === 'probation') {
      return (
        <span style={{ padding: '3px 8px', background: '#F1F3F4', color: '#3C4043', fontSize: 11, fontWeight: 700 }}>
          Probation
        </span>
      )
    }
    return (
      <span style={{ padding: '3px 8px', background: '#FCE8E6', color: '#C5221F', fontSize: 11, fontWeight: 700 }}>
        {status || 'Resigned'}
      </span>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24, position: 'relative' }}>
      {/* Title & Action Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
        <div>
          <h1 className="heading-lg" style={{ fontSize: 28, marginBottom: 4 }}>Employees Directory</h1>
          <p className="body-md" style={{ color: '#767676' }}>Full workforce registry, department filters, and employee profiles.</p>
        </div>
        <button
          onClick={() => setAddModalOpen(true)}
          style={{
            padding: '10px 20px', background: '#000000', color: '#ffffff',
            border: 'none', fontSize: 13, fontWeight: 700, cursor: 'pointer',
            display: 'inline-flex', alignItems: 'center', gap: 8, borderRadius: 0,
          }}
        >
          <UserPlus size={16} /> + Add Employee
        </button>
      </div>

      {/* Header Controls Row */}
      <div style={{
        background: '#ffffff', border: '1px solid #E6E6E6', padding: 20,
        display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 16, justifyContent: 'space-between',
      }}>
        {/* Search Bar */}
        <div style={{
          flex: 1, minWidth: 260, display: 'flex', alignItems: 'center', gap: 8,
          background: '#F7F6F3', border: '1px solid #E6E6E6', padding: '10px 14px',
        }}>
          <Search size={16} color="#767676" />
          <input
            type="text"
            value={search}
            onChange={(e) => { setSearch(e.target.value); setCurrentPage(1); }}
            placeholder="Filter by name or Employee ID (e.g. EMP-101)..."
            style={{ border: 'none', background: 'transparent', outline: 'none', fontSize: 14, width: '100%' }}
          />
        </div>

        {/* Department Filter Dropdown */}
        <div style={{ minWidth: 180 }}>
          <select
            value={selectedDept}
            onChange={(e) => { setSelectedDept(e.target.value); setCurrentPage(1); }}
            style={{ width: '100%', padding: '10px 14px', background: '#F7F6F3', border: '1px solid #E6E6E6', fontSize: 14, outline: 'none' }}
          >
            <option value="ALL">All Departments</option>
            {departments.map((d) => (
              <option key={d.id} value={d.department_name}>{d.department_name}</option>
            ))}
            {departments.length === 0 && (
              <>
                <option value="Engineering">Engineering</option>
                <option value="Product">Product & Design</option>
                <option value="Human Resources">Human Resources</option>
                <option value="Finance">Finance</option>
                <option value="Operations">Operations</option>
              </>
            )}
          </select>
        </div>

        {/* Status Filter Dropdown */}
        <div style={{ minWidth: 160 }}>
          <select
            value={selectedStatus}
            onChange={(e) => { setSelectedStatus(e.target.value); setCurrentPage(1); }}
            style={{ width: '100%', padding: '10px 14px', background: '#F7F6F3', border: '1px solid #E6E6E6', fontSize: 14, outline: 'none' }}
          >
            <option value="ALL">All Statuses</option>
            <option value="Active">Active</option>
            <option value="Probation">Probation</option>
            <option value="Resigned">Resigned</option>
          </select>
        </div>
      </div>

      {/* Employee Table */}
      <div style={{ background: '#ffffff', border: '1px solid #E6E6E6', padding: 24 }}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 13 }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #000000', color: '#767676', textTransform: 'uppercase', fontSize: 11, letterSpacing: '0.05em' }}>
                <th style={{ padding: '12px' }}>Employee ID</th>
                <th style={{ padding: '12px' }}>Name</th>
                <th style={{ padding: '12px' }}>Department</th>
                <th style={{ padding: '12px' }}>Designation</th>
                <th style={{ padding: '12px' }}>Employment Type</th>
                <th style={{ padding: '12px' }}>Status</th>
                <th style={{ padding: '12px' }}>Joined</th>
                <th style={{ padding: '12px', textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {paginatedData.map((emp, i) => (
                <tr key={emp.id || i} style={{ borderBottom: '1px solid #E6E6E6' }}>
                  <td style={{ padding: '14px 12px', fontWeight: 600 }}>{emp.employee_id || `EMP-${emp.id || i + 101}`}</td>
                  <td style={{ padding: '14px 12px', fontWeight: 700, color: '#000000' }}>
                    {emp.first_name ? `${emp.first_name} ${emp.last_name || ''}` : emp.username || `Employee #${emp.id}`}
                  </td>
                  <td style={{ padding: '14px 12px', color: '#555' }}>{emp.department_name || emp.department || 'Engineering'}</td>
                  <td style={{ padding: '14px 12px', color: '#555' }}>{emp.designation_name || emp.designation || 'Software Engineer'}</td>
                  <td style={{ padding: '14px 12px', color: '#555' }}>{emp.employment_type || 'Full-Time'}</td>
                  <td style={{ padding: '14px 12px' }}>
                    {renderStatusBadge(emp.employee_status || emp.status || (emp.is_active !== false ? 'Active' : 'Resigned'))}
                  </td>
                  <td style={{ padding: '14px 12px', color: '#555' }}>{emp.joining_date || '2024-01-15'}</td>
                  <td style={{ padding: '14px 12px', textAlign: 'right' }}>
                    <button
                      onClick={() => handleOpenDetail(emp)}
                      style={{
                        padding: '6px 12px', background: '#000000', color: '#ffffff',
                        border: 'none', fontSize: 12, fontWeight: 600, cursor: 'pointer',
                        display: 'inline-flex', alignItems: 'center', gap: 6, borderRadius: 0,
                      }}
                    >
                      <Eye size={14} /> View
                    </button>
                  </td>
                </tr>
              ))}
              {paginatedData.length === 0 && (
                <tr>
                  <td colSpan={8} style={{ padding: 40, textAlign: 'center', color: '#767676' }}>
                    No employee records match the selected filter criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls (20 per page) */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 24, paddingTop: 16, borderTop: '1px solid #E6E6E6' }}>
          <div style={{ fontSize: 13, color: '#767676' }}>
            Showing {filtered.length > 0 ? (currentPage - 1) * pageSize + 1 : 0} - {Math.min(currentPage * pageSize, filtered.length)} of {filtered.length} employees
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              style={{
                padding: '6px 14px', background: '#ffffff', border: '1px solid #E6E6E6',
                fontSize: 13, fontWeight: 600, cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
                opacity: currentPage === 1 ? 0.5 : 1, display: 'inline-flex', alignItems: 'center', gap: 4,
              }}
            >
              <ChevronLeft size={16} /> Previous
            </button>

            <span style={{ fontSize: 13, fontWeight: 600, color: '#000' }}>
              Page {currentPage} of {totalPages}
            </span>

            <button
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              style={{
                padding: '6px 14px', background: '#ffffff', border: '1px solid #E6E6E6',
                fontSize: 13, fontWeight: 600, cursor: currentPage === totalPages ? 'not-allowed' : 'pointer',
                opacity: currentPage === totalPages ? 0.5 : 1, display: 'inline-flex', alignItems: 'center', gap: 4,
              }}
            >
              Next <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* Add Employee Modal Dialog */}
      {addModalOpen && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.6)', zIndex: 1100,
          display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20,
        }}>
          <div style={{
            background: '#ffffff', border: '1px solid #000000', width: '100%', maxWidth: 640,
            maxHeight: '90vh', overflowY: 'auto', padding: 32, position: 'relative',
          }}>
            {/* Modal Header */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20, borderBottom: '1px solid #E6E6E6', paddingBottom: 16 }}>
              <div>
                <h3 style={{ fontSize: 20, fontWeight: 700, margin: 0, color: '#000000' }}>Onboard New Employee</h3>
                <p style={{ fontSize: 13, color: '#767676', margin: '4px 0 0' }}>Add a new staff member to your company workforce registry.</p>
              </div>
              <button onClick={() => setAddModalOpen(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 4 }}>
                <X size={20} />
              </button>
            </div>

            {formSuccess && (
              <div style={{ background: '#E6F4EA', border: '1px solid #CEEAD6', color: '#137333', padding: '12px 16px', fontSize: 13, fontWeight: 600, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                <CheckCircle size={16} /> {formSuccess}
              </div>
            )}

            {formError && (
              <div style={{ background: '#FFF0F0', border: '1px solid #FFD0D0', color: '#D00000', padding: '12px 16px', fontSize: 13, fontWeight: 600, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                <AlertCircle size={16} /> {formError}
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleAddSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {/* Row 1: Names */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                <div>
                  <label style={{ display: 'block', fontSize: 12, fontWeight: 700, marginBottom: 6, textTransform: 'uppercase' }}>First Name *</label>
                  <input
                    type="text" required
                    value={formData.first_name}
                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                    placeholder="e.g. John"
                    style={{ width: '100%', padding: '10px 12px', border: '1px solid #E6E6E6', background: '#F7F6F3', fontSize: 13, outline: 'none' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: 12, fontWeight: 700, marginBottom: 6, textTransform: 'uppercase' }}>Last Name *</label>
                  <input
                    type="text" required
                    value={formData.last_name}
                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                    placeholder="e.g. Doe"
                    style={{ width: '100%', padding: '10px 12px', border: '1px solid #E6E6E6', background: '#F7F6F3', fontSize: 13, outline: 'none' }}
                  />
                </div>
              </div>

              {/* Row 2: Contact */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                <div>
                  <label style={{ display: 'block', fontSize: 12, fontWeight: 700, marginBottom: 6, textTransform: 'uppercase' }}>Work Email *</label>
                  <input
                    type="email" required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    placeholder="john.doe@company.com"
                    style={{ width: '100%', padding: '10px 12px', border: '1px solid #E6E6E6', background: '#F7F6F3', fontSize: 13, outline: 'none' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: 12, fontWeight: 700, marginBottom: 6, textTransform: 'uppercase' }}>Phone Number</label>
                  <input
                    type="text"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    placeholder="+91 9876543210"
                    style={{ width: '100%', padding: '10px 12px', border: '1px solid #E6E6E6', background: '#F7F6F3', fontSize: 13, outline: 'none' }}
                  />
                </div>
              </div>

              {/* Row 3: Department & Designation */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                <div>
                  <label style={{ display: 'block', fontSize: 12, fontWeight: 700, marginBottom: 6, textTransform: 'uppercase' }}>Department *</label>
                  <select
                    value={formData.department}
                    onChange={(e) => setFormData({ ...formData, department: Number(e.target.value) })}
                    style={{ width: '100%', padding: '10px 12px', border: '1px solid #E6E6E6', background: '#F7F6F3', fontSize: 13, outline: 'none' }}
                  >
                    {departments.map((d) => (
                      <option key={d.id} value={d.id}>{d.department_name}</option>
                    ))}
                    {departments.length === 0 && <option value={1}>General Engineering</option>}
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: 12, fontWeight: 700, marginBottom: 6, textTransform: 'uppercase' }}>Designation *</label>
                  <select
                    value={formData.designation}
                    onChange={(e) => setFormData({ ...formData, designation: Number(e.target.value) })}
                    style={{ width: '100%', padding: '10px 12px', border: '1px solid #E6E6E6', background: '#F7F6F3', fontSize: 13, outline: 'none' }}
                  >
                    {designations.map((d) => (
                      <option key={d.id} value={d.id}>{d.designation_name}</option>
                    ))}
                    {designations.length === 0 && <option value={1}>Software Engineer</option>}
                  </select>
                </div>
              </div>

              {/* Row 4: Employment Type & Salary */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                <div>
                  <label style={{ display: 'block', fontSize: 12, fontWeight: 700, marginBottom: 6, textTransform: 'uppercase' }}>Employment Type</label>
                  <select
                    value={formData.employment_type}
                    onChange={(e) => setFormData({ ...formData, employment_type: e.target.value })}
                    style={{ width: '100%', padding: '10px 12px', border: '1px solid #E6E6E6', background: '#F7F6F3', fontSize: 13, outline: 'none' }}
                  >
                    <option value="Full-Time">Full-Time</option>
                    <option value="Part-Time">Part-Time</option>
                    <option value="Contract">Contract</option>
                    <option value="Intern">Intern</option>
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: 12, fontWeight: 700, marginBottom: 6, textTransform: 'uppercase' }}>Basic Salary (₹/mo)</label>
                  <input
                    type="number"
                    value={formData.basic_salary}
                    onChange={(e) => setFormData({ ...formData, basic_salary: Number(e.target.value) })}
                    style={{ width: '100%', padding: '10px 12px', border: '1px solid #E6E6E6', background: '#F7F6F3', fontSize: 13, outline: 'none' }}
                  />
                </div>
              </div>

              {/* Row 5: Gender & DOB */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                <div>
                  <label style={{ display: 'block', fontSize: 12, fontWeight: 700, marginBottom: 6, textTransform: 'uppercase' }}>Gender</label>
                  <select
                    value={formData.gender}
                    onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                    style={{ width: '100%', padding: '10px 12px', border: '1px solid #E6E6E6', background: '#F7F6F3', fontSize: 13, outline: 'none' }}
                  >
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: 12, fontWeight: 700, marginBottom: 6, textTransform: 'uppercase' }}>Date of Birth</label>
                  <input
                    type="date"
                    value={formData.date_of_birth}
                    onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                    style={{ width: '100%', padding: '10px 12px', border: '1px solid #E6E6E6', background: '#F7F6F3', fontSize: 13, outline: 'none' }}
                  />
                </div>
              </div>

              {/* Actions */}
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 12 }}>
                <button
                  type="button"
                  onClick={() => setAddModalOpen(false)}
                  style={{ padding: '10px 20px', background: '#F1F3F4', color: '#3C4043', border: 'none', fontSize: 13, fontWeight: 600, cursor: 'pointer' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  style={{
                    padding: '10px 24px', background: '#000000', color: '#ffffff',
                    border: 'none', fontSize: 13, fontWeight: 700, cursor: submitting ? 'not-allowed' : 'pointer',
                    display: 'inline-flex', alignItems: 'center', gap: 8,
                  }}
                >
                  {submitting ? <><Loader2 size={16} className="animate-spin" /> Saving...</> : 'Save & Onboard'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Employee Detail Slide-In Panel Drawer (Right 440px wide) */}
      {panelOpen && selectedEmp && (
        <div style={{
          position: 'fixed', top: 0, right: 0, bottom: 0, width: 440,
          background: '#ffffff', borderLeft: '1px solid #E6E6E6',
          boxShadow: '-10px 0 30px rgba(0,0,0,0.1)', zIndex: 1000,
          display: 'flex', flexDirection: 'column', overflowY: 'auto',
        }}>
          {/* Panel Header */}
          <div style={{
            padding: '24px 28px', borderBottom: '1px solid #E6E6E6',
            display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: '#fafafa',
          }}>
            <div>
              <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: '#767676' }}>
                Employee Personnel Profile
              </div>
              <h3 style={{ fontSize: 20, fontWeight: 700, color: '#000000', margin: '4px 0 0' }}>
                {selectedEmp.first_name ? `${selectedEmp.first_name} ${selectedEmp.last_name || ''}` : selectedEmp.username}
              </h3>
            </div>
            <button
              onClick={() => setPanelOpen(false)}
              style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 6, color: '#767676' }}
            >
              <X size={20} />
            </button>
          </div>

          {/* Panel Body Sections */}
          <div style={{ padding: 28, display: 'flex', flexDirection: 'column', gap: 24 }}>
            {/* Personal Section */}
            <div>
              <div style={{ fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: '#000000', marginBottom: 12, borderBottom: '1px solid #000', paddingBottom: 4 }}>
                Personal Information
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, fontSize: 13 }}>
                <div>
                  <div style={{ color: '#767676' }}>Gender</div>
                  <div style={{ fontWeight: 600, color: '#000' }}>{selectedEmp.gender || 'Male'}</div>
                </div>
                <div>
                  <div style={{ color: '#767676' }}>Date of Birth</div>
                  <div style={{ fontWeight: 600, color: '#000' }}>{selectedEmp.date_of_birth || selectedEmp.dob || '1992-06-14'}</div>
                </div>
                <div>
                  <div style={{ color: '#767676' }}>Blood Group</div>
                  <div style={{ fontWeight: 600, color: '#000' }}>{selectedEmp.blood_group || 'O+'}</div>
                </div>
                <div>
                  <div style={{ color: '#767676' }}>Marital Status</div>
                  <div style={{ fontWeight: 600, color: '#000' }}>{selectedEmp.marital_status || 'Single'}</div>
                </div>
              </div>
            </div>

            {/* Contact Section */}
            <div>
              <div style={{ fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: '#000000', marginBottom: 12, borderBottom: '1px solid #000', paddingBottom: 4 }}>
                Contact Information
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10, fontSize: 13 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Mail size={16} color="#767676" />
                  <span style={{ fontWeight: 600, color: '#000' }}>{selectedEmp.email || 'N/A'}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Phone size={16} color="#767676" />
                  <span style={{ fontWeight: 600, color: '#000' }}>{selectedEmp.phone || selectedEmp.phone_number || '+91 9876543210'}</span>
                </div>
              </div>
            </div>

            {/* Organization Section */}
            <div>
              <div style={{ fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: '#000000', marginBottom: 12, borderBottom: '1px solid #000', paddingBottom: 4 }}>
                Organization & Role
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, fontSize: 13 }}>
                <div>
                  <div style={{ color: '#767676' }}>Department</div>
                  <div style={{ fontWeight: 600, color: '#000' }}>{selectedEmp.department_name || selectedEmp.department || 'Engineering'}</div>
                </div>
                <div>
                  <div style={{ color: '#767676' }}>Designation</div>
                  <div style={{ fontWeight: 600, color: '#000' }}>{selectedEmp.designation_name || selectedEmp.designation || 'Software Engineer'}</div>
                </div>
                <div>
                  <div style={{ color: '#767676' }}>Employment Type</div>
                  <div style={{ fontWeight: 600, color: '#000' }}>{selectedEmp.employment_type || 'Full-Time'}</div>
                </div>
                <div>
                  <div style={{ color: '#767676' }}>Joining Date</div>
                  <div style={{ fontWeight: 600, color: '#000' }}>{selectedEmp.joining_date || '2024-01-15'}</div>
                </div>
                <div>
                  <div style={{ color: '#767676' }}>Confirmation Date</div>
                  <div style={{ fontWeight: 600, color: '#000' }}>{selectedEmp.confirmation_date || '2024-07-15'}</div>
                </div>
                <div>
                  <div style={{ color: '#767676' }}>Manager</div>
                  <div style={{ fontWeight: 600, color: '#000' }}>{selectedEmp.reporting_manager_name || selectedEmp.manager_name || 'Department Head'}</div>
                </div>
              </div>
            </div>

            {/* Status Section */}
            <div>
              <div style={{ fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: '#000000', marginBottom: 12, borderBottom: '1px solid #000', paddingBottom: 4 }}>
                Status Classification
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                {renderStatusBadge(selectedEmp.employee_status || selectedEmp.status || (selectedEmp.is_active !== false ? 'Active' : 'Resigned'))}
                <span style={{ fontSize: 13, color: '#767676' }}>
                  {selectedEmp.is_active !== false ? 'Active Enterprise User' : 'Deactivated'}
                </span>
              </div>
            </div>

            {/* Salary Section */}
            <div>
              <div style={{ fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: '#000000', marginBottom: 12, borderBottom: '1px solid #000', paddingBottom: 4 }}>
                Compensation
              </div>
              <div style={{ fontSize: 20, fontWeight: 700, color: '#000000' }}>
                ₹{selectedEmp.basic_salary ? Number(selectedEmp.basic_salary).toLocaleString() : '60,000'} / month
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
