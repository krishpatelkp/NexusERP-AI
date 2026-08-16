import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
export const ProtectedRoute = ({ children, requireAdmin }) => {
    const { isAuthenticated, isLoading, isAdmin } = useAuth();
    const location = useLocation();
    if (isLoading) {
        return (<div style={{
                minHeight: '100vh',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                background: '#F7F6F3',
                fontFamily: 'var(--font-body)',
            }}>
        <div style={{
                width: 40,
                height: 40,
                border: '3px solid #E6E6E6',
                borderTopColor: '#000',
                borderRadius: '50%',
                animation: 'spin 0.8s linear infinite',
                marginBottom: 16,
            }}/>
        <div style={{ fontSize: 14, color: '#767676', fontWeight: 500 }}>
          Authenticating Enterprise Session...
        </div>
      </div>);
    }
    if (!isAuthenticated) {
        return <Navigate to="/login" state={{ from: location }} replace/>;
    }
    if (requireAdmin && !isAdmin) {
        return <Navigate to="/dashboard" replace/>;
    }
    return children;
};
