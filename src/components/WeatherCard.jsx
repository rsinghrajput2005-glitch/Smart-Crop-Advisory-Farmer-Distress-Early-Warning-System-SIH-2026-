import { CloudRain, CloudLightning, CloudDrizzle, CloudSun, Sun, Droplets } from 'lucide-react';
import './WeatherCard.css';

const iconMap = {
  'cloud-rain': CloudRain,
  'cloud-lightning': CloudLightning,
  'cloud-drizzle': CloudDrizzle,
  'cloud-sun': CloudSun,
  'sun': Sun,
};

export default function WeatherCard({ day, date, tempHigh, tempLow, rainProbability, condition, icon }) {
  const WeatherIcon = iconMap[icon] || CloudSun;

  return (
    <div className="weather-card">
      <div className="weather-card-day">{day}</div>
      <div className="weather-card-date">{date}</div>
      <div className="weather-card-icon">
        <WeatherIcon size={32} />
      </div>
      <div className="weather-card-temp">
        {tempHigh}° <span>/ {tempLow}°</span>
      </div>
      <div className="weather-card-condition">{condition}</div>
      <div className="weather-card-rain">
        <Droplets size={14} />
        {rainProbability}%
      </div>
    </div>
  );
}
