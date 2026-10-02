import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

const Layout = () => {
  return (
    <div style={{ display: 'flex', minHeight: '100vh', position: 'relative' }}>
      <Sidebar />
      <main style={{ 
        flex: 1, 
        marginLeft: 'calc(280px + 2rem)', /* Sidebar width + gap */
        padding: '1rem 2rem 1rem 0'
      }}>
        <div 
          className="content-area animate-fade-in"
          style={{
            minHeight: 'calc(100vh - 2rem)',
            borderRadius: '1.5rem',
            paddingBottom: '2rem'
          }}
        >
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout;
