/**
 * KrishiMitra — Smart Crop Advisory & Farmer Distress Early-Warning System
 * SIH 2026 | Frontend Application
 *
 * Features:
 *  - SPA routing (sidebar navigation, no page reload)
 *  - Parallel API calls (advisory, risk, weather, mandi)
 *  - Animated SVG risk gauge
 *  - 5-day weather forecast cards
 *  - Multi-mandi price comparison chart (Chart.js)
 *  - Multilingual TTS (Web Speech API) in 6 Indian languages
 *  - Voice input (SpeechRecognition API)
 *  - Rule-based chatbot with typing animation
 *  - Officer dashboard with alert management
 *  - GPS auto-detect
 */

const API_BASE = 'http://localhost:8000';

// ── State ────────────────────────────────────────────────────────────────────
const state = {
    currentPage: 'home',
    language: 'en',
    lastData: { advisory: null, risk: null, weather: null, mandi: null },
    alerts: [],
    reviewedCount: 0,
    mandiChart: null,
    listening: false,
    speechSynth: window.speechSynthesis,
    voices: [],
};

// ── Language configs ─────────────────────────────────────────────────────────
const LANG_CONFIG = {
    en: { name: 'English',   bcp: 'en-IN',  voiceHint: 'en-IN' },
    hi: { name: 'Hindi',     bcp: 'hi-IN',  voiceHint: 'hi-IN' },
    te: { name: 'Telugu',    bcp: 'te-IN',  voiceHint: 'te-IN' },
    ta: { name: 'Tamil',     bcp: 'ta-IN',  voiceHint: 'ta-IN' },
    bn: { name: 'Bengali',   bcp: 'bn-IN',  voiceHint: 'bn-IN' },
    mr: { name: 'Marathi',   bcp: 'mr-IN',  voiceHint: 'mr-IN' },
    or: { name: 'Odia',      bcp: 'or-IN',  voiceHint: 'en-IN' }, // Odia TTS falls back to en-IN
};

// ── Page titles ──────────────────────────────────────────────────────────────
const PAGE_TITLES = {
    home:     'Farmer Home',
    weather:  'Weather Conditions',
    advisory: 'AI Crop Advisory',
    mandi:    'Mandi Market Prices',
    risk:     'Farmer Distress Risk',
    officer:  'Officer Dashboard',
    chatbot:  'Advisory Chatbot',
};

// ── Weather icon mapping ─────────────────────────────────────────────────────
function weatherIcon(condition = '') {
    const c = condition.toLowerCase();
    if (c.includes('thunder')) return '⛈️';
    if (c.includes('drizzle')) return '🌦️';
    if (c.includes('rain') || c.includes('shower')) return '🌧️';
    if (c.includes('snow')) return '❄️';
    if (c.includes('fog') || c.includes('haze')) return '🌫️';
    if (c.includes('cloud') || c.includes('overcast')) return '☁️';
    if (c.includes('partly')) return '⛅';
    if (c.includes('clear') || c.includes('sunny')) return '☀️';
    return '🌤️';
}

// ═══════════════════════════════════════════════════════════════════
// INIT
// ═══════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    initNav();
    initForm();
    initGPS();
    initChat();
    initOfficerFilters();
    initTTS();
    loadVoices();
    checkAPIStatus();
});

// ═══════════════════════════════════════════════════════════════════
// NAVIGATION
// ═══════════════════════════════════════════════════════════════════

function initNav() {
    // Sidebar nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', e => {
            e.preventDefault();
            navigateTo(item.dataset.page);
        });
    });

    // Sidebar toggle (mobile)
    document.getElementById('sidebar-toggle').addEventListener('click', () => {
        document.getElementById('sidebar').classList.toggle('open');
    });

    // Close sidebar on page click (mobile)
    document.querySelector('.main-content').addEventListener('click', () => {
        document.getElementById('sidebar').classList.remove('open');
    });

    // Language select
    document.getElementById('lang-select').addEventListener('change', e => {
        state.language = e.target.value;
    });

    // Officer dashboard button from risk page
    document.getElementById('view-officer-btn')?.addEventListener('click', () => {
        navigateTo('officer');
    });
}

function navigateTo(page) {
    // Update active nav item
    document.querySelectorAll('.nav-item').forEach(el => {
        el.classList.toggle('active', el.dataset.page === page);
    });

    // Show/hide pages
    document.querySelectorAll('.page').forEach(el => {
        el.classList.toggle('active', el.id === `page-${page}`);
    });

    // Update topbar title
    document.getElementById('page-title').textContent = PAGE_TITLES[page] || page;

    state.currentPage = page;
}

// ═══════════════════════════════════════════════════════════════════
// FORM SUBMISSION
// ═══════════════════════════════════════════════════════════════════

function initForm() {
    document.getElementById('advisory-form').addEventListener('submit', async e => {
        e.preventDefault();
        await runAnalysis();
    });
}

