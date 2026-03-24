const operationStore = [];
let nextOperationId = 1;

function listOperation() {
  return [...operationStore];
}

function createOperation(payload) {
  const { id, ...safePayload } = payload;
  const record = { id: nextOperationId++, ...safePayload };
  operationStore.push(record);
  return record;
}

module.exports = { listOperation, createOperation };
