import React, { useEffect, useState } from 'react';
import { api } from '../apiClient';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const Demand = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [entityType, setEntityType] = useState('');

  useEffect(() => {
    const fetchDemand = async () => {
      setLoading(true);
      try {
        const params = entityType ? { entity_type: entityType } : {};
        const res = await api.getDemandScores(params);
        setData(res.data || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchDemand();
  }, [entityType]);

  return (
    <div>
      <div className="flex-between" style={{ marginBottom: '2rem' }}>
        <div>
          <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Demand Analysis</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Analyze real-time demand scores for occupations and skills.</p>
        </div>
        <select 
          value={entityType} 
          onChange={(e) => setEntityType(e.target.value)}
          style={{
            padding: '0.5rem 1rem',
            borderRadius: 'var(--radius-md)',
            background: 'var(--bg-secondary)',
            border: '1px solid var(--glass-border)',
            color: 'white',
            outline: 'none'
          }}
        >
          <option value="">All Entities</option>
          <option value="occupation">Occupations</option>
          <option value="skill">Skills</option>
          <option value="sector">Sectors</option>
        </select>
      </div>

      {loading ? (
        <div className="flex-center" style={{ height: '300px' }}><div className="spinner"></div></div>
      ) : (
        <>
          <div className="glass-panel" style={{ marginBottom: '2rem' }}>
            <h3 style={{ marginBottom: '1.5rem' }}>Demand Score Distribution</h3>
            <div style={{ height: '400px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.slice(0, 15)} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                  <XAxis dataKey="entity_name" stroke="var(--text-muted)" angle={-45} textAnchor="end" height={80} />
                  <YAxis stroke="var(--text-muted)" />
                  <Tooltip cursor={{fill: 'rgba(255,255,255,0.05)'}} />
                  <Bar dataKey="demand_score" fill="var(--color-demand)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="glass-panel">
            <h3 style={{ marginBottom: '1.5rem' }}>Demand Details</h3>
            <div style={{ overflowX: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Entity</th>
                    <th>Type</th>
                    <th>Geography</th>
                    <th>Score (0-100)</th>
                    <th>Total Postings</th>
                  </tr>
                </thead>
                <tbody>
                  {data.map((item, idx) => (
                    <tr key={idx}>
                      <td style={{ fontWeight: '500' }}>{item.entity_name}</td>
                      <td style={{ textTransform: 'capitalize' }}>{item.entity_type}</td>
                      <td>{item.geography_name}</td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <div style={{ width: '100px', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px' }}>
                            <div style={{ width: `${item.demand_score}%`, height: '100%', background: 'var(--color-demand)', borderRadius: '3px' }}></div>
                          </div>
                          <span>{item.demand_score.toFixed(1)}</span>
                        </div>
                      </td>
                      <td>{item.total_postings.toLocaleString()}</td>
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

export default Demand;
