const experienceStore = [];

function listExperience() {
  return experienceStore;
}

function createExperience(payload) {
  const record = { id: experienceStore.length + 1, ...payload };
  experienceStore.push(record);
  return record;
}

module.exports = { listExperience, createExperience };
