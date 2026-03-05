const repository = require('../repositories/experience.repository');

function listExperienceItems() {
  return repository.listExperience();
}

function createExperienceItem(payload) {
  return repository.createExperience(payload);
}

module.exports = { listExperienceItems, createExperienceItem };
