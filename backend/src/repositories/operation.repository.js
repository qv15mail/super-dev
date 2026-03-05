const operationStore = [];

function listOperation() {
  return operationStore;
}

function createOperation(payload) {
  const record = { id: operationStore.length + 1, ...payload };
  operationStore.push(record);
  return record;
}

module.exports = { listOperation, createOperation };
