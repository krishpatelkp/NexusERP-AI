import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ChevronDown, ArrowRight, Menu, X } from 'lucide-react';
import { api } from '../services/api';
const products = [
    { label: 'HR & Employee Directory', href: '/dashboard' },
    { label: 'Attendance Tracker', href: '/dashboard' },
    { label: 'Leave Studio', href: '/dashboard' },
    { label: 'Payroll & Payslips', href: '/dashboard' },
    { label: 'Inventory & Assets', href: '/dashboard' },
    { label: 'Payments Hub', href: '/dashboard' },
];
const solutions = [
    { label: 'Enterprise Dashboard', href: '/dashboard' },
    { label: 'Company Reports Engine', href: '/dashboard' },
    { label: 'AI Copilot Engine', href: '/ai' },
];
export default function Navbar() {
    const [scrolled, setScrolled] = useState(false);
    const [mobileOpen, setMobileOpen] = useState(false);
    const [dropdown, setDropdown] = useState(null);
    const [token, setToken] = useState(api.getToken());
    const navigate = useNavigate();
    useEffect(() => {
        const handler = () => setScrolled(window.scrollY > 10);
        window.addEventListener('scroll', handler, { passive: true });
        return () => window.removeEventListener('scroll', handler);
    }, []);
    return (<header style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            zIndex: 100,
            height: 72,
            display: 'flex',
            alignItems: 'center',
            background: scrolled ? 'rgba(255,255,255,0.95)' : 'transparent',
            backdropFilter: scrolled ? 'blur(12px)' : 'none',
            borderBottom: scrolled ? '1px solid #e6e6e6' : '1px solid transparent',
            transition: 'all 0.4s ease',
        }}>
      <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        {/* Logo */}
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 8, textDecoration: 'none', color: '#000' }}>
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <rect width="28" height="28" fill="black"/>
            <text x="6" y="20" fill="white" fontSize="16" fontWeight="700" fontFamily="Inter">N</text>
          </svg>
          <span style={{ fontSize: 18, fontWeight: 700, letterSpacing: '-0.02em' }}>NexusERP</span>
        </Link>

        {/* Desktop Nav */}
        <nav style={{ display: 'flex', alignItems: 'center', gap: 4 }} className="hidden lg:flex">
          {/* Products Dropdown */}
          <div style={{ position: 'relative' }} onMouseEnter={() => setDropdown('products')} onMouseLeave={() => setDropdown(null)}>
            <button style={{
            display: 'flex', alignItems: 'center', gap: 4,
            padding: '8px 16px', background: 'none', border: 'none',
            fontSize: 14, fontWeight: 500, cursor: 'pointer', color: '#000',
            fontFamily: 'var(--font-body)',
        }}>
              Modules
              <ChevronDown size={14} style={{
            transition: 'transform 0.3s ease',
            transform: dropdown === 'products' ? 'rotate(180deg)' : 'rotate(0)',
        }}/>
            </button>
            <div style={{
            position: 'absolute', top: '100%', left: '50%',
            transform: dropdown === 'products' ? 'translate(-50%, 0)' : 'translate(-50%, -8px)',
            opacity: dropdown === 'products' ? 1 : 0,
            pointerEvents: dropdown === 'products' ? 'auto' : 'none',
            transition: 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
            paddingTop: 8,
        }}>
              <div style={{
            background: '#fff', border: '1px solid #e6e6e6',
            padding: 8, minWidth: 220, boxShadow: '0 8px 30px rgba(0,0,0,0.08)',
        }}>
                {products.map((item) => (<Link key={item.label} to={item.href} style={{
                display: 'block', padding: '10px 16px', fontSize: 14, color: '#000',
                transition: 'background 0.2s', fontWeight: 400, textDecoration: 'none',
            }} onMouseEnter={e => (e.currentTarget.style.background = '#f7f6f3')} onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}>
                    {item.label}
                  </Link>))}
              </div>
            </div>
          </div>

          {/* Solutions Dropdown */}
          <div style={{ position: 'relative' }} onMouseEnter={() => setDropdown('solutions')} onMouseLeave={() => setDropdown(null)}>
            <button style={{
            display: 'flex', alignItems: 'center', gap: 4,
            padding: '8px 16px', background: 'none', border: 'none',
            fontSize: 14, fontWeight: 500, cursor: 'pointer', color: '#000',
            fontFamily: 'var(--font-body)',
        }}>
              Solutions
              <ChevronDown size={14} style={{
            transition: 'transform 0.3s ease',
            transform: dropdown === 'solutions' ? 'rotate(180deg)' : 'rotate(0)',
        }}/>
            </button>
            <div style={{
            position: 'absolute', top: '100%', left: '50%',
            transform: dropdown === 'solutions' ? 'translate(-50%, 0)' : 'translate(-50%, -8px)',
            opacity: dropdown === 'solutions' ? 1 : 0,
            pointerEvents: dropdown === 'solutions' ? 'auto' : 'none',
            transition: 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
            paddingTop: 8,
        }}>
              <div style={{
            background: '#fff', border: '1px solid #e6e6e6',
            padding: 8, minWidth: 220, boxShadow: '0 8px 30px rgba(0,0,0,0.08)',
        }}>
                {solutions.map((item) => (<Link key={item.label} to={item.href} style={{
                display: 'block', padding: '10px 16px', fontSize: 14, color: '#000',
                transition: 'background 0.2s', fontWeight: 400, textDecoration: 'none',
            }} onMouseEnter={e => (e.currentTarget.style.background = '#f7f6f3')} onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}>
                    {item.label}
                  </Link>))}
              </div>
            </div>
          </div>

          <Link to="/ai" style={{ padding: '8px 16px', fontSize: 14, fontWeight: 500, color: '#000', textDecoration: 'none' }}>AI Copilot</Link>
        </nav>

        {/* Right CTA Actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }} className="hidden lg:flex">
          <Link to="/login" style={{ fontSize: 14, fontWeight: 600, color: '#000', textDecoration: 'none', padding: '8px 16px' }}>
            Log In
          </Link>
          <Link to="/register" className="btn-primary" style={{ height: 40, padding: '0 20px', fontSize: 13, textDecoration: 'none' }}>
            Register Company <ArrowRight size={14}/>
          </Link>
        </div>

        {/* Mobile Hamburger */}
        <button className="lg:hidden" onClick={() => setMobileOpen(!mobileOpen)} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 8 }}>
          {mobileOpen ? <X size={24}/> : <Menu size={24}/>}
        </button>
      </div>

      {/* Mobile Menu */}
      {mobileOpen && (<div style={{
                position: 'absolute', top: 72, left: 0, right: 0,
                background: '#fff', borderBottom: '1px solid #e6e6e6',
                padding: '16px 24px',
            }}>
          <Link to="/login" onClick={() => setMobileOpen(false)} style={{ display: 'block', padding: '12px 0', fontSize: 15, fontWeight: 600, borderBottom: '1px solid #f0f0f0', textDecoration: 'none', color: '#000' }}>
            Log In
          </Link>
          <Link to="/register" onClick={() => setMobileOpen(false)} style={{ display: 'block', padding: '12px 0', fontSize: 15, fontWeight: 600, borderBottom: '1px solid #f0f0f0', textDecoration: 'none', color: '#000' }}>
            Register Company
          </Link>
          <Link to="/ai" onClick={() => setMobileOpen(false)} style={{ display: 'block', padding: '12px 0', fontSize: 15, borderBottom: '1px solid #f0f0f0', textDecoration: 'none', color: '#000' }}>
            AI Copilot
          </Link>
        </div>)}
    </header>);
}
