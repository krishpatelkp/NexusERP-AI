/**
 * NexusERP-AI Frontend API Service
 * Connects React UI to Django REST Framework backend on http://127.0.0.1:8000/api/
 */
const API_BASE = import.meta.env.VITE_API_URL || '/api';
class APIService {
    token = localStorage.getItem('nexuserp_token');
    setToken(token) {
        this.token = token;
        localStorage.setItem('nexuserp_token', token);
    }
    getToken() {
        return this.token || localStorage.getItem('nexuserp_token');
    }
    clearToken() {
        this.token = null;
        localStorage.removeItem('nexuserp_token');
    }
    async ensureAuth() {
        if (!this.token) {
            this.token = localStorage.getItem('nexuserp_token');
        }
    }
    async request(endpoint, options = {}) {
        await this.ensureAuth();
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        let response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers,
        });
        if (response.status === 401) {
            this.clearToken();
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || errData.error || errData.message || 'Session expired. Please sign in again.');
        }
        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || errData.error || errData.message || `HTTP ${response.status}`);
        }
        return response.json();
    }

    /**
     * Login with user credentials
     */
    async login(email, password) {
        const res = await fetch(`${API_BASE}/auth/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
        });
        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.error || data.detail || 'Login failed');
        }
        const token = data.tokens?.access || data.access;
        const refresh = data.tokens?.refresh || data.refresh;
        if (token)
            this.setToken(token);
        if (refresh)
            localStorage.setItem('nexuserp_refresh_token', refresh);
        return data;
    }
    /**
     * Logout user
     */
    async logout() {
        try {
            const refreshToken = localStorage.getItem('nexuserp_refresh_token');
            await fetch(`${API_BASE}/auth/logout/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${this.token}`,
                },
                body: JSON.stringify({ refresh: refreshToken || '' }),
            });
        }
        finally {
            this.clearToken();
            localStorage.removeItem('nexuserp_refresh_token');
        }
    }
    /**
     * Register a new user account
     */
    async register(payload) {
        const res = await fetch(`${API_BASE}/auth/register/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (!res.ok) {
            const err = typeof data === 'object' ? Object.values(data).flat().join(' ') : 'Registration failed';
            throw new Error(err || 'Registration failed');
        }
        const token = data.tokens?.access || data.access;
        const refresh = data.tokens?.refresh || data.refresh;
        if (token)
            this.setToken(token);
        if (refresh)
            localStorage.setItem('nexuserp_refresh_token', refresh);
        return data;
    }
    /**
     * Get current user profile
     */

    async getMe() {
        return this.request('/auth/me/');
    }
    /**
     * Send question to NexusERP AI Engine
     */
    async sendAIChat(question) {
        return this.request('/ai/chat/', {
            method: 'POST',
            body: JSON.stringify({ question }),
        });
    }
    async getAIHealth() {
        return this.request('/ai/health/').catch(() => ({
            ollama_available: false,
            model: 'qwen3:8b',
            status: 'offline',
        }));
    }
    // ─────────────────────────────────────────
    // EMPLOYEES
    // ─────────────────────────────────────────
    async getEmployees() {
        const data = await this.request('/employees/employees/');
        return Array.isArray(data) ? data : data.results || [];
    }
    async createEmployee(payload) {
        return this.request('/employees/employees/', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
    }
    async getDepartments() {
        const data = await this.request('/employees/departments/');
        return Array.isArray(data) ? data : data.results || [];
    }
    async getDesignations() {
        const data = await this.request('/employees/designations/');
        return Array.isArray(data) ? data : data.results || [];
    }
    // ─────────────────────────────────────────
    // ATTENDANCE
    // ─────────────────────────────────────────
    async getAttendanceDashboard() {
        return this.request('/attendance/reports/dashboard/');
    }
    async checkIn(employeeId, remarks) {
        const payload = {
            check_in: new Date().toISOString(),
            remarks: remarks || '',
        };
        if (employeeId)
            payload.employee = employeeId;
        return this.request('/attendance/check-in/', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
    }
    async checkOut(employeeId, remarks) {
        const payload = {
            check_out: new Date().toISOString(),
            remarks: remarks || '',
        };
        if (employeeId)
            payload.employee = employeeId;
        return this.request('/attendance/check-out/', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
    }
    async getDailyAttendance(dateStr) {
        const url = dateStr
            ? `/attendance/reports/daily/?date=${dateStr}`
            : `/attendance/reports/daily/`;
        const data = await this.request(url);
        return Array.isArray(data) ? data : data.results || [];
    }
    async getEmployeeAttendanceHistory(employeeId) {
        try {
            const data = await this.request(`/reports/attendance/history/${employeeId}/`);
            return Array.isArray(data) ? data : data.results || [];
        }
        catch {
            return [];
        }
    }
    // ─────────────────────────────────────────
    // LEAVE
    // ─────────────────────────────────────────
    async getLeaveRequests() {
        const data = await this.request('/leave/requests/');
        return Array.isArray(data) ? data : data.results || [];
    }
    async getLeaveTypes() {
        try {
            const data = await this.request('/leave/types/');
            return Array.isArray(data) ? data : data.results || [];
        }
        catch {
            return [];
        }
    }
    async getLeaveBalances() {
        try {
            const data = await this.request('/leave/balances/');
            return Array.isArray(data) ? data : data.results || [];
        }
        catch {
            return [];
        }
    }
    async applyLeave(payload) {
        return this.request('/leave/requests/apply/', {
            method: 'POST',
            body: JSON.stringify({
                is_half_day: false,
                ...payload,
            }),
        });
    }
    async approveLeave(id, reason) {
        return this.request(`/leave/requests/${id}/approve/`, {
            method: 'POST',
            body: JSON.stringify({ approval_reason: reason || 'Approved by admin' }),
        });
    }
    async rejectLeave(id, reason) {
        return this.request(`/leave/requests/${id}/reject/`, {
            method: 'POST',
            body: JSON.stringify({ approval_reason: reason || 'Rejected by admin' }),
        });
    }
    // ─────────────────────────────────────────
    // PAYROLL & INVENTORY & PAYMENTS
    // ─────────────────────────────────────────
    async getPayslips() {
        const data = await this.request('/payroll/my-payslips/');
        return Array.isArray(data) ? data : data.results || [];
    }
    async getAssets() {
        const data = await this.request('/inventory/assets/');
        return Array.isArray(data) ? data : data.results || [];
    }
    async getPayments() {
        const data = await this.request('/payments/');
        return Array.isArray(data) ? data : data.results || [];
    }
    async getNotifications(unreadOnly = false) {
        const query = unreadOnly ? '?unread_only=true' : '';
        const data = await this.request(`/notifications/${query}`);
        return Array.isArray(data) ? data : data.results || [];
    }
    async getUnreadNotificationCount() {
        return this.request('/notifications/unread-count/').catch(() => ({ unread_count: 0 }));
    }
    async markNotificationRead(id) {
        return this.request(`/notifications/${id}/read/`, { method: 'PATCH' });
    }
    async markAllNotificationsRead() {
        return this.request('/notifications/mark-all-read/', { method: 'POST' });
    }
    async updateProfile(payload) {
        return this.request('/auth/me/update/', {
            method: 'PATCH',
            body: JSON.stringify(payload),
        });
    }
    async changePassword(oldPassword, newPassword, confirmPassword) {
        return this.request('/auth/change-password/', {
            method: 'POST',
            body: JSON.stringify({
                old_password: oldPassword,
                new_password: newPassword,
                confirm_password: confirmPassword,
                confirm_new_password: confirmPassword,
            }),
        });
    }
    // ─────────────────────────────────────────
    // REPORTS
    // ─────────────────────────────────────────
    async getEmployeeSummary() {
        return this.request('/reports/employees/summary/');
    }
    async getLeaveSummary() {
        return this.request('/reports/leave/summary/');
    }
    async getPayrollSummary() {
        return this.request('/reports/payroll/summary/');
    }
    async getInventorySummary() {
        return this.request('/reports/inventory/summary/');
    }
    async getPaymentSummary() {
        return this.request('/reports/payments/summary/');
    }
}
export const api = new APIService();
