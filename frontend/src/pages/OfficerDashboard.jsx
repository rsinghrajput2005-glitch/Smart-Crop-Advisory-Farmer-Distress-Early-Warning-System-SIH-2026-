import { useState, useEffect, useMemo } from 'react';
import { LayoutDashboard, Users, AlertTriangle, ShieldAlert, Bell, Filter, X, MapPin, Wheat } from 'lucide-react';
import { getOfficerData } from '../services/api';
import { getRiskCategory, getRiskColor } from '../utils/helpers';
import StatCard from '../components/StatCard';
import FarmerRiskCard from '../components/FarmerRiskCard';
import './OfficerDashboard.css';

export default function OfficerDashboard() {
  const [data, setData] = useState(null);
  const [riskFilter, setRiskFilter] = useState('ALL');
  const [locationFilter, setLocationFilter] = useState('ALL');
  const [cropFilter, setCropFilter] = useState('ALL');
  const [selectedFarmer, setSelectedFarmer] = useState(null);

  useEffect(() => {
    getOfficerData().then(setData);
  }, []);

  const locations = useMemo(() => {
    if (!data) return [];
    return ['ALL', ...new Set(data.farmers.map(f => f.location))];
  }, [data]);

  const crops = useMemo(() => {
    if (!data) return [];
    return ['ALL', ...new Set(data.farmers.map(f => f.crop))];
  }, [data]);

  const filteredFarmers = useMemo(() => {
    if (!data) return [];
    let result = [...data.farmers];

    if (riskFilter !== 'ALL') {
      result = result.filter(f => getRiskCategory(f.riskScore) === riskFilter);
    }
    if (locationFilter !== 'ALL') {
      result = result.filter(f => f.location === locationFilter);
    }
    if (cropFilter !== 'ALL') {
      result = result.filter(f => f.crop === cropFilter);
    }

    result.sort((a, b) => b.riskScore - a.riskScore);
    return result;
  }, [data, riskFilter, locationFilter, cropFilter]);

  if (!data) return null;

  return (
    <div className="page-container officer-page">
      <div className="officer-header">
        <div className="officer-header-top">
          <h1><LayoutDashboard size={24} style={{ verticalAlign: 'middle', marginRight: 8 }} />Officer Dashboard</h1>
          <span className="officer-header-badge">Agriculture Officer</span>
        </div>
        <p>Monitor farmer distress levels and take proactive intervention</p>
      </div>

      <div className="officer-stats">
        <StatCard
          icon={Users}
          label="Total Farmers"
          value={data.stats.totalFarmers.toLocaleString()}
          color="var(--color-primary)"
        />
        <StatCard
          icon={AlertTriangle}
          label="High Risk"
          value={data.stats.highRisk}
          subtitle="Requires monitoring"
          color="var(--color-high)"
        />
        <StatCard
          icon={ShieldAlert}
          label="Critical Risk"
          value={data.stats.criticalRisk}
          subtitle="Immediate action needed"
          color="var(--color-critical)"
        />
        <StatCard
          icon={Bell}
          label="Alerts Today"
          value={data.stats.alertsToday}
          color="var(--color-warning)"
        />
      </div>

      <div className="officer-filters">
        <span className="officer-filter-label"><Filter size={16} /> Filters:</span>
        <select
          className="officer-filter-select"
          value={riskFilter}
          onChange={e => setRiskFilter(e.target.value)}
        >
          <option value="ALL">All Risk Levels</option>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="MEDIUM">Medium</option>
          <option value="LOW">Low</option>
        </select>
        <select
          className="officer-filter-select"
          value={locationFilter}
          onChange={e => setLocationFilter(e.target.value)}
        >
          {locations.map(loc => (
            <option key={loc} value={loc}>{loc === 'ALL' ? 'All Locations' : loc}</option>
          ))}
        </select>
        <select
          className="officer-filter-select"
          value={cropFilter}
          onChange={e => setCropFilter(e.target.value)}
        >
          {crops.map(crop => (
            <option key={crop} value={crop}>{crop === 'ALL' ? 'All Crops' : crop}</option>
          ))}
        </select>
      </div>

      <div className="officer-results-count">
        Showing {filteredFarmers.length} of {data.farmers.length} farmers
      </div>

      <div className="officer-farmer-list">
        {filteredFarmers.length > 0 ? (
          filteredFarmers.map(farmer => (
            <FarmerRiskCard
              key={farmer.id}
              farmer={farmer}
              onViewDetails={setSelectedFarmer}
            />
          ))
        ) : (
          <div className="officer-no-results">No farmers match the selected filters.</div>
        )}
      </div>

      {selectedFarmer && (
        <div className="farmer-detail-modal" onClick={() => setSelectedFarmer(null)}>
          <div className="farmer-detail-content" onClick={e => e.stopPropagation()}>
            <button className="farmer-detail-close" onClick={() => setSelectedFarmer(null)}>
              <X size={16} />
            </button>
            <h2>{selectedFarmer.name}</h2>
            <div className="farmer-detail-row">
              <span className="farmer-detail-label">Farmer ID</span>
              <span className="farmer-detail-value">{selectedFarmer.id}</span>
            </div>
            <div className="farmer-detail-row">
              <span className="farmer-detail-label">Location</span>
              <span className="farmer-detail-value">{selectedFarmer.location}</span>
            </div>
            <div className="farmer-detail-row">
              <span className="farmer-detail-label">Crop</span>
              <span className="farmer-detail-value">{selectedFarmer.crop}</span>
            </div>
            <div className="farmer-detail-row">
              <span className="farmer-detail-label">Risk Score</span>
              <span className="farmer-detail-value" style={{ color: getRiskColor(selectedFarmer.riskScore) }}>
                {selectedFarmer.riskScore} — {getRiskCategory(selectedFarmer.riskScore)}
              </span>
            </div>
            <div className="farmer-detail-row">
              <span className="farmer-detail-label">Risk Factors</span>
              <div className="farmer-detail-factors">
                {selectedFarmer.riskFactors.map((f, i) => (
                  <span key={i} className="farmer-detail-factor">{f}</span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
