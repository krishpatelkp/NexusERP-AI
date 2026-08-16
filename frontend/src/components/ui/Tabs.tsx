import React from 'react'

export interface TabItem {
  id: string
  label: string
  count?: number
}

export interface TabsProps {
  tabs: TabItem[]
  activeTab: string
  onChange: (id: string) => void
}

export const Tabs: React.FC<TabsProps> = ({ tabs, activeTab, onChange }) => {
  return (
    <div style={{
      display: 'flex',
      gap: 4,
      borderBottom: '1px solid #E6E6E6',
      background: '#fafafa',
      padding: '0 16px',
      overflowX: 'auto',
    }}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            padding: '14px 20px',
            background: 'none',
            border: 'none',
            borderBottom: activeTab === tab.id ? '2px solid #000' : '2px solid transparent',
            color: activeTab === tab.id ? '#000' : '#767676',
            fontWeight: activeTab === tab.id ? 600 : 500,
            fontSize: 14,
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            fontFamily: 'var(--font-body)',
            marginBottom: -1,
            whiteSpace: 'nowrap',
          }}
        >
          {tab.label}
          {tab.count !== undefined && tab.count > 0 && (
            <span style={{
              padding: '2px 8px',
              background: activeTab === tab.id ? '#000' : '#E6E6E6',
              color: activeTab === tab.id ? '#fff' : '#000',
              fontSize: 11,
              fontWeight: 600,
              borderRadius: 10,
            }}>
              {tab.count}
            </span>
          )}
        </button>
      ))}
    </div>
  )
}
