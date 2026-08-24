import { MapPin, Wheat, Eye } from 'lucide-react';
import { getRiskCategory, getRiskColor, getRiskColorClass } from '../utils/helpers';
import './FarmerRiskCard.css';

export default function FarmerRiskCard({ farmer, onViewDetails }) {
  const category = getRiskCategory(farmer.riskScore);
  const color = getRiskColor(farmer.riskScore);
  const colorClass = getRiskColorClass(farmer.riskScore);

  return (
    <div className={`farmer-risk-card risk-border-${category.toLowerCase()}`}>
      <div className="farmer-risk-info">
        <div className="farmer-risk-name">{farmer.name}</div>
        <div className="farmer-risk-meta">
          <span><MapPin size={14} /> {farmer.location}</span>
          <span><Wheat size={14} /> {farmer.crop}</span>
        </div>
        <div className="farmer-risk-factors">
          {farmer.riskFactors.map((factor, i) => (
            <span key={i} className="farmer-risk-factor-tag">{factor}</span>
          ))}
        </div>
      </div>
      <div className="farmer-risk-score-section">
        <div className={`farmer-risk-score-value ${colorClass}`}>{farmer.riskScore}</div>
        <span className={`badge badge-${category.toLowerCase()}`}>{category}</span>
        <button className="farmer-risk-action" onClick={() => onViewDetails && onViewDetails(farmer)}>
          <Eye size={14} style={{ marginRight: 4, verticalAlign: 'middle' }} />
          View
        </button>
      </div>
    </div>
  );
}
