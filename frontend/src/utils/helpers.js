export function getRiskCategory(score) {
  if (score <= 30) return 'LOW';
  if (score <= 60) return 'MEDIUM';
  if (score <= 80) return 'HIGH';
  return 'CRITICAL';
}

export function getRiskColor(score) {
  if (score <= 30) return 'var(--color-low)';
  if (score <= 60) return 'var(--color-medium)';
  if (score <= 80) return 'var(--color-high)';
  return 'var(--color-critical)';
}

export function getRiskColorClass(score) {
  if (score <= 30) return 'risk-low';
  if (score <= 60) return 'risk-medium';
  if (score <= 80) return 'risk-high';
  return 'risk-critical';
}

export function getBestMandi(mandis) {
  return mandis.reduce((best, mandi) =>
    mandi.pricePerQuintal > best.pricePerQuintal ? mandi : best
  , mandis[0]);
}

export function formatPrice(price) {
  return `₹${price.toLocaleString('en-IN')}`;
}

export function getPriorityColor(priority) {
  switch (priority) {
    case 'HIGH': return 'var(--color-danger)';
    case 'MEDIUM': return 'var(--color-warning)';
    case 'LOW': return 'var(--color-success)';
    default: return 'var(--color-info)';
  }
}
