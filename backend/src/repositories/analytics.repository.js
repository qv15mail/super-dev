const analyticsStore = [];

function listAnalytics() {
  return analyticsStore;
}

function createAnalytics(payload) {
  const record = { id: analyticsStore.length + 1, ...payload };
  analyticsStore.push(record);
  return record;
}

module.exports = { listAnalytics, createAnalytics };
