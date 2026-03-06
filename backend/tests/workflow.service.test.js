const test = require('node:test');
const assert = require('node:assert/strict');
const service = require('../src/services/workflow.service');

test('workflow service scaffold', () => {
  const created = service.createWorkflowItem({ name: 'sample' });
  assert.equal(created.id > 0, true);
  const items = service.listWorkflowItems();
  assert.equal(Array.isArray(items), true);
});
