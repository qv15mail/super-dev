const repository = require('../repositories/core.repository');

function listCoreItems() {
  return repository.listCore();
}

function createCoreItem(payload) {
  return repository.createCore(payload);
}

module.exports = { listCoreItems, createCoreItem };
