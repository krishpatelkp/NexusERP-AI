import React from 'react';
export const Card = ({ children, style, className }) => {
    return (<div className={className} style={{
            background: '#fff',
            border: '1px solid #E6E6E6',
            boxShadow: '0 20px 60px rgba(0,0,0,0.04)',
            padding: 24,
            ...style,
        }}>
      {children}
    </div>);
};
