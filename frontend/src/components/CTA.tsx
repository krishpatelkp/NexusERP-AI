import { FadeIn } from './animations'
import { ArrowRight } from 'lucide-react'

export default function CTA() {
  return (
    <section style={{
      background: '#F7F6F3',
      padding: '140px 0',
      textAlign: 'center',
    }}>
      <div className="container">
        <FadeIn>
          <h2 className="heading-lg" style={{ marginBottom: 24, maxWidth: 700, margin: '0 auto 24px' }}>
            Ready to run your business smarter?
          </h2>
        </FadeIn>

        <FadeIn delay={100}>
          <p className="body-lg" style={{ maxWidth: 500, margin: '0 auto 40px' }}>
            Join the next generation of enterprise management. NexusERP-AI brings intelligence to every department.
          </p>
        </FadeIn>

        <FadeIn delay={200}>
          <div style={{ display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
            <a href="#explorer" className="btn-primary">
              Get Started — It's Free <ArrowRight size={16} />
            </a>
            <a href="#features" className="btn-secondary">
              Explore Features
            </a>
          </div>
        </FadeIn>
      </div>
    </section>
  )
}
