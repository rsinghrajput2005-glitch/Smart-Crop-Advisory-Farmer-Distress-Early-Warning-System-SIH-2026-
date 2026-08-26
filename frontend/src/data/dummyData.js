export const farmerData = {
  id: 'F001',
  name: 'Ramesh Kumar',
  location: 'Deoria',
  district: 'Deoria',
  state: 'Uttar Pradesh',
  crop: 'Wheat',
  growthStage: 'Flowering',
  farmSize: '4.5 acres',
  soilType: 'Alluvial'
};

export const weatherData = {
  location: 'Deoria, Uttar Pradesh',
  current: {
    temperature: 32,
    humidity: 78,
    rainfall: 12.5,
    condition: 'Partly Cloudy',
    windSpeed: 14,
    windDirection: 'NW',
    feelsLike: 35,
    uvIndex: 6
  },
  forecast: [
    { day: 'Mon', date: 'Aug 25', tempHigh: 33, tempLow: 24, rainProbability: 80, condition: 'Heavy Rain', icon: 'cloud-rain' },
    { day: 'Tue', date: 'Aug 26', tempHigh: 30, tempLow: 23, rainProbability: 65, condition: 'Thunderstorm', icon: 'cloud-lightning' },
    { day: 'Wed', date: 'Aug 27', tempHigh: 31, tempLow: 24, rainProbability: 40, condition: 'Light Rain', icon: 'cloud-drizzle' },
    { day: 'Thu', date: 'Aug 28', tempHigh: 33, tempLow: 25, rainProbability: 20, condition: 'Partly Cloudy', icon: 'cloud-sun' },
    { day: 'Fri', date: 'Aug 29', tempHigh: 34, tempLow: 25, rainProbability: 10, condition: 'Sunny', icon: 'sun' }
  ],
  warning: 'Heavy rainfall expected in next 24-48 hours. Possible waterlogging in low-lying areas.'
};

export const advisoryData = {
  crop: 'Wheat',
  growthStage: 'Flowering',
  priority: 'HIGH',
  recommendation: 'Do not irrigate today',
  explanation: 'Heavy rainfall is expected in the next 24 hours. Additional irrigation will cause waterlogging and may damage the crop during the flowering stage. Wait for rainfall to pass before resuming irrigation.',
  actions: [
    { id: 1, text: 'Stop all irrigation systems', priority: 'HIGH', icon: 'droplets-off' },
    { id: 2, text: 'Ensure proper drainage channels are clear', priority: 'HIGH', icon: 'waves' },
    { id: 3, text: 'Apply preventive fungicide spray if possible before rain', priority: 'MEDIUM', icon: 'spray-can' },
    { id: 4, text: 'Secure harvested produce in dry storage', priority: 'MEDIUM', icon: 'warehouse' },
    { id: 5, text: 'Monitor crop for signs of lodging after rain', priority: 'LOW', icon: 'eye' }
  ],
  warnings: [
    'Do not spray pesticides during rain — it will wash away and waste money',
    'Avoid entering waterlogged fields — risk of soil compaction',
    'Check crop insurance status before the storm'
  ]
};

export const mandiData = [
  { id: 1, name: 'Deoria Mandi', distance: 5, pricePerQuintal: 2250, lastUpdated: '2 hours ago', trend: 'stable' },
  { id: 2, name: 'Gorakhpur Mandi', distance: 52, pricePerQuintal: 2380, lastUpdated: '1 hour ago', trend: 'up' },
  { id: 3, name: 'Kushinagar Mandi', distance: 38, pricePerQuintal: 2310, lastUpdated: '3 hours ago', trend: 'down' },
  { id: 4, name: 'Ballia Mandi', distance: 74, pricePerQuintal: 2290, lastUpdated: '4 hours ago', trend: 'stable' },
  { id: 5, name: 'Azamgarh Mandi', distance: 95, pricePerQuintal: 2340, lastUpdated: '2 hours ago', trend: 'up' }
];

