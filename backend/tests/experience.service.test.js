const test = require('node:test');
const assert = require('node:assert/strict');
const service = require('../src/services/experience.service');

test('experience service scaffold', () => {
  const created = service.createExperienceItem({ name: 'sample' });
  assert.equal(created.id > 0, true);
  const items = service.listExperienceItems();
  assert.equal(Array.isArray(items), true);
});
