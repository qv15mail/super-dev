const repository = require('../repositories/content.repository');

function listContentItems() {
  return repository.listContent();
}

function createContentItem(payload) {
  return repository.createContent(payload);
}

module.exports = { listContentItems, createContentItem };