export const riskData = {
  overallScore: 84,
  factors: [
    { name: 'Rainfall Risk', score: 24, description: 'Heavy rainfall predicted in next 48 hours may cause waterlogging and crop damage', icon: 'cloud-rain' },
    { name: 'Price Crash Risk', score: 22, description: 'Market prices showing downward trend. MSP may not cover production costs', icon: 'trending-down' },
    { name: 'Crop Loss Risk', score: 18, description: 'Flowering stage is vulnerable to heavy rain and strong winds', icon: 'wheat' },
    { name: 'Financial Risk', score: 17, description: 'Outstanding crop loan of ₹1.2L with repayment due in 45 days', icon: 'indian-rupee' },
    { name: 'Weather Risk', score: 3, description: 'Temperature within acceptable range for current growth stage', icon: 'thermometer' }
  ]
};

export const alertsData = [
  { id: 1, type: 'warning', title: 'Heavy Rainfall Alert', message: 'Heavy rainfall expected in next 24 hours. Irrigation is not recommended today.', timestamp: '30 min ago', priority: 'HIGH' },
  { id: 2, type: 'danger', title: 'Crop Insurance Reminder', message: 'Your crop insurance policy expires in 15 days. Renew before the deadline.', timestamp: '2 hours ago', priority: 'MEDIUM' },
  { id: 3, type: 'info', title: 'MSP Update', message: 'Minimum Support Price for Wheat has been revised to ₹2275/quintal for this season.', timestamp: '1 day ago', priority: 'LOW' }
];

export const officerData = {
  stats: {
    totalFarmers: 1247,
    highRisk: 89,
    criticalRisk: 23,
    alertsToday: 156
  },
  farmers: [
    { id: 'F001', name: 'Ramesh Kumar', location: 'Deoria', crop: 'Wheat', riskScore: 84, riskFactors: ['Heavy rainfall', 'Price crash', 'Crop loss'] },
    { id: 'F002', name: 'Sunil Yadav', location: 'Gorakhpur', crop: 'Rice', riskScore: 91, riskFactors: ['Flood warning', 'Pest outbreak', 'Loan default'] },
    { id: 'F003', name: 'Priya Devi', location: 'Kushinagar', crop: 'Sugarcane', riskScore: 72, riskFactors: ['Water stress', 'Price decline'] },
    { id: 'F004', name: 'Anil Sharma', location: 'Deoria', crop: 'Wheat', riskScore: 67, riskFactors: ['Rainfall risk', 'Financial stress'] },
    { id: 'F005', name: 'Meera Singh', location: 'Ballia', crop: 'Rice', riskScore: 45, riskFactors: ['Moderate pest risk'] },
    { id: 'F006', name: 'Vikram Patel', location: 'Gorakhpur', crop: 'Wheat', riskScore: 38, riskFactors: ['Minor weather concern'] },
    { id: 'F007', name: 'Lakshmi Devi', location: 'Azamgarh', crop: 'Mustard', riskScore: 88, riskFactors: ['Frost warning', 'Price crash', 'Crop disease'] },
    { id: 'F008', name: 'Rajesh Tiwari', location: 'Kushinagar', crop: 'Rice', riskScore: 55, riskFactors: ['Moderate rainfall', 'Storage issues'] },
    { id: 'F009', name: 'Sita Ram', location: 'Deoria', crop: 'Sugarcane', riskScore: 29, riskFactors: ['Low risk overall'] },
    { id: 'F010', name: 'Manoj Gupta', location: 'Ballia', crop: 'Wheat', riskScore: 76, riskFactors: ['Heavy rainfall', 'Pest outbreak'] },
    { id: 'F011', name: 'Kavita Kumari', location: 'Azamgarh', crop: 'Rice', riskScore: 93, riskFactors: ['Flood damage', 'Total crop loss', 'Loan default'] },
    { id: 'F012', name: 'Deepak Verma', location: 'Gorakhpur', crop: 'Mustard', riskScore: 18, riskFactors: ['Minimal risk'] }
  ]
};
