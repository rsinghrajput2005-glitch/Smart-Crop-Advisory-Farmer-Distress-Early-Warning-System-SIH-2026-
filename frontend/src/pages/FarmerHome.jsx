import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  MapPin, Wheat, Thermometer, ShieldAlert, CloudSun,
  BookOpen, Store, ChevronRight, AlertTriangle, Sprout
} from 'lucide-react';
import { getFarmerData, getWeatherData, getAdvisoryData, getMandiData, getRiskData, getAlertsData } from '../services/api';
import { getRiskCategory, getRiskColor, getBestMandi, formatPrice } from '../utils/helpers';
import StatCard from '../components/StatCard';
import RiskGauge from '../components/RiskGauge';
import AlertCard from '../components/AlertCard';
import './FarmerHome.css';

export default function FarmerHome() {
  const [farmer, setFarmer] = useState(null);
  const [weather, setWeather] = useState(null);
  const [advisory, setAdvisory] = useState(null);
  const [mandis, setMandis] = useState([]);
  const [risk, setRisk] = useState(null);
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    async function loadData() {
      const [f, w, a, m, r, al] = await Promise.all([
        getFarmerData(),
        getWeatherData(),
        getAdvisoryData(),
        getMandiData(),
        getRiskData(),
        getAlertsData()
      ]);
      setFarmer(f);
      setWeather(w);
      setAdvisory(a);
      setMandis(m);
      setRisk(r);
      setAlerts(al);
    }
    loadData();
  }, []);

  if (!farmer || !weather || !risk) return null;

  const bestMandi = getBestMandi(mandis);
  const riskCategory = getRiskCategory(risk.overallScore);

  return (
    <div className="page-container farmer-home">
      <div className="farmer-greeting">
        <div className="farmer-greeting-text">
          <h1>Namaste, <span>{farmer.name}</span></h1>
          <p><MapPin size={16} /> {farmer.location}, {farmer.state}</p>
        </div>
        <div className="farmer-crop-badge">
          <div className="crop-icon"><Sprout size={22} /></div>
          <div className="crop-details">
            <strong>{farmer.crop}</strong>
            <span>{farmer.growthStage} stage</span>
          </div>
        </div>
      </div>

      <div className="home-stats">
        <StatCard
          icon={Thermometer}
          label="Temperature"
          value={`${weather.current.temperature}°C`}
          subtitle={weather.current.condition}
          color="var(--color-info)"
        />
        <StatCard
          icon={CloudSun}
          label="Humidity"
          value={`${weather.current.humidity}%`}
          subtitle={`Rainfall: ${weather.current.rainfall}mm`}
          color="var(--color-primary-lighter)"
        />
        <StatCard
          icon={ShieldAlert}
          label="Risk Score"
          value={risk.overallScore}
          subtitle={riskCategory}
          color={getRiskColor(risk.overallScore)}
        />
        <StatCard
          icon={Store}
          label="Best Price"
          value={`${formatPrice(bestMandi.pricePerQuintal)}/q`}
          subtitle={bestMandi.name}
          color="var(--color-primary)"
        />
      </div>

      <div className="home-main">
        <div className="card home-risk-overview">
          <RiskGauge score={risk.overallScore} size="small" />
          <div className="home-risk-text">
            <h3>Risk Assessment</h3>
            <p>
              Your farm currently has a <strong style={{ color: getRiskColor(risk.overallScore) }}>{riskCategory}</strong> risk level.
              Main factors: {risk.factors.slice(0, 2).map(f => f.name).join(', ')}.
            </p>
            <Link to="/risk" className="view-all-link" style={{ marginTop: 12, display: 'inline-flex' }}>
              View Details <ChevronRight size={16} />
            </Link>
          </div>
        </div>

        <div className="card home-advisory-highlight">
          <div className={`advisory-highlight-badge priority-${advisory.priority}`}>
            <AlertTriangle size={14} />
            {advisory.priority} Priority
          </div>
          <div className="advisory-highlight-title">{advisory.recommendation}</div>
          <p className="advisory-highlight-explain">{advisory.explanation.substring(0, 120)}...</p>
          <Link to="/advisory" className="view-all-link" style={{ marginTop: 12, display: 'inline-flex' }}>
            View Full Advisory <ChevronRight size={16} />
          </Link>
        </div>
      </div>

      <div className="home-section">
        <div className="home-section-header">
          <h2 className="section-title"><AlertTriangle size={20} /> Active Alerts</h2>
          </div>
        {alerts.slice(0, 2).map(alert => (
          <AlertCard
            key={alert.id}
            type={alert.type}
            title={alert.title}
            message={alert.message}
            timestamp={alert.timestamp}
          />
        ))}
      </div>

      <div className="home-section">
        <div className="home-section-header">
          <h2 className="section-title"><Store size={20} /> Best Mandi Price</h2>
          <Link to="/mandi" className="view-all-link">
            All Mandis <ChevronRight size={16} />
          </Link>
        </div>
        <div className="home-mandi-highlight">
          <div className="mandi-icon"><Store size={24} /></div>
          <div className="mandi-info">
            <div className="mandi-label">Best price for {farmer.crop}</div>
            <div className="mandi-price">{formatPrice(bestMandi.pricePerQuintal)}/quintal</div>
            <div className="mandi-name">{bestMandi.name} • {bestMandi.distance} km away</div>
          </div>
        </div>
      </div>

      <div className="home-section">
        <h2 className="section-title">Quick Navigation</h2>
        <div className="home-quick-nav">
          <Link to="/weather" className="quick-nav-card">
            <div className="nav-card-icon"><CloudSun size={24} /></div>
            <div className="nav-card-label">Weather</div>
            <div className="nav-card-desc">Forecast & alerts</div>
          </Link>
          <Link to="/advisory" className="quick-nav-card">
            <div className="nav-card-icon"><BookOpen size={24} /></div>
            <div className="nav-card-label">Crop Advisory</div>
            <div className="nav-card-desc">Today's actions</div>
          </Link>
          <Link to="/mandi" className="quick-nav-card">
            <div className="nav-card-icon"><Store size={24} /></div>
            <div className="nav-card-label">Mandi Prices</div>
            <div className="nav-card-desc">Compare & sell</div>
          </Link>
          <Link to="/risk" className="quick-nav-card">
            <div className="nav-card-icon"><ShieldAlert size={24} /></div>
            <div className="nav-card-label">Risk Score</div>
            <div className="nav-card-desc">Risk breakdown</div>
          </Link>
        </div>
      </div>
    </div>
  );
}
