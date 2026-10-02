import React, { useEffect, useState } from 'react';
import { api } from '../apiClient';
import { Activity, Briefcase, Users, AlertTriangle } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  LineChart, Line
} from 'recharts';

const StatCard = ({ title, value, subtitle, icon: Icon, colorClass }) => (
  <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
    <div className="flex-between">
      <h3 style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', fontWeight: '500' }}>{title}</h3>
      <div style={{ padding: '0.5rem', borderRadius: '0.5rem', background: 'rgba(255,255,255,0.05)' }}>
        <Icon size={20} className={colorClass} />
      </div>
    </div>
    <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--text-primary)' }}>
      {value}
    </div>
    <p style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>{subtitle}</p>
  </div>
);

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState({
    demand: [],
    supply: [],
    gaps: []
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [demandRes, supplyRes, gapRes] = await Promise.all([
          api.getDemandScores({ limit: 5 }),
          api.getSupplyEstimates({ limit: 5 }),
          api.getGaps({ limit: 5 })
        ]);
        
        setData({
          demand: demandRes.data || [],
          supply: supplyRes.data || [],
          gaps: gapRes.data || []
        });
      } catch (err) {
        console.error("Dashboard data load failed", err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex-center" style={{ height: '100%' }}>
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Overview Dashboard</h1>
        <p style={{ color: 'var(--text-secondary)' }}>High-level summary of current labour market intelligence.</p>
      </div>

      <div className="grid-dashboard" style={{ marginBottom: '2rem' }}>
        <StatCard 
          title="Top In-Demand" 
          value={data.demand.length > 0 ? data.demand[0].entity_name : 'N/A'}
          subtitle="Highest demand score across sectors"
          icon={Briefcase}
          colorClass="text-gradient"
          style={{ color: 'var(--color-demand)' }}
        />
        <StatCard 
          title="Top Labour Supply" 
          value={data.supply.length > 0 ? data.supply[0].entity_name : 'N/A'}
          subtitle="Largest available workforce"
          icon={Users}
          style={{ color: 'var(--color-supply)' }}
        />
        <StatCard 
          title="Critical Shortages" 
          value={data.gaps.filter(g => g.risk_category === 'Critical Shortage').length}
          subtitle="Immediate policy intervention needed"
          icon={AlertTriangle}
          style={{ color: 'var(--color-critical)' }}
        />
        <StatCard 
          title="System Health" 
          value="Online"
          subtitle="API backend connected"
          icon={Activity}
          style={{ color: 'var(--color-policy)' }}
        />
      </div>

      <div className="grid-dashboard" style={{ gridTemplateColumns: '1fr 1fr' }}>
        <div className="glass-panel">
          <h3 style={{ marginBottom: '1.5rem', fontWeight: '600' }}>Top Demand Entities</h3>
          <div style={{ height: '300px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.demand} layout="vertical" margin={{ top: 0, right: 0, left: 50, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" horizontal={false} />
                <XAxis type="number" stroke="var(--text-muted)" />
                <YAxis dataKey="entity_name" type="category" stroke="var(--text-muted)" width={100} tick={{ fontSize: 12 }} />
                <RechartsTooltip cursor={{fill: 'rgba(255,255,255,0.05)'}} />
                <Bar dataKey="demand_score" fill="var(--color-demand)" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div className="glass-panel">
          <h3 style={{ marginBottom: '1.5rem', fontWeight: '600' }}>Critical Gaps Overview</h3>
          <table className="data-table">
            <thead>
              <tr>
                <th>Entity</th>
                <th>Gap</th>
                <th>Risk</th>
              </tr>
            </thead>
            <tbody>
              {data.gaps.slice(0, 5).map((gap, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: '500' }}>{gap.entity_name}</td>
                  <td>{Math.abs(gap.gap_value).toLocaleString()}</td>
                  <td>
                    <span className={`badge ${gap.risk_category.includes('Critical') ? 'badge-critical' : 'badge-high'}`}>
                      {gap.risk_category}
                    </span>
                  </td>
                </tr>
              ))}
              {data.gaps.length === 0 && (
                <tr><td colSpan="3" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>Data unavailable</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