async function runAnalysis() {
    const lat = parseFloat(document.getElementById('lat').value);
    const lon = parseFloat(document.getElementById('lon').value);
    const location = document.getElementById('location-name').value;
    const crop = document.getElementById('crop').value;
    const growthStage = document.getElementById('growth-stage').value;
    const stateFilter = document.getElementById('state-filter').value;

    // Show loading overlay
    setLoadingState(true);

    try {
        // Fire all 4 API calls concurrently
        const [advisory, risk, weather, mandi] = await Promise.all([
            fetchAdvisory(lat, lon, crop, growthStage),
            fetchRisk(lat, lon, crop, growthStage),
            fetchWeather(lat, lon),
            fetchMandi(crop, stateFilter),
        ]);

        state.lastData = { advisory, risk, weather, mandi };

        // Populate all pages
        populateWeather(weather);
        populateAdvisory(advisory, crop, growthStage);
        populateMandi(mandi);
        populateRisk(risk, location, crop);

        // Check if high risk — add to officer dashboard
        if (risk && (risk.risk_level === 'High' || risk.risk_level === 'Medium')) {
            addOfficerAlert(risk, location, crop, lat, lon);
        }

        showToast('✅ Farm analysis complete!');

        // Navigate to advisory page automatically
        navigateTo('advisory');

    } catch (err) {
        console.error(err);
        showToast('❌ Error connecting to API. Check if backend is running.');
    } finally {
        setLoadingState(false);
    }
}

function setLoadingState(loading) {
    const overlay = document.getElementById('loading-overlay');
    const btn = document.getElementById('submit-btn');
    const spinner = document.getElementById('submit-spinner');
    const label = document.getElementById('submit-label');

    if (loading) {
        overlay.classList.remove('hidden');
        btn.disabled = true;
        spinner.classList.remove('hidden');
        label.textContent = 'Analyzing...';
        animateLoadingSteps();
    } else {
        overlay.classList.add('hidden');
        btn.disabled = false;
        spinner.classList.add('hidden');
        label.textContent = '🔍 Analyze My Farm';
    }
}

function animateLoadingSteps() {
    const steps = ['step-soil', 'step-weather', 'step-ndvi', 'step-mandi', 'step-ai'];
    steps.forEach((id, i) => {
        const el = document.getElementById(id);
        if (!el) return;
        el.className = 'loading-step';
        setTimeout(() => {
            el.className = 'loading-step active';
            setTimeout(() => el.className = 'loading-step done', 600);
        }, i * 500);
    });
}

// ═══════════════════════════════════════════════════════════════════
// API CALLS
// ═══════════════════════════════════════════════════════════════════

async function fetchAdvisory(lat, lon, crop, growth_stage) {
    const res = await fetch(`${API_BASE}/advisory`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lat, lon, crop, growth_stage }),
    });
    if (!res.ok) throw new Error(`Advisory API ${res.status}`);
    return res.json();
}

async function fetchRisk(lat, lon, crop, growth_stage) {
    const res = await fetch(`${API_BASE}/risk`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lat, lon, crop, growth_stage, mandi_commodity: crop }),
    });
    if (!res.ok) throw new Error(`Risk API ${res.status}`);
    return res.json();
}

async function fetchWeather(lat, lon) {
    const res = await fetch(`${API_BASE}/weather/?lat=${lat}&lon=${lon}`);
    if (!res.ok) throw new Error(`Weather API ${res.status}`);
    return res.json();
}

async function fetchMandi(commodity, state) {
    const res = await fetch(`${API_BASE}/mandi/prices?commodity=${encodeURIComponent(commodity)}&state=${encodeURIComponent(state)}&days_back=7`);
    if (!res.ok) throw new Error(`Mandi API ${res.status}`);
    return res.json();
}

