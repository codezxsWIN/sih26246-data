import React, { useEffect, useState } from 'react';
import { api } from '../apiClient';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const Forecast = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchForecasts = async () => {
      setLoading(true);
      try {
        const res = await api.getForecasts();
        setData(res.data || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchForecasts();
  }, []);

  // Process data for charts: group by entity to show trend lines
  const chartDataMap = {};
  data.forEach(item => {
    if (!chartDataMap[item.horizon_months]) {
      chartDataMap[item.horizon_months] = { name: `${item.horizon_months} Months` };
    }
    // We'll just show the top 5 entities
    if (data.indexOf(item) < 15) {
      chartDataMap[item.horizon_months][item.entity_name] = item.forecasted_value;
    }
  });
  
  const chartData = Object.values(chartDataMap).sort((a, b) => parseInt(a.name) - parseInt(b.name));

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>AI Forecasting</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Predictive ML models projecting future labour demand.</p>
      </div>

      {loading ? (
        <div className="flex-center" style={{ height: '300px' }}><div className="spinner"></div></div>
      ) : (
        <>
          <div className="glass-panel" style={{ marginBottom: '2rem' }}>
            <h3 style={{ marginBottom: '1.5rem' }}>Demand Projections (3, 6, 12 Months)</h3>
            <div style={{ height: '400px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="name" stroke="var(--text-muted)" />
                  <YAxis stroke="var(--text-muted)" />
                  <Tooltip cursor={{fill: 'rgba(255,255,255,0.05)'}} />
                  <Legend />
                  {Object.keys(chartData[0] || {}).filter(k => k !== 'name').map((key, i) => (
                    <Line 
                      key={key} 
                      type="monotone" 
                      dataKey={key} 
                      stroke={`hsl(${(i * 50) % 360}, 70%, 60%)`} 
                      strokeWidth={3}
                      activeDot={{ r: 8 }} 
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="glass-panel">
            <h3 style={{ marginBottom: '1.5rem' }}>Forecast Details & SHAP Values</h3>
            <div style={{ overflowX: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Entity</th>
                    <th>Horizon</th>
                    <th>Forecast Value</th>
                    <th>Model Used</th>
                    <th>Top SHAP Feature</th>
                  </tr>
                </thead>
                <tbody>
                  {data.map((item, idx) => {
                    let shapInfo = "N/A";
                    try {
                      const shap = JSON.parse(item.shap_explanation);
                      if (shap && Object.keys(shap).length > 0) {
                        shapInfo = Object.keys(shap)[0]; // Just showing top feature
                      }
                    } catch (e) {}

                    return (
                      <tr key={idx}>
                        <td style={{ fontWeight: '500' }}>{item.entity_name}</td>
                        <td>{item.horizon_months} Months</td>
                        <td style={{ color: 'var(--color-forecast)', fontWeight: '600' }}>
                          {item.forecasted_value.toFixed(2)}
                        </td>
                        <td><span className="badge" style={{ background: 'rgba(139, 92, 246, 0.15)', color: '#a78bfa' }}>{item.model_used}</span></td>
                        <td style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{shapInfo}</td>
                      </tr>
                    );
                  })}
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

export default Forecast;
