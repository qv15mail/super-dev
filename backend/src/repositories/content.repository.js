const contentStore = [];
let nextContentId = 1;

function listContent() {
  return [...contentStore];
}

function createContent(payload) {
  const { id, ...safePayload } = payload;
  const record = { id: nextContentId++, ...safePayload };
  contentStore.push(record);
  return record;
}

module.exports = { listContent, createContent };
