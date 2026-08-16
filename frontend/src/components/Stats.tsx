import { FadeIn } from './animations'

const stats = [
  { value: '20', label: 'AI Features' },
  { value: '98%', label: 'System Accuracy' },
  { value: '9', label: 'Core Modules' },
  { value: '100%', label: 'Audit Compliance' },
]

export default function Stats() {
  return (
    <section style={{ background: '#000', color: '#fff', padding: '100px 0' }}>
      <div className="container">
        <FadeIn>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
            gap: 32,
            textAlign: 'center',
          }}>
            {stats.map((s) => (
              <div key={s.label}>
                <div style={{
                  fontSize: 'clamp(40px, 6vw, 64px)',
                  fontWeight: 700,
                  letterSpacing: '-0.03em',
                  lineHeight: 1,
                  marginBottom: 8,
                  fontFamily: 'var(--font-display)',
                }}>
                  {s.value}
                </div>
                <div style={{ fontSize: 14, color: '#999', fontWeight: 400 }}>{s.label}</div>
              </div>
            ))}
          </div>
        </FadeIn>
      </div>
    </section>
  )
}
