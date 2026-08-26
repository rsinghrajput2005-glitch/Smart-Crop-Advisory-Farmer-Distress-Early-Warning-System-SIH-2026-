import { farmerData, weatherData, advisoryData, mandiData, riskData, alertsData, officerData } from '../data/dummyData';

// Simulates async API calls. Replace internals with fetch() for FastAPI backend.
const delay = (ms = 100) => new Promise(resolve => setTimeout(resolve, ms));

export async function getFarmerData() {
  await delay();
  return farmerData;
}

export async function getWeatherData() {
  await delay();
  return weatherData;
}

export async function getAdvisoryData() {
  await delay();
  return advisoryData;
}

export async function getMandiData() {
  await delay();
  return mandiData;
}

export async function getRiskData() {
  await delay();
  return riskData;
}

export async function getAlertsData() {
  await delay();
  return alertsData;
}

export async function getOfficerData() {
  await delay();
  return officerData;
}
