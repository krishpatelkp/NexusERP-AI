import React from 'react';
import { Card } from '../../components/ui/Card';
import { useAuth } from '../../context/AuthContext';
import { Building2, ShieldCheck, Mail } from 'lucide-react';
export default function SettingsPage() {
    const { user, isAdmin } = useAuth();
    return (<div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div>
        <h1 className="heading-lg" style={{ fontSize: 28, marginBottom: 4 }}>Company & Account Settings</h1>
        <p className="body-md" style={{ color: '#767676' }}>Manage organization profile, active role credentials, and preferences.</p>
      </div>

      <Card style={{ maxWidth: 640 }}>
        <h3 style={{ fontSize: 18, fontWeight: 700, margin: '0 0 20px', color: '#000' }}>Active Account Details</h3>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div>
            <label style={{ fontSize: 12, textTransform: 'uppercase', color: '#767676', fontWeight: 600 }}>Work Email</label>
            <div style={{ fontSize: 15, fontWeight: 600, color: '#000', marginTop: 4, display: 'flex', alignItems: 'center', gap: 8 }}>
              <Mail size={16}/> {user?.email}
            </div>
          </div>

          <div>
            <label style={{ fontSize: 12, textTransform: 'uppercase', color: '#767676', fontWeight: 600 }}>Organization Name</label>
            <div style={{ fontSize: 15, fontWeight: 600, color: '#000', marginTop: 4, display: 'flex', alignItems: 'center', gap: 8 }}>
              <Building2 size={16}/> {user?.company_name || 'Test Company'}
            </div>
          </div>

          <div>
            <label style={{ fontSize: 12, textTransform: 'uppercase', color: '#767676', fontWeight: 600 }}>Role Classification</label>
            <div style={{ fontSize: 15, fontWeight: 600, color: '#000', marginTop: 4, display: 'flex', alignItems: 'center', gap: 8 }}>
              <ShieldCheck size={16} color="#137333"/> {user?.role_name || (isAdmin ? 'Admin / HR' : 'Employee')}
            </div>
          </div>
        </div>
      </Card>
    </div>);
}
