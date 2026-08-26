import { useState, useEffect } from 'react';
import { Droplets, Wind, Thermometer, Sun, Eye, AlertTriangle, CloudSun, MapPin } from 'lucide-react';
import { getWeatherData } from '../services/api';
import WeatherCard from '../components/WeatherCard';
import './Weather.css';

export default function Weather() {
  const [weather, setWeather] = useState(null);

  useEffect(() => {
    getWeatherData().then(setWeather);
  }, []);

  if (!weather) return null;

  const { current, forecast, warning, location } = weather;

  return (
    <div className="page-container weather-page">
      <div className="page-header">
        <h1>Weather Forecast</h1>
        <p><MapPin size={16} style={{ verticalAlign: 'middle' }} /> {location}</p>
      </div>

      <div className="current-weather">
        <div className="current-weather-main">
          <div>
            <div className="current-weather-temp">
              {current.temperature}<span>°C</span>
            </div>
            <div className="current-weather-details">
              <h2>{current.condition}</h2>
              <p>Feels like {current.feelsLike}°C</p>
            </div>
          </div>
        </div>
        <div className="current-weather-stats">
          <div className="weather-stat">
            <div className="weather-stat-icon"><Droplets size={18} /></div>
            <div>
              <div className="weather-stat-label">Humidity</div>
              <div className="weather-stat-value">{current.humidity}%</div>
            </div>
          </div>
          <div className="weather-stat">
            <div className="weather-stat-icon"><CloudSun size={18} /></div>
            <div>
              <div className="weather-stat-label">Rainfall</div>
              <div className="weather-stat-value">{current.rainfall} mm</div>
            </div>
          </div>
          <div className="weather-stat">
            <div className="weather-stat-icon"><Wind size={18} /></div>
            <div>
              <div className="weather-stat-label">Wind</div>
              <div className="weather-stat-value">{current.windSpeed} km/h {current.windDirection}</div>
            </div>
          </div>
          <div className="weather-stat">
            <div className="weather-stat-icon"><Sun size={18} /></div>
            <div>
              <div className="weather-stat-label">UV Index</div>
              <div className="weather-stat-value">{current.uvIndex}</div>
            </div>
          </div>
        </div>
      </div>

      {warning && (
        <div className="weather-warning">
          <div className="weather-warning-icon">
            <AlertTriangle size={20} />
          </div>
          <div className="weather-warning-text">
            <h3>Weather Warning</h3>
            <p>{warning}</p>
          </div>
        </div>
      )}

      <div className="home-section">
        <h2 className="section-title"><CloudSun size={20} /> 5-Day Forecast</h2>
        <div className="forecast-grid">
          {forecast.map((day, i) => (
            <WeatherCard key={i} {...day} />
          ))}
        </div>
      </div>
    </div>
  );
}
