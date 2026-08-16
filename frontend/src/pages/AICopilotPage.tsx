import React, { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import { useAuth } from '../context/AuthContext'
import { Bot, Send, ArrowLeft, Plus, MessageSquare, Terminal, ShieldCheck, Sparkles, CheckCircle2 } from 'lucide-react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  tools_used?: string[]
}

export default function AICopilotPage() {
  const { isAdmin } = useAuth()

  // State
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [aiStatus, setAiStatus] = useState<'online' | 'standby'>('online')
  const [conversations, setConversations] = useState<{ id: string; title: string }[]>([
    { id: 'c1', title: 'Enterprise Operations' },
  ])
  const [activeConvId, setActiveConvId] = useState('c1')

  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  // Suggested prompts
  const adminPrompts = [
    'How many employees are active?',
    "What is today's attendance?",
    'Show pending leave requests',
    'What is our payroll cost this year?',
    'How many assets are assigned?',
  ]

  const employeePrompts = [
    'What is my leave balance?',
    'Show my last payslip',
    'What assets do I have?',
    'How many days have I been absent this month?',
  ]

  const suggestedPrompts = isAdmin ? adminPrompts : employeePrompts

  const handleSend = async (promptText?: string) => {
    const text = promptText || input
    if (!text.trim() || loading) return

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text.trim(),
    }

    setMessages((prev) => [...prev, userMsg])
    if (!promptText) setInput('')
    setLoading(true)

    try {
      const res = await api.sendAIChat(text.trim())
      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: res.response || 'Enterprise data process complete.',
        tools_used: res.used_tools || (res as any).tools_used || [],
      }
      setMessages((prev) => [...prev, aiMsg])
    } catch (err: any) {
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Error executing AI query: ${err.message || 'Server connection timeout.'}`,
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setLoading(false)
    }
  }

  const handleNewChat = () => {
    const newId = `c${Date.now()}`
    setConversations((prev) => [{ id: newId, title: 'New Conversation' }, ...prev])
    setActiveConvId(newId)
    setMessages([])
  }

  return (
    <div style={{ height: '100vh', display: 'flex', background: '#000000', color: '#ffffff', fontFamily: 'var(--font-body)', overflow: 'hidden' }}>
      {/* LEFT SIDEBAR — Conversation History (240px wide) */}
      <aside style={{
        width: 240,
        background: '#0a0a0a',
        borderRight: '1px solid rgba(255,255,255,0.1)',
        display: 'flex',
        flexDirection: 'column',
        flexShrink: 0,
      }}>
        {/* Top Header & Back to Dashboard Link */}
        <div style={{ padding: '20px 16px', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
          <Link
            to="/dashboard"
            style={{
              display: 'inline-flex', alignItems: 'center', gap: 6,
              fontSize: 12, fontWeight: 600, color: '#999999', textDecoration: 'none', marginBottom: 16,
            }}
          >
            <ArrowLeft size={14} /> Back to Dashboard
          </Link>

          <button
            onClick={handleNewChat}
            style={{
              width: '100%', padding: '10px 14px', background: '#ffffff', color: '#000000',
              border: 'none', fontSize: 13, fontWeight: 700, cursor: 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, borderRadius: 0,
            }}
          >
            <Plus size={16} /> New Chat Session
          </button>
        </div>

        {/* History Item List */}
        <div style={{ flex: 1, padding: 12, display: 'flex', flexDirection: 'column', gap: 4, overflowY: 'auto' }}>
          <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: '#666666', padding: '8px 8px 4px' }}>
            Chat Sessions
          </div>
          {conversations.map((c) => (
            <button
              key={c.id}
              onClick={() => setActiveConvId(c.id)}
              style={{
                width: '100%', padding: '10px 12px', background: activeConvId === c.id ? 'rgba(255,255,255,0.1)' : 'transparent',
                color: activeConvId === c.id ? '#ffffff' : '#888888', border: 'none',
                textAlign: 'left', fontSize: 13, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8,
              }}
            >
              <MessageSquare size={14} />
              <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{c.title}</span>
            </button>
          ))}
        </div>

        {/* Footer info */}
        <div style={{ padding: 16, borderTop: '1px solid rgba(255,255,255,0.1)', fontSize: 11, color: '#666666' }}>
          NexusERP Agentic Engine v2.4
        </div>
      </aside>

      {/* RIGHT MAIN CHAT AREA */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0, background: '#000000' }}>
        {/* Header */}
        <header style={{
          height: 72, borderBottom: '1px solid rgba(255,255,255,0.1)', padding: '0 32px',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexShrink: 0,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ width: 32, height: 32, background: '#ffffff', color: '#000000', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700 }}>
              <Bot size={18} />
            </div>
            <div>
              <div style={{ fontSize: 16, fontWeight: 700, letterSpacing: '-0.02em', color: '#ffffff' }}>
                NexusERP AI Copilot
              </div>
              <div style={{ fontSize: 11, color: '#888888' }}>
                Enterprise Database Neural Assistant
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            {/* Model Name Badge */}
            <span style={{ padding: '3px 8px', background: 'rgba(255,255,255,0.1)', color: '#cccccc', fontSize: 11, fontWeight: 600, fontFamily: 'monospace' }}>
              Model: qwen3:8b
            </span>

            {/* Online Status Indicator */}
            <span style={{
              padding: '3px 10px', background: '#137333', color: '#ffffff',
              fontSize: 11, fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: 6,
            }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#28C840' }} />
              ONLINE
            </span>
          </div>
        </header>

        {/* Message Container Area */}
        <div style={{ flex: 1, padding: 32, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* Empty Chat State: Suggested Questions */}
          {messages.length === 0 && (
            <div style={{ maxWidth: 640, margin: '40px auto', textAlign: 'center' }}>
              <div style={{
                width: 56, height: 56, background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)',
                display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: 20,
              }}>
                <Sparkles size={28} color="#ffffff" />
              </div>
              <h2 style={{ fontSize: 24, fontWeight: 700, marginBottom: 8, color: '#ffffff' }}>
                Ask NexusERP AI Anything
              </h2>
              <p style={{ fontSize: 14, color: '#888888', marginBottom: 32 }}>
                Query workforce headcount, attendance metrics, leave applications, or payroll summaries in plain English.
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 10, textAlign: 'left' }}>
                <div style={{ fontSize: 12, fontWeight: 700, textTransform: 'uppercase', color: '#666666', letterSpacing: '0.05em', marginBottom: 4 }}>
                  Suggested Questions ({isAdmin ? 'Admin' : 'Employee'})
                </div>
                {suggestedPrompts.map((prompt) => (
                  <button
                    key={prompt}
                    onClick={() => handleSend(prompt)}
                    style={{
                      padding: '12px 18px', background: '#111111', border: '1px solid rgba(255,255,255,0.1)',
                      color: '#ffffff', fontSize: 14, cursor: 'pointer', textAlign: 'left',
                      transition: 'background 0.2s', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.background = '#222222')}
                    onMouseLeave={(e) => (e.currentTarget.style.background = '#111111')}
                  >
                    <span>"{prompt}"</span>
                    <Send size={14} color="#666666" />
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Active Message History */}
          {messages.map((m) => (
            <div
              key={m.id}
              style={{
                display: 'flex',
                justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start',
                marginBottom: 4,
              }}
            >
              <div style={{
                maxWidth: '75%',
                padding: '16px 20px',
                background: m.role === 'user' ? '#000000' : '#ffffff',
                color: m.role === 'user' ? '#ffffff' : '#000000',
                border: m.role === 'user' ? '1px solid rgba(255,255,255,0.3)' : '1px solid #E6E6E6',
                borderRadius: 0,
                boxShadow: m.role === 'assistant' ? '0 10px 30px rgba(0,0,0,0.5)' : 'none',
              }}>
                <div style={{ fontSize: 14, lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>
                  {m.content}
                </div>

                {/* Collapsed Tool Results Badges below AI message */}
                {m.role === 'assistant' && m.tools_used && m.tools_used.length > 0 && (
                  <div style={{ marginTop: 12, paddingTop: 10, borderTop: '1px solid #E6E6E6', display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
                    <Terminal size={12} color="#767676" />
                    <span style={{ fontSize: 11, fontWeight: 700, color: '#767676', textTransform: 'uppercase' }}>Used:</span>
                    {m.tools_used.map((t) => (
                      <span key={t} style={{ padding: '2px 6px', background: '#F1F3F4', color: '#3C4043', fontSize: 10, fontWeight: 700, fontFamily: 'monospace' }}>
                        {t}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* Loading Animation Dots */}
          {loading && (
            <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
              <div style={{
                padding: '16px 24px', background: '#ffffff', color: '#000000',
                border: '1px solid #E6E6E6', display: 'flex', alignItems: 'center', gap: 8,
              }}>
                <div style={{ fontSize: 13, fontWeight: 600 }}>NexusERP AI is searching database</div>
                <div style={{ display: 'flex', gap: 4 }}>
                  <span style={{ width: 6, height: 6, background: '#000', borderRadius: '50%', animation: 'bounce 1s infinite 0s' }} />
                  <span style={{ width: 6, height: 6, background: '#000', borderRadius: '50%', animation: 'bounce 1s infinite 0.2s' }} />
                  <span style={{ width: 6, height: 6, background: '#000', borderRadius: '50%', animation: 'bounce 1s infinite 0.4s' }} />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar at Bottom */}
        <div style={{ padding: 24, borderTop: '1px solid rgba(255,255,255,0.1)', background: '#0a0a0a' }}>
          <form
            onSubmit={(e) => { e.preventDefault(); handleSend(); }}
            style={{ display: 'flex', gap: 12, maxWidth: 900, margin: '0 auto' }}
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={isAdmin ? 'Ask Admin query (e.g. "What is today\'s attendance?")' : 'Ask Employee query (e.g. "What is my leave balance?")'}
              style={{
                flex: 1, padding: '14px 20px', background: '#111111', border: '1px solid rgba(255,255,255,0.2)',
                color: '#ffffff', fontSize: 14, outline: 'none', fontFamily: 'var(--font-body)',
              }}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              style={{
                padding: '0 24px', background: '#ffffff', color: '#000000',
                border: 'none', fontSize: 14, fontWeight: 700, cursor: loading || !input.trim() ? 'not-allowed' : 'pointer',
                opacity: loading || !input.trim() ? 0.5 : 1, display: 'inline-flex', alignItems: 'center', gap: 8, borderRadius: 0,
              }}
            >
              <Send size={16} /> Send
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
