import { CheckCircle } from 'lucide-react';
import './AdvisoryCard.css';

export default function AdvisoryCard({ text, priority, icon: Icon = CheckCircle }) {
  return (
    <div className="advisory-card">
      <div className="advisory-card-icon">
        <Icon size={20} />
      </div>
      <div className="advisory-card-content">
        <div className="advisory-card-header">
          <span className="advisory-card-text">{text}</span>
          <span className={`advisory-card-priority priority-${priority}`}>{priority}</span>
        </div>
      </div>
    </div>
  );
}