async function fetchChat(message, crop, growth_stage) {
    const res = await fetch(`${API_BASE}/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, language: state.language, crop, growth_stage }),
    });
    if (!res.ok) throw new Error(`Chat API ${res.status}`);
    return res.json();
}

// ═══════════════════════════════════════════════════════════════════
// POPULATE: WEATHER
// ═══════════════════════════════════════════════════════════════════

function populateWeather(weather) {
    if (!weather) return;

    const cur = weather.current || {};
    const forecast = weather.forecast || [];
    const riskData = weather.weather_risk || {};

    // Current weather card
    const card = document.getElementById('weather-current-card');
    const temp = cur.temperature_c ?? '--';
    const cond = cur.condition || cur.description || 'Unknown';
    const humidity = cur.humidity_pct ?? '--';
    const wind = cur.wind_speed_kmh ?? '--';
    const feels = cur.feels_like_c ?? '--';
    const pressure = cur.pressure_hpa ?? '--';

    card.innerHTML = `
        <div class="weather-main-display">
            <div class="weather-temp-big">${typeof temp === 'number' ? temp.toFixed(1) : temp}°C</div>
            <div class="weather-meta">
                <h3>${weatherIcon(cond)} ${cond}</h3>
                <p>Feels like ${typeof feels === 'number' ? feels.toFixed(1) : feels}°C · ${cur.city || weather.source || 'Current Location'}</p>
                <p style="margin-top:6px;font-size:0.8rem;color:var(--text-muted);">Source: ${weather.source || 'API'}</p>
            </div>
        </div>
        <div class="weather-stats-row">
            <div class="w-stat">
                <div class="w-stat-value" style="color:#60a5fa">💧 ${humidity}%</div>
                <div class="w-stat-label">Humidity</div>
            </div>
            <div class="w-stat">
                <div class="w-stat-value" style="color:#818cf8">💨 ${wind} km/h</div>
                <div class="w-stat-label">Wind Speed</div>
            </div>
            <div class="w-stat">
                <div class="w-stat-value" style="color:#f59e0b">🌧️ ${cur.rainfall_mm ?? cur.precipitation_mm ?? 0} mm</div>
                <div class="w-stat-label">Current Rain</div>
            </div>
            <div class="w-stat">
                <div class="w-stat-value" style="color:#a78bfa">📊 ${pressure} hPa</div>
                <div class="w-stat-label">Pressure</div>
            </div>
        </div>
    `;

    // Forecast cards
    const fGrid = document.getElementById('forecast-grid');
    fGrid.innerHTML = forecast.map(day => {
        const dayName = new Date(day.date).toLocaleDateString('en-IN', { weekday: 'short', month: 'short', day: 'numeric' });
        const rain = day.rainfall_mm ?? day.rain_sum_mm ?? day.precipitation_sum_mm ?? 0;
        const tMax = day.temp_max_c ?? day.temp_max ?? '--';
        const tMin = day.temp_min_c ?? day.temp_min ?? '--';
        const dc = day.condition || day.description || '';
        return `
            <div class="forecast-day-card">
                <div class="forecast-date">${dayName}</div>
                <div class="forecast-icon">${weatherIcon(dc)}</div>
                <div class="forecast-temp">
                    ${typeof tMax === 'number' ? tMax.toFixed(0) : tMax}° 
                    <span class="temp-min">/ ${typeof tMin === 'number' ? tMin.toFixed(0) : tMin}°</span>
                </div>
                <div class="forecast-rain">🌧 ${typeof rain === 'number' ? rain.toFixed(1) : rain} mm</div>
            </div>
        `;
    }).join('');

    // Weather risk panel
    const panel = document.getElementById('weather-risk-panel');
    const riskLevel = riskData.risk_level || 'Unknown';
    const riskColor = riskLevel === 'High' ? 'var(--risk-high)' :
                     riskLevel === 'Medium' ? 'var(--risk-medium)' : 'var(--risk-low)';
    const factors = riskData.risk_factors || ['No significant weather risks detected.'];
    panel.innerHTML = `
        <h3>🌩 Agricultural Weather Risk: 
            <span style="color:${riskColor};font-weight:700;">${riskLevel}</span>
        </h3>
        <div style="margin-top:12px;">
            ${factors.map(f => `
                <div class="risk-factor-item">
                    <span class="factor-icon">⚡</span>
                    <span>${f}</span>
                </div>
            `).join('')}
        </div>
    `;
}

// ═══════════════════════════════════════════════════════════════════
// POPULATE: CROP ADVISORY
// ═══════════════════════════════════════════════════════════════════

function populateAdvisory(advisory, crop, stage) {
    if (!advisory) return;

    const mainCard = document.getElementById('advisory-main-card');
    const ndviCard = document.getElementById('ndvi-card');
    const soilCard = document.getElementById('soil-card');

    const advisoryText = advisory.advisory || 'Advisory not available.';
    const soil = advisory.soil_summary || {};
    const ndviCond = advisory.ndvi_condition || 'Unknown';
    const weather = advisory.weather_summary || {};

    mainCard.innerHTML = `
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">
            <div style="width:40px;height:40px;background:var(--emerald-glow);border:1px solid var(--border-accent);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.3rem;">🚜</div>
            <div>
                <h3 style="font-size:1rem;font-weight:700;">${capitalize(crop)} — ${capitalize(stage.replace('_', ' '))}</h3>
                <p style="font-size:0.8rem;color:var(--text-muted);">AI-Generated Advisory</p>
            </div>
            <button class="tts-btn" style="margin-left:auto;" onclick="speakText('${advisoryText.replace(/'/g, "\\'")}')">🔊 Read</button>
        </div>
        <div class="advisory-text-box">${advisoryText}</div>
        <div class="advisory-meta">
            <div class="meta-item">
                <div class="meta-label">Temperature</div>
                <div class="meta-value">${weather.temperature_c ?? '--'}°C</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Forecast Rain</div>
                <div class="meta-value">${weather.rainfall_mm !== undefined ? Number(weather.rainfall_mm).toFixed(1) : '--'} mm</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Crop Condition</div>
                <div class="meta-value" style="color:var(--emerald)">${ndviCond}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Soil pH</div>
                <div class="meta-value">${soil.ph ?? '--'}</div>
            </div>
        </div>
    `;

    // NDVI card — mock value shown here, real from advisory.ndvi_condition
    const ndviMap = {
        'Dense / Very Healthy Vegetation': 0.78,
        'Healthy Crop': 0.62,
        'Moderate Vegetation': 0.44,
        'Bare Soil / Sparse Vegetation': 0.18,
        'Water / Non-vegetated': 0.05,
    };
    const ndviVal = ndviMap[ndviCond] ?? 0.5;
    const ndviColor = ndviVal >= 0.6 ? 'var(--risk-low)' : ndviVal >= 0.4 ? 'var(--risk-medium)' : 'var(--risk-high)';

    ndviCard.innerHTML = `
        <h4 style="font-size:0.85rem;font-weight:600;margin-bottom:12px;">🛰️ NDVI Vegetation Index</h4>
        <div class="ndvi-value-display">
            <div class="ndvi-big" style="color:${ndviColor}">${ndviVal.toFixed(2)}</div>
            <div style="font-size:0.8rem;color:var(--text-muted);margin-top:4px;">${ndviCond}</div>
        </div>
        <div class="ndvi-bar-outer">
            <div class="ndvi-bar-inner" style="width:${ndviVal * 100}%"></div>
        </div>
        <p style="font-size:0.72rem;color:var(--text-muted);text-align:center;">Scale: 0 (bare) → 1 (dense)</p>
    `;

    soilCard.innerHTML = `
        <h4 style="font-size:0.85rem;font-weight:600;margin-bottom:12px;">🌍 Soil Profile</h4>
        <div class="data-grid">
            <div class="data-row-item">
                <span class="drk">pH Level</span>
                <span class="drv" style="color:${getSoilPhColor(soil.ph)}">${soil.ph ?? 'N/A'}</span>
            </div>
            <div class="data-row-item">
                <span class="drk">Organic Carbon</span>
                <span class="drv">${soil.organic_carbon ? soil.organic_carbon + ' g/kg' : 'N/A'}</span>
            </div>
            <div class="data-row-item">
                <span class="drk">Data Source</span>
                <span class="drv" style="font-size:0.75rem;color:var(--text-muted)">SoilGrids ISRIC</span>
            </div>
        </div>
    `;
}

function getSoilPhColor(ph) {
    if (!ph) return 'var(--text-secondary)';
    if (ph < 5.5) return 'var(--risk-high)';
    if (ph < 6.0) return 'var(--risk-medium)';
    if (ph <= 7.5) return 'var(--risk-low)';
    return 'var(--risk-medium)';
}

// ═══════════════════════════════════════════════════════════════════
// POPULATE: MANDI
// ═══════════════════════════════════════════════════════════════════

function populateMandi(mandi) {
    if (!mandi) return;

    const summary = mandi.summary || {};
    const priceTrend = mandi.price_trend || {};
    const records = mandi.records || [];

    // Summary stat cards
    const summaryRow = document.getElementById('mandi-summary-row');
    const trendClass = getTrendClass(priceTrend.trend);
    summaryRow.innerHTML = `
        <div class="mandi-stat-card">
            <div class="mandi-stat-value">₹${summary.avg_modal_price ? Math.round(summary.avg_modal_price).toLocaleString('en-IN') : '--'}</div>
            <div class="mandi-stat-label">Avg Modal Price / Quintal</div>
        </div>
        <div class="mandi-stat-card">
            <div class="mandi-stat-value" style="color:var(--risk-low)">₹${summary.min_modal_price ? Math.round(summary.min_modal_price).toLocaleString('en-IN') : '--'}</div>
            <div class="mandi-stat-label">Minimum Price / Q</div>
        </div>
        <div class="mandi-stat-card">
            <div class="mandi-stat-value" style="color:var(--amber)">₹${summary.max_modal_price ? Math.round(summary.max_modal_price).toLocaleString('en-IN') : '--'}</div>
            <div class="mandi-stat-label">Maximum Price / Q</div>
        </div>
        <div class="mandi-stat-card">
            <div class="mandi-stat-value">${summary.num_markets ?? '--'}</div>
            <div class="mandi-stat-label">Mandis Compared</div>
            <div class="mandi-trend-badge ${trendClass}">${priceTrend.trend || 'N/A'}</div>
            ${priceTrend.change_pct != null ? `<div style="font-size:0.75rem;color:var(--text-muted);margin-top:4px;">${priceTrend.change_pct > 0 ? '+' : ''}${priceTrend.change_pct?.toFixed(1)}% (7-day)</div>` : ''}
        </div>
    `;

    // Table
    const tbody = document.getElementById('mandi-tbody');
    // Deduplicate by mandi name, taking the most recent
    const latestByMandi = {};
    records.forEach(r => {
        const key = r.mandi_name || r.market;
        if (!latestByMandi[key] || r.arrival_date > latestByMandi[key].arrival_date) {
            latestByMandi[key] = r;
        }
    });
    const tableRecords = Object.values(latestByMandi);

    if (tableRecords.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty-cell">No mandi data available.</td></tr>';
    } else {
        tbody.innerHTML = tableRecords.map(r => `
            <tr>
                <td><strong>${r.mandi_name || r.market || 'N/A'}</strong><br><small style="color:var(--text-muted)">${r.district || r.state || ''}</small></td>
                <td>${r.variety || 'Local'}</td>
                <td>₹${r.min_price ? Math.round(r.min_price).toLocaleString('en-IN') : '--'}</td>
                <td class="modal-price">₹${r.modal_price ? Math.round(r.modal_price).toLocaleString('en-IN') : '--'}</td>
                <td>₹${r.max_price ? Math.round(r.max_price).toLocaleString('en-IN') : '--'}</td>
                <td style="color:var(--text-muted)">${r.arrival_date || '--'}</td>
            </tr>
        `).join('');
    }

    // Chart
    buildMandiChart(tableRecords);
}

function getTrendClass(trend = '') {
    if (trend.includes('Sharply Falling')) return 'trend-sharp-fall';
    if (trend.includes('Falling')) return 'trend-falling';
    if (trend.includes('Sharply Rising')) return 'trend-sharp-rise';
    if (trend.includes('Rising')) return 'trend-rising';
    return 'trend-stable';
}

function buildMandiChart(records) {
    const canvas = document.getElementById('mandi-chart');
    if (!canvas) return;
    if (state.mandiChart) { state.mandiChart.destroy(); state.mandiChart = null; }

    if (records.length === 0) return;

    const labels = records.map(r => (r.mandi_name || r.market || '').split(' ')[0]);
    const minPrices   = records.map(r => r.min_price || 0);
    const modalPrices = records.map(r => r.modal_price || 0);
    const maxPrices   = records.map(r => r.max_price || 0);

    state.mandiChart = new Chart(canvas, {
        type: 'bar',
        data: {
            labels,
            datasets: [
                {
                    label: 'Min Price',
                    data: minPrices,
                    backgroundColor: 'rgba(239, 68, 68, 0.4)',
                    borderColor: '#ef4444',
                    borderWidth: 1,
                    borderRadius: 4,
                },
                {
                    label: 'Modal Price',
                    data: modalPrices,
                    backgroundColor: 'rgba(16, 217, 127, 0.5)',
                    borderColor: '#10d97f',
                    borderWidth: 1,
                    borderRadius: 4,
                },
                {
                    label: 'Max Price',
                    data: maxPrices,
                    backgroundColor: 'rgba(245, 158, 11, 0.4)',
                    borderColor: '#f59e0b',
                    borderWidth: 1,
                    borderRadius: 4,
                },
            ],
        },
        options: {
            responsive: true,
            plugins: {
                legend: { labels: { color: '#a8b4d0', font: { size: 11 } } },
                tooltip: {
                    callbacks: {
                        label: ctx => `${ctx.dataset.label}: ₹${ctx.parsed.y.toLocaleString('en-IN')}/Q`,
                    },
                },
            },
            scales: {
                x: {
                    ticks: { color: '#5a6b8a', font: { size: 10 } },
                    grid: { color: 'rgba(255,255,255,0.04)' },
                },
                y: {
                    ticks: { color: '#5a6b8a', font: { size: 10 }, callback: v => '₹' + v.toLocaleString('en-IN') },
                    grid: { color: 'rgba(255,255,255,0.04)' },
                },
            },
        },
    });
}

// ═══════════════════════════════════════════════════════════════════
// POPULATE: RISK
// ═══════════════════════════════════════════════════════════════════

function populateRisk(risk, location, crop) {
    if (!risk) return;

    const level = risk.risk_level || 'Unknown';
    const score = risk.risk_score ?? 0;
    const factors = risk.risk_factors || [];

    // Animate gauge
    animateGauge(score, level);

    // Risk level badge
    const badge = document.getElementById('risk-level-badge');
    badge.textContent = level.toUpperCase();
    badge.className = `risk-level-badge badge-${level.toLowerCase()}`;

    // Risk indicators (color coded based on factors)
    const priceDistress = factors.some(f => f.toLowerCase().includes('price'));
    const weatherBad    = factors.some(f => f.toLowerCase().includes('weather'));
    const ndviBad       = factors.some(f => f.toLowerCase().includes('ndvi'));
    const rainBad       = factors.some(f => f.toLowerCase().includes('rainfall') || f.toLowerCase().includes('drought'));

    setIndicator('ind-ndvi',    ndviBad   ? level : 'Low');
    setIndicator('ind-weather', weatherBad ? level : 'Low');
    setIndicator('ind-price',   priceDistress ? level : 'Low');
    setIndicator('ind-rain',    rainBad   ? level : 'Low');

    // Risk factors list
    const list = document.getElementById('risk-factors-list');
    if (factors.length === 0) {
        list.innerHTML = '<li class="empty-factor">No significant risk factors detected.</li>';
    } else {
        list.innerHTML = factors.map(f => `
            <li class="risk-factor-li ${level.toLowerCase()}">
                <span>⚡</span>
                <span>${f}</span>
            </li>
        `).join('');
    }

    // Officer alert panel
    const alertPanel = document.getElementById('officer-alert-panel');
    if (level === 'High') {
        alertPanel.classList.remove('hidden');
    } else {
        alertPanel.classList.add('hidden');
    }
}

function animateGauge(score, level) {
    const arc = document.getElementById('gauge-arc');
    const scoreText = document.getElementById('gauge-score-text');
    if (!arc || !scoreText) return;

    // Arc total length ≈ 283 (half-circle)
    const totalLength = 283;
    const fillRatio = Math.min(score / 10, 1);
    const dashArr = `${fillRatio * totalLength} ${totalLength}`;

    const color = level === 'High' ? '#ef4444' : level === 'Medium' ? '#f59e0b' : '#10d97f';
    arc.style.stroke = color;
    arc.style.strokeDasharray = dashArr;
    arc.style.filter = `drop-shadow(0 0 8px ${color}60)`;

    // Animate score counter
    let current = 0;
    const target = score;
    const step = target / 30;
    const timer = setInterval(() => {
        current = Math.min(current + step, target);
        scoreText.textContent = current.toFixed(1);
        if (current >= target) clearInterval(timer);
    }, 30);
}

function setIndicator(id, level) {
    const el = document.getElementById(id);
    if (!el) return;
    el.className = 'indicator-dot dot-' + level.toLowerCase();
}

// ═══════════════════════════════════════════════════════════════════
// OFFICER DASHBOARD
// ═══════════════════════════════════════════════════════════════════

function addOfficerAlert(risk, location, crop, lat, lon) {
    const alert = {
        id: Date.now(),
        location,
        lat, lon,
        crop: capitalize(crop),
        riskLevel: risk.risk_level,
        riskScore: risk.risk_score,
        factors: risk.risk_factors || [],
        timestamp: new Date().toLocaleString('en-IN'),
        reviewed: false,
    };

    state.alerts.unshift(alert);
    renderOfficerTable();
    updateOfficerStats();
    updateOfficerBadge();
}

function renderOfficerTable(filter = 'all', search = '') {
    const tbody = document.getElementById('officer-tbody');
    if (!tbody) return;

    let alerts = state.alerts;
    if (filter !== 'all') alerts = alerts.filter(a => a.riskLevel === filter);
    if (search) {
        const q = search.toLowerCase();
        alerts = alerts.filter(a =>
            a.location.toLowerCase().includes(q) ||
            a.crop.toLowerCase().includes(q)
        );
    }

    if (alerts.length === 0) {
        tbody.innerHTML = `
            <tr><td colspan="7" class="empty-cell">
                <div class="empty-state">
                    <span>✅</span>
                    <p>No alerts match the current filter.</p>
                </div>
            </td></tr>
        `;
        return;
    }

    tbody.innerHTML = alerts.map(a => {
        const rowClass = `row-${a.riskLevel.toLowerCase()}`;
        const badgeClass = `badge-risk-${a.riskLevel.toLowerCase()}`;
        const reviewedClass = a.reviewed ? 'reviewed' : '';
        return `
            <tr class="${rowClass}">
                <td>
                    <strong>${a.location}</strong><br>
                    <small style="color:var(--text-muted)">${a.lat}, ${a.lon}</small>
                </td>
                <td>${a.crop}</td>
                <td><span class="risk-badge ${badgeClass}">${a.riskLevel.toUpperCase()}</span></td>
                <td><strong>${a.riskScore}/10</strong></td>
                <td style="max-width:260px;"><small style="color:var(--text-muted)">${a.factors.join(' · ')}</small></td>
                <td style="color:var(--text-muted);font-size:0.78rem">${a.timestamp}</td>
                <td>
                    <button class="review-btn ${reviewedClass}" 
                            onclick="markReviewed(${a.id})" 
                            ${a.reviewed ? 'disabled' : ''}>
                        ${a.reviewed ? '✅ Reviewed' : 'Review Case'}
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function markReviewed(id) {
    const alert = state.alerts.find(a => a.id === id);
    if (alert) {
        alert.reviewed = true;
        state.reviewedCount++;
        renderOfficerTable(
            document.getElementById('officer-filter')?.value,
            document.getElementById('officer-search')?.value
        );
        updateOfficerStats();
        showToast('✅ Case marked as reviewed');
    }
}

function updateOfficerStats() {
    const total  = state.alerts.length;
    const high   = state.alerts.filter(a => a.riskLevel === 'High').length;
    const medium = state.alerts.filter(a => a.riskLevel === 'Medium').length;
    const rev    = state.alerts.filter(a => a.reviewed).length;

    document.getElementById('stat-total').textContent   = total;
    document.getElementById('stat-high').textContent    = high;
    document.getElementById('stat-medium').textContent  = medium;
    document.getElementById('stat-reviewed').textContent= rev;
}

function updateOfficerBadge() {
    const badge = document.getElementById('officer-badge');
    if (!badge) return;
    const unreviewed = state.alerts.filter(a => !a.reviewed).length;
    if (unreviewed > 0) {
        badge.textContent = unreviewed;
        badge.classList.remove('hidden');
    } else {
        badge.classList.add('hidden');
    }
}

function initOfficerFilters() {
    document.getElementById('officer-search')?.addEventListener('input', e => {
        renderOfficerTable(document.getElementById('officer-filter').value, e.target.value);
    });

    document.getElementById('officer-filter')?.addEventListener('change', e => {
        renderOfficerTable(e.target.value, document.getElementById('officer-search').value);
    });
}

// ═══════════════════════════════════════════════════════════════════
// CHATBOT
// ═══════════════════════════════════════════════════════════════════

function initChat() {
    const input  = document.getElementById('chat-input');
    const sendBtn= document.getElementById('send-btn');
    const voiceBtn=document.getElementById('voice-btn');

    sendBtn?.addEventListener('click', () => sendChatMessage());
    input?.addEventListener('keypress', e => { if (e.key === 'Enter') sendChatMessage(); });

    // Suggestion chips
    document.querySelectorAll('.suggestion-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            input.value = chip.dataset.msg;
            sendChatMessage();
        });
    });

    // Voice input
    voiceBtn?.addEventListener('click', () => toggleVoiceInput());
}

