import React from 'react'

export interface Column<T> {
  header: string
  accessor: keyof T | ((row: T) => React.ReactNode)
  align?: 'left' | 'center' | 'right'
}

export interface TableProps<T> {
  columns: Column<T>[]
  data: T[]
  keyField?: keyof T
  emptyText?: string
}

export function Table<T extends Record<string, any>>({
  columns,
  data,
  keyField = 'id',
  emptyText = 'No data available',
}: TableProps<T>) {
  return (
    <div style={{ width: '100%', overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 14 }}>
        <thead>
          <tr style={{ borderBottom: '2px solid #000', color: '#767676', fontSize: 12, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            {columns.map((col, i) => (
              <th key={i} style={{ padding: '12px 16px', textAlign: col.align || 'left' }}>
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.length > 0 ? (
            data.map((row, idx) => (
              <tr key={row[keyField] ?? idx} style={{ borderBottom: '1px solid #E6E6E6' }}>
                {columns.map((col, cIdx) => (
                  <td key={cIdx} style={{ padding: '14px 16px', textAlign: col.align || 'left' }}>
                    {typeof col.accessor === 'function' ? col.accessor(row) : row[col.accessor]}
                  </td>
                ))}
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan={columns.length} style={{ padding: 40, textAlign: 'center', color: '#767676' }}>
                {emptyText}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
