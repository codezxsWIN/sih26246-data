import React, { useEffect, useState } from 'react';
import { api } from '../apiClient';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const getRiskColor = (risk) => {
  if (risk === 'Critical Shortage') return 'var(--color-critical)';
  if (risk === 'Moderate Shortage') return 'var(--color-moderate)';
  if (risk === 'Oversupply') return 'var(--color-supply)';
  return 'var(--color-balanced)'; // Balanced
};

const getRiskBadgeClass = (risk) => {
  if (risk === 'Critical Shortage') return 'badge-critical';
  if (risk === 'Moderate Shortage') return 'badge-moderate';
  if (risk === 'Oversupply') return 'badge-demand'; // Custom logic
  return 'badge-balanced';
};

const Gap = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchGaps = async () => {
      setLoading(true);
      try {
        const res = await api.getGaps();
        setData(res.data || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchGaps();
  }, []);

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Gap & Shortage Analysis</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Identify skill shortages and oversupply across the market.</p>
      </div>

      {loading ? (
        <div className="flex-center" style={{ height: '300px' }}><div className="spinner"></div></div>
      ) : (
        <>
          <div className="glass-panel" style={{ marginBottom: '2rem' }}>
            <h3 style={{ marginBottom: '1.5rem' }}>Shortage vs Oversupply (Gap Value)</h3>
            <div style={{ height: '400px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.slice(0, 20)} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                  <XAxis dataKey="entity_name" stroke="var(--text-muted)" angle={-45} textAnchor="end" height={80} />
                  <YAxis stroke="var(--text-muted)" />
                  <Tooltip 
                    cursor={{fill: 'rgba(255,255,255,0.05)'}} 
                    formatter={(value) => [value.toLocaleString(), 'Gap']}
                  />
                  <Bar dataKey="gap_value">
                    {data.slice(0, 20).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={getRiskColor(entry.risk_category)} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="glass-panel">
            <h3 style={{ marginBottom: '1.5rem' }}>Detailed Gap Assessment</h3>
            <div style={{ overflowX: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Entity</th>
                    <th>Type</th>
                    <th>Demand Score</th>
                    <th>Supply Est</th>
                    <th>Gap Value</th>
                    <th>Risk Category</th>
                  </tr>
                </thead>
                <tbody>
                  {data.map((item, idx) => (
                    <tr key={idx}>
                      <td style={{ fontWeight: '500' }}>{item.entity_name}</td>
                      <td style={{ textTransform: 'capitalize' }}>{item.entity_type}</td>
                      <td>{item.demand_score.toFixed(1)}</td>
                      <td>{item.supply_estimate.toLocaleString()}</td>
                      <td style={{ fontWeight: '600' }}>
                        {item.gap_value > 0 ? `+${item.gap_value.toLocaleString()}` : item.gap_value.toLocaleString()}
                      </td>
                      <td>
                        <span className={`badge ${getRiskBadgeClass(item.risk_category)}`}>
                          {item.risk_category}
                        </span>
                      </td>
                    </tr>
                  ))}
                  {data.length === 0 && (
                    <tr><td colSpan="6" style={{ textAlign: 'center' }}>Insufficient data</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Gap;
