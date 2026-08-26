import { AlertTriangle, AlertCircle, Info } from 'lucide-react';
import './AlertCard.css';

const iconMap = {
  warning: AlertTriangle,
  danger: AlertCircle,
  info: Info,
};

export default function AlertCard({ type = 'info', title, message, timestamp }) {
  const Icon = iconMap[type] || Info;

  return (
    <div className={`alert-card alert-${type}`}>
      <div className="alert-card-icon">
        <Icon size={18} />
      </div>
      <div className="alert-card-content">
        <div className="alert-card-title">{title}</div>
        <div className="alert-card-message">{message}</div>
        {timestamp && <div className="alert-card-time">{timestamp}</div>}
      </div>
    </div>
  );
}
