const analyticsStore = [];
let nextAnalyticsId = 1;

function listAnalytics() {
  return [...analyticsStore];
}

function createAnalytics(payload) {
  const { id, ...safePayload } = payload;
  const record = { id: nextAnalyticsId++, ...safePayload };
  analyticsStore.push(record);
  return record;
}

module.exports = { listAnalytics, createAnalytics };
