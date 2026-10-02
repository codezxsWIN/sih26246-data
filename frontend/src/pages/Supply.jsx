import React, { useEffect, useState } from 'react';
import { api } from '../apiClient';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const Supply = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSupply = async () => {
      setLoading(true);
      try {
        const res = await api.getSupplyEstimates();
        setData(res.data || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchSupply();
  }, []);

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Supply Estimation</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Track available labour supply based on PLFS and skilling datasets.</p>
      </div>

      {loading ? (
        <div className="flex-center" style={{ height: '300px' }}><div className="spinner"></div></div>
      ) : (
        <>
          <div className="glass-panel" style={{ marginBottom: '2rem' }}>
            <h3 style={{ marginBottom: '1.5rem' }}>Supply Distribution</h3>
            <div style={{ height: '400px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.slice(0, 15)} margin={{ top: 20, right: 30, left: 40, bottom: 60 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                  <XAxis dataKey="entity_name" stroke="var(--text-muted)" angle={-45} textAnchor="end" height={80} />
                  <YAxis stroke="var(--text-muted)" />
                  <Tooltip cursor={{fill: 'rgba(255,255,255,0.05)'}} />
                  <Bar dataKey="total_supply_estimate" fill="var(--color-supply)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="glass-panel">
            <h3 style={{ marginBottom: '1.5rem' }}>Supply Details</h3>
            <div style={{ overflowX: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Entity</th>
                    <th>Type</th>
                    <th>Geography</th>
                    <th>Total Supply</th>
                    <th>Confidence Score</th>
                  </tr>
                </thead>
                <tbody>
                  {data.map((item, idx) => (
                    <tr key={idx}>
                      <td style={{ fontWeight: '500' }}>{item.entity_name}</td>
                      <td style={{ textTransform: 'capitalize' }}>{item.entity_type}</td>
                      <td>{item.geography_name}</td>
                      <td style={{ color: 'var(--color-supply)', fontWeight: '600' }}>
                        {item.total_supply_estimate.toLocaleString()}
                      </td>
                      <td>{item.confidence_score.toFixed(2)}</td>
                    </tr>
                  ))}
                  {data.length === 0 && (
                    <tr><td colSpan="5" style={{ textAlign: 'center' }}>Insufficient data</td></tr>
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

export default Supply;
