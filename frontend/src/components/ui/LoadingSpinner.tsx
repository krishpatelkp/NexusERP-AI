import React from 'react'

export const LoadingSpinner: React.FC<{ text?: string }> = ({ text = 'Loading...' }) => {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 40,
      color: '#767676',
      fontSize: 14,
    }}>
      <div style={{
        width: 32,
        height: 32,
        border: '3px solid #E6E6E6',
        borderTopColor: '#000',
        borderRadius: '50%',
        animation: 'spin 0.8s linear infinite',
        marginBottom: 12,
      }} />
      {text}
    </div>
  )
}
