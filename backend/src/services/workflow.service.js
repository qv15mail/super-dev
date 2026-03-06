const repository = require('../repositories/workflow.repository');

function listWorkflowItems() {
  return repository.listWorkflow();
}

function createWorkflowItem(payload) {
  return repository.createWorkflow(payload);
}

module.exports = { listWorkflowItems, createWorkflowItem };
