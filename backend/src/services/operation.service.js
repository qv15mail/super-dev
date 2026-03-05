const repository = require('../repositories/operation.repository');

function listOperationItems() {
  return repository.listOperation();
}

function createOperationItem(payload) {
  return repository.createOperation(payload);
}

module.exports = { listOperationItems, createOperationItem };
