const contentStore = [];

function listContent() {
  return contentStore;
}

function createContent(payload) {
  const record = { id: contentStore.length + 1, ...payload };
  contentStore.push(record);
  return record;
}

module.exports = { listContent, createContent };
