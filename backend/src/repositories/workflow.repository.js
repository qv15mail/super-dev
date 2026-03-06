const workflowStore = [];

function listWorkflow() {
  return workflowStore;
}

function createWorkflow(payload) {
  const record = { id: workflowStore.length + 1, ...payload };
  workflowStore.push(record);
  return record;
}

module.exports = { listWorkflow, createWorkflow };
