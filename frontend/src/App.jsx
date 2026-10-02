import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Demand from './pages/Demand';
import Supply from './pages/Supply';
import Gap from './pages/Gap';
import Forecast from './pages/Forecast';
import Policy from './pages/Policy';
import Copilot from './pages/Copilot';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="demand" element={<Demand />} />
          <Route path="supply" element={<Supply />} />
          <Route path="gap" element={<Gap />} />
          <Route path="forecast" element={<Forecast />} />
          <Route path="policy" element={<Policy />} />
          <Route path="copilot" element={<Copilot />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
