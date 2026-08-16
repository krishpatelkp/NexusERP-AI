import React from 'react'
import { X } from 'lucide-react'

export interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  children: React.ReactNode
}

export const Modal: React.FC<ModalProps> = ({ isOpen, onClose, title, children }) => {
  if (!isOpen) return null

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0,0,0,0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: 24,
    }}>
      <div style={{
        width: '100%',
        maxWidth: 520,
        background: '#fff',
        border: '1px solid #E6E6E6',
        boxShadow: '0 20px 60px rgba(0,0,0,0.15)',
        overflow: 'hidden',
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '16px 24px',
          borderBottom: '1px solid #E6E6E6',
          background: '#fafafa',
        }}>
          <h3 style={{ fontSize: 16, fontWeight: 700, margin: 0, color: '#000' }}>{title}</h3>
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 4, color: '#767676' }}
          >
            <X size={18} />
          </button>
        </div>
        <div style={{ padding: 24 }}>
          {children}
        </div>
      </div>
    </div>
  )
}