async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const msg = input.value.trim();
    if (!msg) return;

    input.value = '';
    appendChatMessage(msg, 'user');

    // Show typing indicator
    const typingId = showTypingIndicator();

    try {
        const crop = document.getElementById('crop')?.value;
        const stage = document.getElementById('growth-stage')?.value;
        const data = await fetchChat(msg, crop, stage);
        removeTypingIndicator(typingId);
        appendChatMessage(data.response, 'bot');
        // TTS: speak the response
        speakText(data.response);
    } catch (err) {
        removeTypingIndicator(typingId);
        appendChatMessage(
            'Sorry, I could not connect to the advisory service. Please make sure the backend server is running.',
            'bot'
        );
    }
}

function appendChatMessage(text, role) {
    const window_ = document.getElementById('chat-window');
    const div = document.createElement('div');
    div.className = `chat-message ${role === 'user' ? 'user-message' : 'bot-message'}`;

    const time = new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
    const avatar = role === 'user' ? '👨‍🌾' : '🌾';

    div.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-bubble">
            <p>${text.replace(/\n/g, '<br>').replace(/\|/g, '<br>• ')}</p>
            <p class="msg-time">${time}</p>
        </div>
    `;
    window_.appendChild(div);
    window_.scrollTop = window_.scrollHeight;
}

function showTypingIndicator() {
    const window_ = document.getElementById('chat-window');
    const id = 'typing-' + Date.now();
    const div = document.createElement('div');
    div.className = 'chat-message bot-message typing-indicator';
    div.id = id;
    div.innerHTML = `
        <div class="message-avatar">🌾</div>
        <div class="message-bubble">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
        </div>
    `;
    window_.appendChild(div);
    window_.scrollTop = window_.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    document.getElementById(id)?.remove();
}

// ═══════════════════════════════════════════════════════════════════
// VOICE INPUT (SpeechRecognition)
// ═══════════════════════════════════════════════════════════════════

function toggleVoiceInput() {
    if (!('SpeechRecognition' in window) && !('webkitSpeechRecognition' in window)) {
        showToast('⚠️ Voice input not supported in this browser. Try Chrome.');
        return;
    }

    if (state.listening) {
        state.recognition?.stop();
        return;
    }

    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    const rec = new SpeechRec();
    state.recognition = rec;

    const lang = LANG_CONFIG[state.language];
    rec.lang = lang?.bcp || 'en-IN';
    rec.continuous = false;
    rec.interimResults = false;

    rec.onstart = () => {
        state.listening = true;
        document.getElementById('voice-btn').classList.add('listening');
        document.getElementById('voice-status').classList.remove('hidden');
    };

    rec.onresult = e => {
        const transcript = e.results[0][0].transcript;
        document.getElementById('chat-input').value = transcript;
        sendChatMessage();
    };

    rec.onerror = () => showToast('⚠️ Voice input error. Please try again.');

    rec.onend = () => {
        state.listening = false;
        document.getElementById('voice-btn').classList.remove('listening');
        document.getElementById('voice-status').classList.add('hidden');
    };

    rec.start();
}

// ═══════════════════════════════════════════════════════════════════
// TEXT-TO-SPEECH
// ═══════════════════════════════════════════════════════════════════

function initTTS() {
    document.getElementById('tts-btn')?.addEventListener('click', () => {
        speakCurrentPage();
    });
}

function loadVoices() {
    const loadV = () => { state.voices = state.speechSynth?.getVoices() || []; };
    loadV();
    state.speechSynth?.addEventListener?.('voiceschanged', loadV);
}

function speakText(text) {
    if (!state.speechSynth) return;
    state.speechSynth.cancel();

    const utter = new SpeechSynthesisUtterance(text);
    const langCode = LANG_CONFIG[state.language]?.bcp || 'en-IN';

    // Try to find a matching voice
    const matchedVoice = state.voices.find(v => v.lang === langCode) ||
                         state.voices.find(v => v.lang.startsWith(langCode.split('-')[0])) ||
                         state.voices.find(v => v.lang.includes('IN'));

    if (matchedVoice) utter.voice = matchedVoice;
    utter.lang = langCode;
    utter.rate = 0.9;
    utter.pitch = 1.0;

    state.speechSynth.speak(utter);
}

function speakCurrentPage() {
    let textToSpeak = '';
    const data = state.lastData;

    switch (state.currentPage) {
        case 'advisory':
            textToSpeak = data.advisory?.advisory || 'No advisory data available.';
            break;
        case 'weather':
            const cur = data.weather?.current;
            if (cur) {
                textToSpeak = `Current weather: ${cur.temperature_c} degrees Celsius. Condition: ${cur.condition || cur.description}. Humidity: ${cur.humidity_pct} percent. Wind: ${cur.wind_speed_kmh} kilometers per hour.`;
            }
            break;
        case 'risk':
            textToSpeak = `Farmer distress risk level is ${data.risk?.risk_level}. Score is ${data.risk?.risk_score} out of 10. Risk factors: ${(data.risk?.risk_factors || []).join('. ')}`;
            break;
        case 'mandi':
            const sum = data.mandi?.summary;
            if (sum) {
                textToSpeak = `Average modal price for your crop is ${Math.round(sum.avg_modal_price)} rupees per quintal. Price trend is ${data.mandi?.price_trend?.trend}.`;
            }
            break;
        default:
            textToSpeak = 'KrishiMitra: Smart Crop Advisory System. Submit your farm details to get personalized advisory.';
    }

    speakText(textToSpeak);
}

// ═══════════════════════════════════════════════════════════════════
// GPS DETECTION
// ═══════════════════════════════════════════════════════════════════

function initGPS() {
    document.getElementById('gps-btn')?.addEventListener('click', () => {
        if (!navigator.geolocation) {
            showToast('⚠️ Geolocation not supported in this browser.');
            return;
        }
        const btn = document.getElementById('gps-btn');
        btn.textContent = '📡 Detecting...';
        btn.disabled = true;

        navigator.geolocation.getCurrentPosition(
            pos => {
                document.getElementById('lat').value = pos.coords.latitude.toFixed(6);
                document.getElementById('lon').value = pos.coords.longitude.toFixed(6);
                document.getElementById('location-name').value = `${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)}`;
                btn.textContent = '✅ Location Set';
                setTimeout(() => { btn.textContent = '📡 Detect Location'; btn.disabled = false; }, 2000);
                showToast('📍 Location detected!');
            },
            err => {
                btn.textContent = '📡 Detect Location';
                btn.disabled = false;
                showToast('⚠️ Could not get location. Check browser permissions.');
            },
            { timeout: 10000, enableHighAccuracy: true }
        );
    });
}

// ═══════════════════════════════════════════════════════════════════
// API STATUS CHECK
// ═══════════════════════════════════════════════════════════════════

async function checkAPIStatus() {
    try {
        const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(5000) });
        if (res.ok) {
            const dot = document.querySelector('.status-dot');
            if (dot) {
                dot.style.background = 'var(--risk-low)';
                dot.style.boxShadow = '0 0 6px var(--risk-low)';
            }
            document.querySelector('.status-indicator span:last-child').textContent = 'API Online';
        }
    } catch {
        const dot = document.querySelector('.status-dot');
        if (dot) {
            dot.style.background = 'var(--risk-high)';
            dot.style.boxShadow = '0 0 6px var(--risk-high)';
        }
        document.querySelector('.status-indicator span:last-child').textContent = 'API Offline';
    }
}

// ═══════════════════════════════════════════════════════════════════
// UTILITIES
// ═══════════════════════════════════════════════════════════════════

function showToast(msg, duration = 3500) {
    const toast = document.getElementById('toast');
    const toastMsg = document.getElementById('toast-msg');
    if (!toast || !toastMsg) return;
    toastMsg.textContent = msg;
    toast.classList.remove('hidden');
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => toast.classList.add('hidden'), duration);
}

function capitalize(str = '') {
    return str.charAt(0).toUpperCase() + str.slice(1).replace(/_/g, ' ');
}

// Expose markReviewed globally for onclick in dynamic HTML
window.markReviewed = markReviewed;
window.speakText = speakText;
