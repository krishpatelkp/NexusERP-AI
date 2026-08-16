import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { AppLayout } from './components/AppLayout';
// Public Pages
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
// Protected Application Pages
import AdminDashboardPage from './pages/app/AdminDashboardPage';
import EmployeeDashboardPage from './pages/app/EmployeeDashboardPage';
import EmployeesPage from './pages/app/EmployeesPage';
import AttendancePage from './pages/app/AttendancePage';
import LeavePage from './pages/app/LeavePage';
import PayrollPage from './pages/app/PayrollPage';
import InventoryPage from './pages/app/InventoryPage';
import PaymentsPage from './pages/app/PaymentsPage';
import ReportsPage from './pages/app/ReportsPage';
import SettingsPage from './pages/app/SettingsPage';
import AICopilotPage from './pages/AICopilotPage';
function DashboardSwitcher() {
    const { isAdmin } = useAuth();
    return isAdmin ? <AdminDashboardPage /> : <EmployeeDashboardPage />;
}
export default function App() {
    return (<AuthProvider>
      <Router>
        <Routes>
          {/* Public Unauthenticated Routes */}
          <Route path="/" element={<LandingPage />}/>
          <Route path="/login" element={<LoginPage />}/>
          <Route path="/register" element={<RegisterPage />}/>

          {/* Protected Role-Based Application Routes wrapped in AppLayout */}
          <Route path="/dashboard" element={<ProtectedRoute>
                <AppLayout>
                  <DashboardSwitcher />
                </AppLayout>
              </ProtectedRoute>}/>
          <Route path="/employees" element={<ProtectedRoute requireAdmin>
                <AppLayout>
                  <EmployeesPage />
                </AppLayout>
              </ProtectedRoute>}/>
          <Route path="/attendance" element={<ProtectedRoute>
                <AppLayout>
                  <AttendancePage />
                </AppLayout>
              </ProtectedRoute>}/>
          <Route path="/leave" element={<ProtectedRoute>
                <AppLayout>
                  <LeavePage />
                </AppLayout>
              </ProtectedRoute>}/>
          <Route path="/payroll" element={<ProtectedRoute>
                <AppLayout>
                  <PayrollPage />
                </AppLayout>
              </ProtectedRoute>}/>
          <Route path="/inventory" element={<ProtectedRoute>
                <AppLayout>
                  <InventoryPage />
                </AppLayout>
              </ProtectedRoute>}/>
          <Route path="/payments" element={<ProtectedRoute>
                <AppLayout>
                  <PaymentsPage />
                </AppLayout>
              </ProtectedRoute>}/>
          <Route path="/reports" element={<ProtectedRoute requireAdmin>
                <AppLayout>
                  <ReportsPage />
                </AppLayout>
              </ProtectedRoute>}/>
          <Route path="/settings" element={<ProtectedRoute>
                <AppLayout>
                  <SettingsPage />
                </AppLayout>
              </ProtectedRoute>}/>
          <Route path="/ai" element={<ProtectedRoute>
                <AICopilotPage />
              </ProtectedRoute>}/>

          {/* Fallback Catch-All */}
          <Route path="*" element={<Navigate to="/" replace/>}/>
        </Routes>
      </Router>
    </AuthProvider>);
}
