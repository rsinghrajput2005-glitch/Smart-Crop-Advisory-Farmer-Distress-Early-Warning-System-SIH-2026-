import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import FarmerHome from './pages/FarmerHome';
import Weather from './pages/Weather';
import CropAdvisory from './pages/CropAdvisory';
import MandiPrices from './pages/MandiPrices';
import RiskScore from './pages/RiskScore';
import OfficerDashboard from './pages/OfficerDashboard';
import './App.css';

export default function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <Navbar />
        <main className="app-content">
          <Routes>
            <Route path="/" element={<FarmerHome />} />
            <Route path="/weather" element={<Weather />} />
            <Route path="/advisory" element={<CropAdvisory />} />
            <Route path="/mandi" element={<MandiPrices />} />
            <Route path="/risk" element={<RiskScore />} />
            <Route path="/officer" element={<OfficerDashboard />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
