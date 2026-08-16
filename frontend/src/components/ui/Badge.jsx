import React from 'react';
export const Badge = ({ children, variant = 'neutral' }) => {
    const styles = {
        success: { bg: '#E6F4EA', color: '#137333' },
        danger: { bg: '#FCE8E6', color: '#C5221F' },
        warning: { bg: '#FEF7E0', color: '#B06000' },
        info: { bg: '#E8F0FE', color: '#1A73E8' },
        neutral: { bg: '#F1F3F4', color: '#3C4043' },
    };
    const current = styles[variant] || styles.neutral;
    return (<span style={{
            display: 'inline-flex',
            alignItems: 'center',
            padding: '3px 10px',
            fontSize: 12,
            fontWeight: 600,
            background: current.bg,
            color: current.color,
            borderRadius: 4,
            whiteSpace: 'nowrap',
        }}>
      {children}
    </span>);
};
