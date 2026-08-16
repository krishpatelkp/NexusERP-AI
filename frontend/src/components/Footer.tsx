const footerLinks = [
  {
    title: 'Products',
    links: ['HR Management', 'Attendance Tracker', 'Leave Studio', 'Payroll & Payslips', 'Inventory & Assets', 'Payments Hub'],
  },
  {
    title: 'Solutions',
    links: ['Enterprise Dashboard', 'Reports & Analytics', 'AI Copilot', 'Data Exchange Engine'],
  },
  {
    title: 'Resources',
    links: ['API Documentation', 'System Status', 'Security & Compliance', 'Release Notes'],
  },
  {
    title: 'Company',
    links: ['About NexusERP', 'Careers', 'Contact Sales', 'Privacy Policy'],
  },
]

export default function Footer() {
  return (
    <footer style={{ background: '#000', color: '#fff', padding: '80px 0 40px', borderTop: '1px solid #1a1a1a' }}>
      <div className="container">
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
          gap: 32,
          marginBottom: 64,
        }}>
          {/* Brand Column */}
          <div style={{ gridColumn: 'span 1' }}>
            <div style={{ display: 'flex', items: 'center', gap: 8, marginBottom: 16 }}>
              <svg width="24" height="24" viewBox="0 0 28 28" fill="none">
                <rect width="28" height="28" fill="white" />
                <text x="6" y="20" fill="black" fontSize="16" fontWeight="700" fontFamily="Inter">N</text>
              </svg>
              <span style={{ fontSize: 18, fontWeight: 700, letterSpacing: '-0.02em', color: '#fff' }}>NexusERP</span>
            </div>
            <p style={{ fontSize: 13, color: '#888', lineHeight: 1.6 }}>
              Intelligent Enterprise Resource Planning powered by AI. Unifying HR, Payroll, Attendance, Inventory, and Financial Analytics.
            </p>
          </div>

          {/* Links Columns */}
          {footerLinks.map((col) => (
            <div key={col.title}>
              <h4 style={{ fontSize: 14, fontWeight: 600, color: '#fff', marginBottom: 20, letterSpacing: '-0.01em' }}>{col.title}</h4>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: 12 }}>
                {col.links.map((link) => (
                  <li key={link}>
                    <a
                      href="#"
                      style={{ fontSize: 13, color: '#888', textDecoration: 'none', transition: 'color 0.2s ease' }}
                      onMouseEnter={(e) => (e.currentTarget.style.color = '#fff')}
                      onMouseLeave={(e) => (e.currentTarget.style.color = '#888')}
                    >
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom Bar */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          paddingTop: 32,
          borderTop: '1px solid #1a1a1a',
          fontSize: 12,
          color: '#666',
        }}>
          <div>© {new Date().getFullYear()} NexusERP-AI. All rights reserved.</div>
          <div style={{ display: 'flex', gap: 24 }}>
            <a href="#" style={{ color: '#666', textDecoration: 'none' }}>Privacy Policy</a>
            <a href="#" style={{ color: '#666', textDecoration: 'none' }}>Terms of Service</a>
            <a href="#" style={{ color: '#666', textDecoration: 'none' }}>Security</a>
          </div>
        </div>
      </div>
    </footer>
  )
}
