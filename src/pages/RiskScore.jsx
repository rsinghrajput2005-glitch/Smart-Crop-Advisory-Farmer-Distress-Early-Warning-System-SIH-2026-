import { useState, useEffect } from 'react';
import { ShieldAlert, CloudRain, TrendingDown, Wheat, IndianRupee, Thermometer } from 'lucide-react';
import { getRiskData, getFarmerData } from '../services/api';
import { getRiskCategory, getRiskColor, getRiskColorClass } from '../utils/helpers';
import RiskGauge from '../components/RiskGauge';
import './RiskScore.css';

const factorIconMap = {
  'cloud-rain': CloudRain,
  'trending-down': TrendingDown,
  'wheat': Wheat,
  'indian-rupee': IndianRupee,
  'thermometer': Thermometer,
};

export default function RiskScore() {
  const [risk, setRisk] = useState(null);
  const [farmer, setFarmer] = useState(null);

  useEffect(() => {
    Promise.all([getRiskData(), getFarmerData()]).then(([r, f]) => {
      setRisk(r);
      setFarmer(f);
    });
  }, []);

  if (!risk || !farmer) return null;

  const category = getRiskCategory(risk.overallScore);
  const color = getRiskColor(risk.overallScore);

  return (
    <div className="page-container risk-page">
      <div className="page-header">
        <h1>Risk Assessment</h1>
        <p>Comprehensive risk analysis for {farmer.name}'s farm</p>
      </div>

      <div className="risk-hero">
        <RiskGauge score={risk.overallScore} />
        <div className="risk-hero-text">
          <h2>Your Farm Risk Level: <span style={{ color }}>{category}</span></h2>
          <p>
            Your farm in {farmer.location} is currently at a {category.toLowerCase()} risk level
            with an overall score of {risk.overallScore}/100. This score is calculated based on
            multiple factors including weather conditions, market prices, crop health, and financial status.
          </p>
          <div className="risk-thresholds">
            <div className="risk-threshold">
              <span className="risk-threshold-dot" style={{ background: 'var(--color-low)' }} />
              0–30 Low
            </div>
            <div className="risk-threshold">
              <span className="risk-threshold-dot" style={{ background: 'var(--color-medium)' }} />
              31–60 Medium
            </div>
            <div className="risk-threshold">
              <span className="risk-threshold-dot" style={{ background: 'var(--color-high)' }} />
              61–80 High
            </div>
            <div className="risk-threshold">
              <span className="risk-threshold-dot" style={{ background: 'var(--color-critical)' }} />
              81–100 Critical
            </div>
          </div>
        </div>
      </div>

      <div className="risk-factors-section">
        <h2 className="section-title"><ShieldAlert size={20} /> Risk Factors</h2>
        {risk.factors.map((factor, i) => {
          const Icon = factorIconMap[factor.icon] || ShieldAlert;
          const factorColor = getRiskColor(factor.score * 4);
          return (
            <div key={i} className="risk-factor-card">
              <div className="risk-factor-icon" style={{ background: `${factorColor}18`, color: factorColor }}>
                <Icon size={22} />
              </div>
              <div className="risk-factor-content">
                <div className="risk-factor-header">
                  <span className="risk-factor-name">{factor.name}</span>
                  <span className="risk-factor-score" style={{ color: factorColor }}>{factor.score}</span>
                </div>
                <div className="risk-factor-bar">
                  <div
                    className="risk-factor-bar-fill"
                    style={{ width: `${(factor.score / 25) * 100}%`, background: factorColor }}
                  />
                </div>
                <div className="risk-factor-desc">{factor.description}</div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="risk-summary-card">
        <div className="risk-summary-header">
          <h3>Score Breakdown</h3>
          <span className={`badge badge-${category.toLowerCase()}`}>{category}</span>
        </div>
        <div className="risk-summary-rows">
          {risk.factors.map((factor, i) => (
            <div key={i} className="risk-summary-row">
              <span className="risk-summary-row-name">{factor.name}</span>
              <span className="risk-summary-row-score">{factor.score}</span>
            </div>
          ))}
        </div>
        <hr className="risk-summary-divider" />
        <div className="risk-summary-total-row">
          <span>Total Risk Score</span>
          <span style={{ color }}>{risk.overallScore}</span>
        </div>
      </div>
    </div>
  );
}
