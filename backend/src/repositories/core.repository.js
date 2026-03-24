const coreStore = [];
let nextCoreId = 1;

function listCore() {
  return [...coreStore];
}

function createCore(payload) {
  const { id, ...safePayload } = payload;
  const record = { id: nextCoreId++, ...safePayload };
  coreStore.push(record);
  return record;
}

module.exports = { listCore, createCore };
