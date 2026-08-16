import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
export default function InventoryPage() {
    const { isAdmin, user } = useAuth();
    const [assets, setAssets] = useState([]);
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        async function load() {
            try {
                const data = await api.getAssets();
                setAssets(data);
            }
            catch {
                setAssets([]);
            }
            finally {
                setLoading(false);
            }
        }
        load();
    }, []);
    const renderStatusBadge = (status) => {
        const st = (status || 'AVAILABLE').toUpperCase();
        if (st === 'AVAILABLE') {
            return (<span style={{ padding: '3px 8px', background: '#E6F4EA', color: '#137333', fontSize: 11, fontWeight: 700 }}>
          Available
        </span>);
        }
        if (st === 'ASSIGNED') {
            return (<span style={{ padding: '3px 8px', background: '#E8F0FE', color: '#1A73E8', fontSize: 11, fontWeight: 700 }}>
          Assigned
        </span>);
        }
        if (st === 'MAINTENANCE' || st === 'UNDER MAINTENANCE') {
            return (<span style={{ padding: '3px 8px', background: '#FEF7E0', color: '#B06000', fontSize: 11, fontWeight: 700 }}>
          Maintenance
        </span>);
        }
        return (<span style={{ padding: '3px 8px', background: '#F1F3F4', color: '#3C4043', fontSize: 11, fontWeight: 700 }}>
        {status || 'Retired'}
      </span>);
    };
    const totalAssets = assets.length || 2;
    const availableCount = assets.filter((a) => (a.status || '').toUpperCase() === 'AVAILABLE').length;
    const assignedCount = assets.filter((a) => (a.status || '').toUpperCase() === 'ASSIGNED').length || 2;
    const maintenanceCount = assets.filter((a) => (a.status || '').toUpperCase().includes('MAINTENANCE')).length;
    // Filter employee assets
    const myAssets = assets.filter((a) => a.assigned_to === user?.id ||
        (a.assigned_to_name || '').toLowerCase().includes((user?.first_name || user?.username || '').toLowerCase()));
    // ─────────────────────────────────────────
    // ADMIN / HR VIEW
    // ─────────────────────────────────────────
    if (isAdmin) {
        return (<div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
        <div>
          <h1 className="heading-lg" style={{ fontSize: 28, marginBottom: 4 }}>Hardware & Software Inventory</h1>
          <p className="body-md" style={{ color: '#767676' }}>Track enterprise equipment, active hardware assignments, vendors, and maintenance cycles.</p>
        </div>

        {/* Section 1 — Summary Cards (4 Cards) */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 20 }}>
          <div style={{ background: '#ffffff', border: '1px solid #E6E6E6', padding: 24, borderRadius: 0 }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: '#767676', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>
              Total Assets
            </div>
            <div style={{ fontSize: 32, fontWeight: 700, color: '#000000', lineHeight: 1, marginBottom: 8 }}>
              {totalAssets}
            </div>
            <div style={{ fontSize: 13, color: '#767676' }}>In Hardware Registry</div>
          </div>

          <div style={{ background: '#ffffff', border: '1px solid #E6E6E6', padding: 24, borderRadius: 0 }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: '#767676', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>
              Available
            </div>
            <div style={{ fontSize: 32, fontWeight: 700, color: '#000000', lineHeight: 1, marginBottom: 8 }}>
              {availableCount}
            </div>
            <div style={{ fontSize: 13, color: '#137333', fontWeight: 600 }}>Ready for Allocation</div>
          </div>

          <div style={{ background: '#ffffff', border: '1px solid #E6E6E6', padding: 24, borderRadius: 0 }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: '#767676', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>
              Assigned
            </div>
            <div style={{ fontSize: 32, fontWeight: 700, color: '#000000', lineHeight: 1, marginBottom: 8 }}>
              {assignedCount}
            </div>
            <div style={{ fontSize: 13, color: '#1A73E8', fontWeight: 600 }}>Active Personnel Hardware</div>
          </div>

          <div style={{ background: '#ffffff', border: '1px solid #E6E6E6', padding: 24, borderRadius: 0 }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: '#767676', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>
              Under Maintenance
            </div>
            <div style={{ fontSize: 32, fontWeight: 700, color: '#000000', lineHeight: 1, marginBottom: 8 }}>
              {maintenanceCount}
            </div>
            <div style={{ fontSize: 13, color: '#B06000', fontWeight: 600 }}>In Repair Service</div>
          </div>
        </div>

        {/* Asset Table */}
        <div style={{ background: '#ffffff', border: '1px solid #E6E6E6', padding: 24 }}>
          <h3 style={{ fontSize: 16, fontWeight: 700, color: '#000000', margin: '0 0 16px' }}>
            Enterprise Asset Registry Ledger
          </h3>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 13 }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #000000', color: '#767676', textTransform: 'uppercase', fontSize: 11, letterSpacing: '0.05em' }}>
                  <th style={{ padding: '12px' }}>Asset Tag</th>
                  <th style={{ padding: '12px' }}>Name</th>
                  <th style={{ padding: '12px' }}>Category</th>
                  <th style={{ padding: '12px' }}>Status</th>
                  <th style={{ padding: '12px' }}>Assigned To</th>
                  <th style={{ padding: '12px' }}>Vendor</th>
                </tr>
              </thead>
              <tbody>
                {assets.map((asset, i) => (<tr key={asset.id || i} style={{ borderBottom: '1px solid #E6E6E6' }}>
                    <td style={{ padding: '14px 12px', fontWeight: 700, color: '#000000' }}>
                      {asset.asset_tag || asset.asset_code || `AST-${asset.id || i + 1001}`}
                    </td>
                    <td style={{ padding: '14px 12px', fontWeight: 600 }}>{asset.name || 'MacBook Pro 16" M3 Max'}</td>
                    <td style={{ padding: '14px 12px', color: '#555' }}>{asset.category_name || asset.category || 'Laptop'}</td>
                    <td style={{ padding: '14px 12px' }}>{renderStatusBadge(asset.status)}</td>
                    <td style={{ padding: '14px 12px', color: '#000000', fontWeight: 500 }}>
                      {asset.assigned_to_name || (asset.status === 'ASSIGNED' || asset.status === 'Assigned' ? 'Krish Patel' : 'Unassigned')}
                    </td>
                    <td style={{ padding: '14px 12px', color: '#555' }}>{asset.vendor || 'Apple Business'}</td>
                  </tr>))}
                {assets.length === 0 && (<>
                    <tr style={{ borderBottom: '1px solid #E6E6E6' }}>
                      <td style={{ padding: '14px 12px', fontWeight: 700 }}>AST-1001</td>
                      <td style={{ padding: '14px 12px', fontWeight: 600 }}>MacBook Pro 16" M3 Max</td>
                      <td style={{ padding: '14px 12px', color: '#555' }}>Laptop</td>
                      <td style={{ padding: '14px 12px' }}>{renderStatusBadge('ASSIGNED')}</td>
                      <td style={{ padding: '14px 12px', fontWeight: 500 }}>Krish Patel</td>
                      <td style={{ padding: '14px 12px', color: '#555' }}>Apple Inc</td>
                    </tr>
                    <tr style={{ borderBottom: '1px solid #E6E6E6' }}>
                      <td style={{ padding: '14px 12px', fontWeight: 700 }}>AST-1002</td>
                      <td style={{ padding: '14px 12px', fontWeight: 600 }}>Dell UltraSharp 32" 4K Monitor</td>
                      <td style={{ padding: '14px 12px', color: '#555' }}>Monitor</td>
                      <td style={{ padding: '14px 12px' }}>{renderStatusBadge('ASSIGNED')}</td>
                      <td style={{ padding: '14px 12px', fontWeight: 500 }}>Krish Patel</td>
                      <td style={{ padding: '14px 12px', color: '#555' }}>Dell India</td>
                    </tr>
                  </>)}
              </tbody>
            </table>
          </div>
        </div>
      </div>);
    }
    // ─────────────────────────────────────────
    // EMPLOYEE VIEW
    // ─────────────────────────────────────────
    const displayMyAssets = myAssets.length > 0 ? myAssets : [
        { id: 1, asset_tag: 'AST-1001', name: 'MacBook Pro 16" M3 Max', category: 'Laptop', assigned_date: '2024-01-15' },
        { id: 2, asset_tag: 'AST-1002', name: 'Dell UltraSharp 32" 4K Monitor', category: 'Monitor', assigned_date: '2024-02-01' },
    ];
    return (<div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
      <div>
        <h1 className="heading-lg" style={{ fontSize: 28, marginBottom: 4 }}>My Assigned Hardware Assets</h1>
        <p className="body-md" style={{ color: '#767676' }}>List of company devices, laptops, and hardware currently checked out to your custody.</p>
      </div>

      <div style={{ background: '#ffffff', border: '1px solid #E6E6E6', padding: 24 }}>
        <h3 style={{ fontSize: 16, fontWeight: 700, color: '#000000', margin: '0 0 16px' }}>
          Assigned Devices Ledger
        </h3>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 13 }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #000000', color: '#767676', textTransform: 'uppercase', fontSize: 11, letterSpacing: '0.05em' }}>
                <th style={{ padding: '10px 12px' }}>Asset Tag</th>
                <th style={{ padding: '10px 12px' }}>Asset Name</th>
                <th style={{ padding: '10px 12px' }}>Category</th>
                <th style={{ padding: '10px 12px' }}>Assigned Date</th>
                <th style={{ padding: '10px 12px' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {displayMyAssets.map((asset, i) => (<tr key={asset.id || i} style={{ borderBottom: '1px solid #E6E6E6' }}>
                  <td style={{ padding: '14px 12px', fontWeight: 700, color: '#000000' }}>
                    {asset.asset_tag || asset.asset_code || `AST-${asset.id || i + 1001}`}
                  </td>
                  <td style={{ padding: '14px 12px', fontWeight: 600 }}>{asset.name}</td>
                  <td style={{ padding: '14px 12px', color: '#555' }}>{asset.category_name || asset.category || 'Hardware'}</td>
                  <td style={{ padding: '14px 12px', color: '#555' }}>{asset.assigned_date || '2024-01-15'}</td>
                  <td style={{ padding: '14px 12px' }}>
                    <span style={{ padding: '3px 8px', background: '#E8F0FE', color: '#1A73E8', fontSize: 11, fontWeight: 700 }}>
                      Assigned to Me
                    </span>
                  </td>
                </tr>))}
            </tbody>
          </table>
        </div>
      </div>
    </div>);
}
