import { getRiskCategory, getRiskColor, getRiskColorClass } from '../utils/helpers';
import './RiskGauge.css';

export default function RiskGauge({ score, size = 'normal' }) {
  const category = getRiskCategory(score);
  const color = getRiskColor(score);
  const colorClass = getRiskColorClass(score);

  const isSmall = size === 'small';
  const circleSize = isSmall ? 100 : 180;
  const radius = isSmall ? 40 : 72;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const center = circleSize / 2;

  return (
    <div className={`risk-gauge ${isSmall ? 'risk-gauge-small' : ''}`}>
      <div className="risk-gauge-circle">
        <svg viewBox={`0 0 ${circleSize} ${circleSize}`}>
          <circle className="gauge-bg" cx={center} cy={center} r={radius} />
          <circle
            className="gauge-fill"
            cx={center}
            cy={center}
            r={radius}
            stroke={color}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
          />
        </svg>
        <div className="risk-gauge-value">
          <div className="risk-gauge-score" style={{ color }}>{score}</div>
          <div className="risk-gauge-max">/ 100</div>
        </div>
      </div>
      <span
        className={`risk-gauge-category badge badge-${category.toLowerCase()}`}
      >
        {category}
      </span>
    </div>
  );
}
