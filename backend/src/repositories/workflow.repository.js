const workflowStore = [];
let nextWorkflowId = 1;

function listWorkflow() {
  return [...workflowStore];
}

function createWorkflow(payload) {
  const { id, ...safePayload } = payload;
  const record = { id: nextWorkflowId++, ...safePayload };
  workflowStore.push(record);
  return record;
}

module.exports = { listWorkflow, createWorkflow };
