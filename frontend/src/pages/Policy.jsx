import React, { useEffect, useState } from 'react';
import { api } from '../apiClient';
import { Target, ArrowRight } from 'lucide-react';

const Policy = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPolicies = async () => {
      setLoading(true);
      try {
        const res = await api.getPolicyRecommendations();
        setData(res.data || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchPolicies();
  }, []);

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Policy Interventions</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Generated deterministic rules for skilling and market interventions.</p>
      </div>

      {loading ? (
        <div className="flex-center" style={{ height: '300px' }}><div className="spinner"></div></div>
      ) : (
        <div style={{ display: 'grid', gap: '1.5rem', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))' }}>
          {data.map((item, idx) => (
            <div key={idx} className="glass-panel" style={{ display: 'flex', flexDirection: 'column' }}>
              <div className="flex-between" style={{ marginBottom: '1rem' }}>
                <span className={`badge ${item.priority_level === 'HIGH' ? 'badge-critical' : item.priority_level === 'MEDIUM' ? 'badge-moderate' : 'badge-balanced'}`}>
                  {item.priority_level} Priority
                </span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{item.target_state || 'All India'}</span>
              </div>
              
              <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Target size={20} style={{ color: 'var(--color-policy)' }} />
                {item.intervention_type.replace(/_/g, ' ')}
              </h3>
              
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '1.5rem', flex: 1, lineHeight: '1.6' }}>
                {item.description}
              </p>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--color-demand)', fontWeight: '500', fontSize: '0.875rem', cursor: 'pointer' }}>
                View detailed execution plan <ArrowRight size={16} />
              </div>
            </div>
          ))}
          {data.length === 0 && (
            <div className="glass-panel flex-center" style={{ gridColumn: '1 / -1', padding: '3rem', color: 'var(--text-muted)' }}>
              No policy recommendations available at this time.
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Policy;
