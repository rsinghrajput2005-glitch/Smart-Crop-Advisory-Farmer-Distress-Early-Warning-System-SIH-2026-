import { Store, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { formatPrice } from '../utils/helpers';
import './MandiRow.css';

const trendIcons = {
  up: TrendingUp,
  down: TrendingDown,
  stable: Minus,
};

export default function MandiRow({ name, distance, pricePerQuintal, isBest, lastUpdated, trend }) {
  const TrendIcon = trendIcons[trend] || Minus;

  return (
    <div className={`mandi-row ${isBest ? 'mandi-best' : ''}`}>
      <div className="mandi-row-info">
        <div className="mandi-row-icon">
          <Store size={20} />
        </div>
        <div>
          <div className="mandi-row-name">{name}</div>
          <div className="mandi-row-distance">{distance} km away</div>
          {lastUpdated && <div className="mandi-row-meta">Updated {lastUpdated}</div>}
        </div>
      </div>
      <div className="mandi-row-price-section">
        <div>
          <div className="mandi-row-price">
            {formatPrice(pricePerQuintal)}<span className="mandi-row-unit">/q</span>
          </div>
          <div className={`mandi-row-trend trend-${trend}`}>
            <TrendIcon size={14} />
            {trend === 'up' ? 'Rising' : trend === 'down' ? 'Falling' : 'Stable'}
          </div>
        </div>
        {isBest && <span className="mandi-best-badge">Best Price</span>}
      </div>
    </div>
  );
}
