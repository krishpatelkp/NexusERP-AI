import React from 'react';
export const EmptyState = ({ title, description, actionLabel, onAction }) => {
    return (<div style={{
            textAlign: 'center',
            padding: '48px 24px',
            background: '#fff',
            border: '1px solid #E6E6E6',
        }}>
      <h3 style={{ fontSize: 18, fontWeight: 600, color: '#000', marginBottom: 8 }}>{title}</h3>
      {description && <p style={{ fontSize: 14, color: '#767676', maxWidth: 400, margin: '0 auto 20px' }}>{description}</p>}
      {actionLabel && onAction && (<button onClick={onAction} className="btn-primary" style={{ fontSize: 13, height: 38 }}>
          {actionLabel}
        </button>)}
    </div>);
};
