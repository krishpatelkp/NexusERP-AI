import { useState } from 'react'
import { FadeIn } from './animations'
import { Bot, Send, Sparkles, Loader2 } from 'lucide-react'
import { api } from '../services/api'

interface Message {
  role: 'user' | 'ai'
  text: string
  tool?: string
  isError?: boolean
}

const initialMessages: Message[] = [
  {
    role: 'user',
    text: 'Who is absent today?',
  },
  {
    role: 'ai',
    text: 'Today <strong>0 of 105 employees</strong> are absent (0.0%). All registered employees are present.',
  },
  {
    role: 'user',
    text: 'Show payroll summary for this year',
  },
  {
    role: 'ai',
    text: 'Total net payroll for the current year is <strong>₹85,000.00</strong> across <strong>1 active payroll cycle</strong>.',
  },
]

const quickPrompts = [
  'Who is absent today?',
  'Show payroll summary',
  'Employee count by department',
  'Pending leave requests',
]

export default function AICopilot() {
  const [messages, setMessages] = useState<Message[]>(initialMessages)
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSend = async (queryText?: string) => {
    const textToSend = queryText || input
    if (!textToSend.trim() || loading) return

    const userMsg: Message = { role: 'user', text: textToSend }
    setMessages((prev) => [...prev, userMsg])
    if (!queryText) setInput('')
    setLoading(true)

    try {
      const res = await api.sendAIChat(textToSend)
      const aiMsg: Message = {
        role: 'ai',
        text: res.response || "I couldn't generate a response.",
      }
      setMessages((prev) => [...prev, aiMsg])
    } catch (err: any) {
      const errorMsg: Message = {
        role: 'ai',
        text: err.message || 'Error connecting to NexusERP AI engine.',
        isError: true,
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setLoading(false)
    }
  }

  return (
    <section id="ai" style={{ background: '#000', color: '#fff', padding: '140px 0' }}>
      <div className="container">
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: 48,
          alignItems: 'center',
        }}>
          {/* Left Description */}
          <div>
            <FadeIn>
              <p className="label" style={{ color: '#999', marginBottom: 16 }}>AI Copilot</p>
              <h2 style={{
                fontSize: 'clamp(36px, 5vw, 56px)',
                fontWeight: 600,
                lineHeight: 1.1,
                letterSpacing: '-0.02em',
                marginBottom: 24,
                fontFamily: 'var(--font-display)',
              }}>
                Ask your data anything
              </h2>
              <p style={{ fontSize: 18, lineHeight: 1.6, color: '#999', marginBottom: 40, maxWidth: 480 }}>
                Ask instant questions about employees, attendance, payroll, and inventory in plain language.
              </p>
            </FadeIn>

            {/* Quick prompts */}
            <FadeIn delay={200}>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {quickPrompts.map((prompt) => (
                  <button
                    key={prompt}
                    disabled={loading}
                    onClick={() => {
                      setInput(prompt)
                      handleSend(prompt)
                    }}
                    style={{
                      padding: '8px 14px',
                      fontSize: 13,
                      background: 'rgba(255,255,255,0.08)',
                      border: '1px solid rgba(255,255,255,0.15)',
                      color: '#ccc',
                      cursor: loading ? 'not-allowed' : 'pointer',
                      transition: 'all 0.3s ease',
                      fontFamily: 'var(--font-body)',
                      display: 'flex', alignItems: 'center', gap: 6,
                    }}
                    onMouseEnter={e => { e.currentTarget.style.borderColor = '#fff'; e.currentTarget.style.color = '#fff' }}
                    onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.15)'; e.currentTarget.style.color = '#ccc' }}
                  >
                    <Sparkles size={12} />{prompt}
                  </button>
                ))}
              </div>
            </FadeIn>
          </div>

          {/* Right — Chat Box */}
          <FadeIn delay={100}>
            <div style={{
              background: '#1A1A1A',
              border: '1px solid rgba(255,255,255,0.1)',
              overflow: 'hidden',
            }}>
              {/* Header */}
              <div style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '16px 20px',
                borderBottom: '1px solid rgba(255,255,255,0.08)',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div style={{
                    width: 36, height: 36,
                    background: 'rgba(255,255,255,0.08)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                  }}>
                    <Bot size={18} />
                  </div>
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 600 }}>NexusERP Copilot</div>
                    <div style={{ fontSize: 12, color: '#28C840', display: 'flex', alignItems: 'center', gap: 4 }}>
                      <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#28C840' }} />
                      Online
                    </div>
                  </div>
                </div>
              </div>

              {/* Chat Messages */}
              <div style={{ padding: 20, minHeight: 320, maxHeight: 380, overflowY: 'auto' }}>
                {messages.map((msg, i) => (
                  <div key={i} style={{
                    display: 'flex',
                    justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                    marginBottom: 16,
                  }}>
                    <div style={{
                      maxWidth: '85%',
                      padding: '12px 16px',
                      fontSize: 14,
                      lineHeight: 1.5,
                      background: msg.role === 'user' ? 'rgba(255,255,255,0.12)' : 'rgba(255,255,255,0.05)',
                      borderLeft: msg.isError ? '3px solid #FF5F57' : undefined,
                    }}>
                      <div dangerouslySetInnerHTML={{ __html: msg.text }} />
                    </div>
                  </div>
                ))}
                {loading && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#999', fontSize: 13 }}>
                    <Loader2 size={16} className="animate-spin" />
                    NexusERP AI is searching your enterprise data...
                  </div>
                )}
              </div>

              {/* Chat Input */}
              <div style={{
                display: 'flex', gap: 8,
                padding: '16px 20px',
                borderTop: '1px solid rgba(255,255,255,0.08)',
              }}>
                <input
                  type="text"
                  value={input}
                  disabled={loading}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && handleSend()}
                  placeholder="Ask NexusERP AI (e.g. 'Who is absent today?')"
                  style={{
                    flex: 1, padding: '10px 14px',
                    background: 'rgba(255,255,255,0.06)',
                    border: '1px solid rgba(255,255,255,0.1)',
                    color: '#fff', fontSize: 14,
                    outline: 'none',
                    fontFamily: 'var(--font-body)',
                  }}
                />
                <button
                  onClick={() => handleSend()}
                  disabled={loading}
                  style={{
                    width: 44, height: 44,
                    background: '#fff', border: 'none',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    cursor: loading ? 'not-allowed' : 'pointer',
                  }}
                >
                  {loading ? <Loader2 size={16} color="#000" className="animate-spin" /> : <Send size={16} color="#000" />}
                </button>
              </div>
            </div>
          </FadeIn>
        </div>
      </div>
    </section>
  )
}
