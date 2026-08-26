import { useState, useEffect } from 'react';
import { Sprout, AlertTriangle, CheckCircle, Droplets, Waves, SprayCan, Warehouse, Eye } from 'lucide-react';
import { getAdvisoryData } from '../services/api';
import AdvisoryCard from '../components/AdvisoryCard';
import './CropAdvisory.css';

const actionIconMap = {
  'droplets-off': Droplets,
  'waves': Waves,
  'spray-can': SprayCan,
  'warehouse': Warehouse,
  'eye': Eye,
};

export default function CropAdvisory() {
  const [advisory, setAdvisory] = useState(null);

  useEffect(() => {
    getAdvisoryData().then(setAdvisory);
  }, []);

  if (!advisory) return null;

  return (
    <div className="page-container advisory-page">
      <div className="page-header">
        <h1>Crop Advisory</h1>
        <p>Personalized recommendations for your crop</p>
      </div>

      <div className="advisory-hero">
        <div className="advisory-hero-icon">
          <Sprout size={32} />
        </div>
        <div className="advisory-hero-content">
          <div className="crop-info">
            <span className="crop-name">{advisory.crop}</span>
            <span className="growth-stage">{advisory.growthStage}</span>
          </div>
          <p>Advisory generated based on current weather conditions and crop growth stage</p>
        </div>
      </div>

      <div className="advisory-recommendation">
        <div className="advisory-recommendation-header">
          <div className={`rec-icon priority-${advisory.priority}`}>
            <AlertTriangle size={24} />
          </div>
          <span className={`badge badge-${advisory.priority === 'HIGH' ? 'critical' : advisory.priority === 'MEDIUM' ? 'high' : 'low'}`}>
            {advisory.priority} Priority
          </span>
        </div>
        <h2>{advisory.recommendation}</h2>
        <div className="explanation">{advisory.explanation}</div>
      </div>

      <div className="advisory-actions-section">
        <h2 className="section-title"><CheckCircle size={20} /> Today's Actions</h2>
        {advisory.actions.map(action => {
          const Icon = actionIconMap[action.icon] || CheckCircle;
          return (
            <AdvisoryCard
              key={action.id}
              text={action.text}
              priority={action.priority}
              icon={Icon}
            />
          );
        })}
      </div>

      <div className="advisory-warnings">
        <h3><AlertTriangle size={18} /> Important Warnings</h3>
        <ul className="advisory-warning-list">
          {advisory.warnings.map((warning, i) => (
            <li key={i}>
              <span className="warning-bullet"><AlertTriangle size={12} /></span>
              {warning}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
