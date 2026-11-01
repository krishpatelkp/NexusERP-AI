import React, { useState } from 'react';
import { Card } from '../../components/ui/Card';
import { useAuth } from '../../context/AuthContext';
import { api } from '../../services/api';
import { Building2, ShieldCheck, Mail, User, Phone, KeyRound, CheckCircle2, AlertCircle, Calendar, Hash } from 'lucide-react';

export default function SettingsPage() {
    const { user, isAdmin, refreshUser } = useAuth();

    // Profile form state
    const [username, setUsername] = useState(user?.username || '');
    const [phoneNumber, setPhoneNumber] = useState(user?.phone_number || '');
    const [profileSaving, setProfileSaving] = useState(false);
    const [profileMsg, setProfileMsg] = useState(null);

    // Password form state
    const [oldPassword, setOldPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [passwordSaving, setPasswordSaving] = useState(false);
    const [passwordMsg, setPasswordMsg] = useState(null);

    const handleUpdateProfile = async (e) => {
        e.preventDefault();
        setProfileSaving(true);
        setProfileMsg(null);
        try {
            const res = await api.updateProfile({
                username: username.trim(),
                phone_number: phoneNumber.trim(),
            });
            setProfileMsg({ type: 'success', text: res?.message || 'Profile updated successfully.' });
            if (refreshUser) await refreshUser();
        } catch (err) {
            setProfileMsg({ type: 'error', text: err?.message || 'Failed to update profile.' });
        } finally {
            setProfileSaving(false);
        }
    };

    const handleChangePassword = async (e) => {
        e.preventDefault();
        if (newPassword !== confirmPassword) {
            setPasswordMsg({ type: 'error', text: 'New passwords do not match.' });
            return;
        }
        if (newPassword.length < 8) {
            setPasswordMsg({ type: 'error', text: 'New password must be at least 8 characters long.' });
            return;
        }
        setPasswordSaving(true);
        setPasswordMsg(null);
        try {
            const res = await api.changePassword(oldPassword, newPassword, confirmPassword);
            setPasswordMsg({ type: 'success', text: res?.message || 'Password updated successfully.' });
            setOldPassword('');
            setNewPassword('');
            setConfirmPassword('');
        } catch (err) {
            setPasswordMsg({ type: 'error', text: err?.message || 'Failed to change password.' });
        } finally {
            setPasswordSaving(false);
        }
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 28, maxWidth: 960 }}>
            <div>
                <h1 className="heading-lg" style={{ fontSize: 28, marginBottom: 4 }}>Company & Account Settings</h1>
                <p className="body-md" style={{ color: '#767676' }}>
                    Manage enterprise credentials, security settings, and profile information.
                </p>
            </div>

            {/* Overview Card */}
            <Card>
                <h3 style={{ fontSize: 17, fontWeight: 700, margin: '0 0 16px', color: '#111' }}>
                    Active Organization & Identity
                </h3>
                
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
                    gap: 20,
                    background: '#fafafa',
                    padding: 20,
                    borderRadius: 6,
                    border: '1px solid #ebebeb'
                }}>
                    <div>
                        <div style={{ fontSize: 11, textTransform: 'uppercase', color: '#767676', fontWeight: 700, letterSpacing: '0.04em' }}>
                            Organization
                        </div>
                        <div style={{ fontSize: 15, fontWeight: 600, color: '#000', marginTop: 6, display: 'flex', alignItems: 'center', gap: 8 }}>
                            <Building2 size={16} color="#000" />
                            <span>{user?.company_name || 'Enterprise Workspace'}</span>
                        </div>
                    </div>

                    <div>
                        <div style={{ fontSize: 11, textTransform: 'uppercase', color: '#767676', fontWeight: 700, letterSpacing: '0.04em' }}>
                            Role & Authority
                        </div>
                        <div style={{ fontSize: 15, fontWeight: 600, color: '#000', marginTop: 6, display: 'flex', alignItems: 'center', gap: 8 }}>
                            <ShieldCheck size={16} color="#15803d" />
                            <span>{user?.role_name || (isAdmin ? 'Admin' : 'Employee')}</span>
                            {user?.role_code && (
                                <span style={{
                                    fontSize: 10,
                                    fontWeight: 700,
                                    padding: '2px 6px',
                                    background: '#e0f2fe',
                                    color: '#0369a1',
                                    borderRadius: 4
                                }}>
                                    {user.role_code}
                                </span>
                            )}
                        </div>
                    </div>

                    <div>
                        <div style={{ fontSize: 11, textTransform: 'uppercase', color: '#767676', fontWeight: 700, letterSpacing: '0.04em' }}>
                            Employee Code
                        </div>
                        <div style={{ fontSize: 15, fontWeight: 600, color: '#000', marginTop: 6, display: 'flex', alignItems: 'center', gap: 8 }}>
                            <Hash size={16} color="#6b7280" />
                            <span>{user?.employee_code || (user?.employee_id ? `EMP-${user.employee_id}` : 'Workspace Founder')}</span>
                        </div>
                    </div>

                    <div>
                        <div style={{ fontSize: 11, textTransform: 'uppercase', color: '#767676', fontWeight: 700, letterSpacing: '0.04em' }}>
                            Account Status
                        </div>
                        <div style={{ fontSize: 14, fontWeight: 600, color: '#15803d', marginTop: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
                            <CheckCircle2 size={16} color="#15803d" />
                            <span>Active & Verified</span>
                        </div>
                    </div>
                </div>
            </Card>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: 24 }}>
                {/* Profile Form */}
                <Card>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
                        <User size={18} color="#000" />
                        <h3 style={{ fontSize: 16, fontWeight: 700, margin: 0, color: '#111' }}>
                            Personal Profile
                        </h3>
                    </div>

                    {profileMsg && (
                        <div style={{
                            padding: '10px 14px',
                            borderRadius: 6,
                            marginBottom: 16,
                            fontSize: 13,
                            display: 'flex',
                            alignItems: 'center',
                            gap: 8,
                            background: profileMsg.type === 'success' ? '#f0fdf4' : '#fef2f2',
                            color: profileMsg.type === 'success' ? '#15803d' : '#b91c1c',
                            border: `1px solid ${profileMsg.type === 'success' ? '#bbf7d0' : '#fecaca'}`
                        }}>
                            {profileMsg.type === 'success' ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
                            {profileMsg.text}
                        </div>
                    )}

                    <form onSubmit={handleUpdateProfile} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                        <div>
                            <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#4b5563', marginBottom: 4 }}>
                                Work Email (Locked)
                            </label>
                            <input
                                type="email"
                                value={user?.email || ''}
                                disabled
                                style={{
                                    width: '100%',
                                    padding: '9px 12px',
                                    borderRadius: 6,
                                    border: '1px solid #d1d5db',
                                    background: '#f3f4f6',
                                    color: '#6b7280',
                                    fontSize: 14,
                                    boxSizing: 'border-box'
                                }}
                            />
                        </div>

                        <div>
                            <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#4b5563', marginBottom: 4 }}>
                                Username
                            </label>
                            <input
                                type="text"
                                required
                                minLength={5}
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                style={{
                                    width: '100%',
                                    padding: '9px 12px',
                                    borderRadius: 6,
                                    border: '1px solid #d1d5db',
                                    fontSize: 14,
                                    boxSizing: 'border-box'
                                }}
                            />
                        </div>

                        <div>
                            <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#4b5563', marginBottom: 4 }}>
                                Phone Number
                            </label>
                            <input
                                type="tel"
                                value={phoneNumber}
                                onChange={(e) => setPhoneNumber(e.target.value)}
                                placeholder="+91 98765 43210"
                                style={{
                                    width: '100%',
                                    padding: '9px 12px',
                                    borderRadius: 6,
                                    border: '1px solid #d1d5db',
                                    fontSize: 14,
                                    boxSizing: 'border-box'
                                }}
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={profileSaving}
                            style={{
                                marginTop: 8,
                                padding: '10px 16px',
                                background: '#000000',
                                color: '#ffffff',
                                border: 'none',
                                borderRadius: 6,
                                fontSize: 13,
                                fontWeight: 600,
                                cursor: profileSaving ? 'not-allowed' : 'pointer',
                                opacity: profileSaving ? 0.7 : 1,
                                transition: 'opacity 0.15s ease'
                            }}
                        >
                            {profileSaving ? 'Saving Changes...' : 'Save Profile Changes'}
                        </button>
                    </form>
                </Card>

                {/* Password / Security Form */}
                <Card>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
                        <KeyRound size={18} color="#000" />
                        <h3 style={{ fontSize: 16, fontWeight: 700, margin: 0, color: '#111' }}>
                            Security & Credentials
                        </h3>
                    </div>

                    {passwordMsg && (
                        <div style={{
                            padding: '10px 14px',
                            borderRadius: 6,
                            marginBottom: 16,
                            fontSize: 13,
                            display: 'flex',
                            alignItems: 'center',
                            gap: 8,
                            background: passwordMsg.type === 'success' ? '#f0fdf4' : '#fef2f2',
                            color: passwordMsg.type === 'success' ? '#15803d' : '#b91c1c',
                            border: `1px solid ${passwordMsg.type === 'success' ? '#bbf7d0' : '#fecaca'}`
                        }}>
                            {passwordMsg.type === 'success' ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
                            {passwordMsg.text}
                        </div>
                    )}

                    <form onSubmit={handleChangePassword} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                        <div>
                            <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#4b5563', marginBottom: 4 }}>
                                Current Password
                            </label>
                            <input
                                type="password"
                                required
                                value={oldPassword}
                                onChange={(e) => setOldPassword(e.target.value)}
                                style={{
                                    width: '100%',
                                    padding: '9px 12px',
                                    borderRadius: 6,
                                    border: '1px solid #d1d5db',
                                    fontSize: 14,
                                    boxSizing: 'border-box'
                                }}
                            />
                        </div>

                        <div>
                            <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#4b5563', marginBottom: 4 }}>
                                New Password
                            </label>
                            <input
                                type="password"
                                required
                                minLength={8}
                                value={newPassword}
                                onChange={(e) => setNewPassword(e.target.value)}
                                style={{
                                    width: '100%',
                                    padding: '9px 12px',
                                    borderRadius: 6,
                                    border: '1px solid #d1d5db',
                                    fontSize: 14,
                                    boxSizing: 'border-box'
                                }}
                            />
                        </div>

                        <div>
                            <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#4b5563', marginBottom: 4 }}>
                                Confirm New Password
                            </label>
                            <input
                                type="password"
                                required
                                minLength={8}
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                style={{
                                    width: '100%',
                                    padding: '9px 12px',
                                    borderRadius: 6,
                                    border: '1px solid #d1d5db',
                                    fontSize: 14,
                                    boxSizing: 'border-box'
                                }}
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={passwordSaving}
                            style={{
                                marginTop: 8,
                                padding: '10px 16px',
                                background: '#111827',
                                color: '#ffffff',
                                border: 'none',
                                borderRadius: 6,
                                fontSize: 13,
                                fontWeight: 600,
                                cursor: passwordSaving ? 'not-allowed' : 'pointer',
                                opacity: passwordSaving ? 0.7 : 1,
                                transition: 'opacity 0.15s ease'
                            }}
                        >
                            {passwordSaving ? 'Updating Password...' : 'Update Password'}
                        </button>
                    </form>
                </Card>
            </div>
        </div>
    );
}
