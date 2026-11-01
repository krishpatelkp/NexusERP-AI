import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { Card } from '../../components/ui/Card';
import { Table } from '../../components/ui/Table';
import { Badge } from '../../components/ui/Badge';
import { KPICard } from '../../components/ui/KPICard';
import { CreditCard, ArrowUpRight } from 'lucide-react';
export default function PaymentsPage() {
    const [payments, setPayments] = useState([]);
    useEffect(() => {
        async function load() {
            const data = await api.getPayments().catch(() => []);
            setPayments(data);
        }
        load();
    }, []);
    const totalDisbursed = payments.reduce((sum, p) => sum + Number(p.amount || 0), 0);
    return (<div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div>
        <h1 className="heading-lg" style={{ fontSize: 28, marginBottom: 4 }}>Payments & Financial Audit Hub</h1>
        <p className="body-md" style={{ color: '#767676' }}>Audit log of outbound payment transfers, disbursements, and transaction references.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
        <KPICard label="Total Disbursed" value={`₹${totalDisbursed.toLocaleString()}`} change="Successful Transfers" icon={CreditCard}/>
        <KPICard label="Total Transactions" value={payments.length} change="Audit Records" icon={ArrowUpRight}/>
      </div>

      <Card>
        <Table columns={[
            { header: 'Payment #', accessor: (row) => row.payment_number || `PAY-${row.id}` },
            { header: 'Employee', accessor: (row) => row.employee_name || 'N/A' },
            { header: 'Payment Method', accessor: (row) => row.payment_method || 'Bank Transfer' },
            { header: 'Amount', accessor: (row) => `₹${Number(row.amount || 0).toLocaleString()}` },
            { header: 'Disbursement Date', accessor: (row) => row.payment_date || row.processed_at?.split('T')[0] || '—' },
            { header: 'Bank / Trans Ref', accessor: (row) => row.bank_reference_number || row.transaction_id || '—' },
            {
                header: 'Status',
                accessor: (row) => (<Badge variant={row.status === 'PAID' || row.status === 'COMPLETED' || row.status === 'SUCCESS' ? 'success' : row.status === 'FAILED' ? 'danger' : 'warning'}>
                  {row.status || 'PENDING'}
                </Badge>),
            },
        ]} data={payments} emptyText="No financial payment records found."/>
      </Card>
    </div>);
}

