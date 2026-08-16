/**
 * NexusERP-AI Frontend API Service
 * Connects React UI to Django REST Framework backend on http://127.0.0.1:8000/api/
 */

const API_BASE = '/api'

export interface UserProfile {
  id: number
  username: string
  email: string
  first_name?: string
  last_name?: string
  is_superuser?: boolean
  company_name?: string
  role_name?: string
  employee_id_number?: number
  role?: {
    id: number
    role_name: string
  }
}

export interface AIChatResponse {
  response: string
  used_tools?: string[]
  tool_results?: any[]
  success?: boolean
}

class APIService {
  private token: string | null = localStorage.getItem('nexuserp_token')

  setToken(token: string) {
    this.token = token
    localStorage.setItem('nexuserp_token', token)
  }

  getToken(): string | null {
    return this.token || localStorage.getItem('nexuserp_token')
  }

  clearToken() {
    this.token = null
    localStorage.removeItem('nexuserp_token')
  }

  private async ensureAuth(): Promise<void> {
    if (!this.token) {
      this.token = localStorage.getItem('nexuserp_token')
    }
    if (!this.token) {
      await this.autoLogin()
    }
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    await this.ensureAuth()

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    }

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`
    }

    let response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    })

    if (response.status === 401) {
      const reloginSuccess = await this.autoLogin()
      if (reloginSuccess) {
        headers['Authorization'] = `Bearer ${this.token}`
        response = await fetch(`${API_BASE}${endpoint}`, { ...options, headers })
      }
    }

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}))
      throw new Error(errData.detail || errData.error || errData.message || `HTTP ${response.status}`)
    }

    return response.json()
  }

  /**
   * Auto-login helper for seamless demo & API connection
   */
  async autoLogin(): Promise<boolean> {
    try {
      const res = await fetch(`${API_BASE}/auth/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'Krish@gmail.com',
          password: 'password123',
        }),
      })

      if (res.ok) {
        const data = await res.json()
        const token = data.tokens?.access || data.access
        if (token) {
          this.setToken(token)
          return true
        }
      }
    } catch {
      // silent fallback
    }
    return false
  }

  /**
   * Login with user credentials
   */
  async login(email: string, password: string): Promise<any> {
    const res = await fetch(`${API_BASE}/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    const data = await res.json()
    if (!res.ok) {
      throw new Error(data.error || data.detail || 'Login failed')
    }
    const token = data.tokens?.access || data.access
    const refresh = data.tokens?.refresh || data.refresh
    if (token) this.setToken(token)
    if (refresh) localStorage.setItem('nexuserp_refresh_token', refresh)
    return data
  }

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    try {
      const refreshToken = localStorage.getItem('nexuserp_refresh_token')
      await fetch(`${API_BASE}/auth/logout/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${this.token}`,
        },
        body: JSON.stringify({ refresh: refreshToken || '' }),
      })
    } finally {
      this.clearToken()
      localStorage.removeItem('nexuserp_refresh_token')
    }
  }

  /**
   * Register a new user account
   */
  async register(payload: { email: string; username: string; phone_number?: string; password: string; confirm_password: string }): Promise<any> {
    const res = await fetch(`${API_BASE}/auth/register/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const data = await res.json()
    if (!res.ok) {
      const err = typeof data === 'object' ? Object.values(data).flat().join(' ') : 'Registration failed'
      throw new Error(err || 'Registration failed')
    }
    const token = data.tokens?.access || data.access
    if (token) {
      this.setToken(token)
    }
    return data
  }

  /**
   * Get current user profile
   */
  async getMe(): Promise<UserProfile> {
    return this.request<UserProfile>('/auth/me/')
  }

  /**
   * Send question to NexusERP AI Engine
   */
  async sendAIChat(question: string): Promise<AIChatResponse> {
    return this.request<AIChatResponse>('/ai/chat/', {
      method: 'POST',
      body: JSON.stringify({ question }),
    })
  }

  // ─────────────────────────────────────────
  // EMPLOYEES
  // ─────────────────────────────────────────
  async getEmployees(): Promise<any[]> {
    const data = await this.request<any>('/employees/employees/')
    return Array.isArray(data) ? data : data.results || []
  }

  async createEmployee(payload: any): Promise<any> {
    return this.request<any>('/employees/employees/', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  }

  async getDepartments(): Promise<any[]> {
    const data = await this.request<any>('/employees/departments/')
    return Array.isArray(data) ? data : data.results || []
  }

  async getDesignations(): Promise<any[]> {
    const data = await this.request<any>('/employees/designations/')
    return Array.isArray(data) ? data : data.results || []
  }

  // ─────────────────────────────────────────
  // ATTENDANCE
  // ─────────────────────────────────────────
  async getAttendanceDashboard(): Promise<any> {
    return this.request<any>('/attendance/reports/dashboard/')
  }

  async checkIn(employeeId?: number, remarks?: string): Promise<any> {
    const payload: any = {
      check_in: new Date().toISOString(),
      remarks: remarks || '',
    }
    if (employeeId) payload.employee = employeeId
    return this.request<any>('/attendance/check-in/', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  }

  async checkOut(employeeId?: number, remarks?: string): Promise<any> {
    const payload: any = {
      check_out: new Date().toISOString(),
      remarks: remarks || '',
    }
    if (employeeId) payload.employee = employeeId
    return this.request<any>('/attendance/check-out/', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  }

  async getDailyAttendance(dateStr?: string): Promise<any> {
    const url = dateStr
      ? `/attendance/reports/daily/?date=${dateStr}`
      : `/attendance/reports/daily/`
    const data = await this.request<any>(url)
    return Array.isArray(data) ? data : data.results || []
  }

  async getEmployeeAttendanceHistory(employeeId: number): Promise<any[]> {
    try {
      const data = await this.request<any>(`/reports/attendance/history/${employeeId}/`)
      return Array.isArray(data) ? data : data.results || []
    } catch {
      return []
    }
  }

  // ─────────────────────────────────────────
  // LEAVE
  // ─────────────────────────────────────────
  async getLeaveRequests(): Promise<any[]> {
    const data = await this.request<any>('/leave/requests/')
    return Array.isArray(data) ? data : data.results || []
  }

  async getLeaveTypes(): Promise<any[]> {
    try {
      const data = await this.request<any>('/leave/types/')
      return Array.isArray(data) ? data : data.results || []
    } catch {
      return []
    }
  }

  async getLeaveBalances(): Promise<any[]> {
    try {
      const data = await this.request<any>('/leave/balances/')
      return Array.isArray(data) ? data : data.results || []
    } catch {
      return []
    }
  }

  async applyLeave(payload: { leave_type: number; start_date: string; end_date: string; reason: string; is_half_day?: boolean }): Promise<any> {
    return this.request<any>('/leave/requests/apply/', {
      method: 'POST',
      body: JSON.stringify({
        is_half_day: false,
        ...payload,
      }),
    })
  }

  async approveLeave(id: number, reason?: string): Promise<any> {
    return this.request<any>(`/leave/requests/${id}/approve/`, {
      method: 'POST',
      body: JSON.stringify({ approval_reason: reason || 'Approved by admin' }),
    })
  }

  async rejectLeave(id: number, reason?: string): Promise<any> {
    return this.request<any>(`/leave/requests/${id}/reject/`, {
      method: 'POST',
      body: JSON.stringify({ approval_reason: reason || 'Rejected by admin' }),
    })
  }

  // ─────────────────────────────────────────
  // PAYROLL & INVENTORY & PAYMENTS
  // ─────────────────────────────────────────
  async getPayslips(): Promise<any[]> {
    const data = await this.request<any>('/payroll/my-payslips/')
    return Array.isArray(data) ? data : data.results || []
  }

  async getAssets(): Promise<any[]> {
    const data = await this.request<any>('/inventory/assets/')
    return Array.isArray(data) ? data : data.results || []
  }

  async getPayments(): Promise<any[]> {
    const data = await this.request<any>('/payments/')
    return Array.isArray(data) ? data : data.results || []
  }

  async getNotifications(): Promise<any[]> {
    const data = await this.request<any>('/notifications/')
    return Array.isArray(data) ? data : data.results || []
  }

  // ─────────────────────────────────────────
  // REPORTS
  // ─────────────────────────────────────────
  async getEmployeeSummary(): Promise<any> {
    return this.request<any>('/reports/employees/summary/')
  }

  async getLeaveSummary(): Promise<any> {
    return this.request<any>('/reports/leave/summary/')
  }

  async getPayrollSummary(): Promise<any> {
    return this.request<any>('/reports/payroll/summary/')
  }

  async getInventorySummary(): Promise<any> {
    return this.request<any>('/reports/inventory/summary/')
  }

  async getPaymentSummary(): Promise<any> {
    return this.request<any>('/reports/payments/summary/')
  }
}

export const api = new APIService()
