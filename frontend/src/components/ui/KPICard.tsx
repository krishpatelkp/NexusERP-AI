import React from 'react'
import { Card } from './Card'

export interface KPICardProps {
  label: string
  value: string | number
  change?: string
  icon?: React.ComponentType<{ size: number; color?: string }>
}

export const KPICard: React.FC<KPICardProps> = ({ label, value, change, icon: Icon }) => {
  return (
    <Card style={{ padding: 20 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
        <div style={{ fontSize: 13, color: '#767676', fontWeight: 500 }}>{label}</div>
        {Icon && (
          <div style={{
            width: 32, height: 32,
            background: '#F7F6F3',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Icon size={16} color="#000" />
          </div>
        )}
      </div>
      <div style={{ fontSize: 32, fontWeight: 700, letterSpacing: '-0.03em', lineHeight: 1, color: '#000', marginBottom: 6 }}>
        {value}
      </div>
      {change && (
        <div style={{ fontSize: 12, color: '#137333', fontWeight: 600 }}>
          {change}
        </div>
      )}
    </Card>
  )
}
