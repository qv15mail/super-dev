const coreStore = [];

function listCore() {
  return coreStore;
}

function createCore(payload) {
  const record = { id: coreStore.length + 1, ...payload };
  coreStore.push(record);
  return record;
}

module.exports = { listCore, createCore };
