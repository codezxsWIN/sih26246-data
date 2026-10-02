import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  TrendingUp, 
  Users, 
  Activity, 
  LineChart, 
  ShieldCheck, 
  MessageSquareText 
} from 'lucide-react';
import { motion } from 'framer-motion';

const navItems = [
  { path: '/', label: 'Overview Dashboard', icon: LayoutDashboard },
  { path: '/demand', label: 'Demand Analysis', icon: TrendingUp },
  { path: '/supply', label: 'Supply Estimation', icon: Users },
  { path: '/gap', label: 'Gap & Shortages', icon: Activity },
  { path: '/forecast', label: 'AI Forecasting', icon: LineChart },
  { path: '/policy', label: 'Policy Interventions', icon: ShieldCheck },
  { path: '/copilot', label: 'AI Policy Copilot', icon: MessageSquareText },
];

const Sidebar = () => {
  return (
    <motion.aside 
      initial={{ x: -250 }}
      animate={{ x: 0 }}
      className="sidebar glass-panel"
      style={{
        width: '280px',
        height: 'calc(100vh - 2rem)',
        position: 'fixed',
        top: '1rem',
        left: '1rem',
        display: 'flex',
        flexDirection: 'column',
        padding: '2rem 1.5rem',
        borderRadius: '1.5rem'
      }}
    >
      <div className="sidebar-header" style={{ marginBottom: '2.5rem' }}>
        <h2 className="title-gradient" style={{ fontSize: '1.5rem', lineHeight: '1.2' }}>
          Labour Market<br />Intelligence
        </h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginTop: '0.5rem' }}>
          AI-Powered Engine
        </p>
      </div>

      <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => 
                `nav-link ${isActive ? 'active' : ''}`
              }
              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: '1rem',
                padding: '0.875rem 1rem',
                borderRadius: '0.75rem',
                color: isActive ? 'white' : 'var(--text-secondary)',
                background: isActive ? 'rgba(59, 130, 246, 0.15)' : 'transparent',
                border: isActive ? '1px solid rgba(59, 130, 246, 0.3)' : '1px solid transparent',
                textDecoration: 'none',
                transition: 'all 0.2s',
                fontWeight: isActive ? '600' : '500'
              })}
            >
              <Icon size={20} style={{ color: 'var(--color-demand)' }} />
              {item.label}
            </NavLink>
          );
        })}
      </nav>

      <div style={{ marginTop: 'auto', paddingTop: '2rem', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'linear-gradient(135deg, var(--color-policy), var(--color-demand))', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
            GP
          </div>
          <div>
            <div style={{ fontWeight: '600', fontSize: '0.875rem' }}>Gov Portal</div>
            <div style={{ color: 'var(--color-demand)', fontSize: '0.75rem' }}>Connected</div>
          </div>
        </div>
      </div>
    </motion.aside>
  );
};

export default Sidebar;
