const experienceStore = [];
let nextExperienceId = 1;

function listExperience() {
  return [...experienceStore];
}

function createExperience(payload) {
  const { id, ...safePayload } = payload;
  const record = { id: nextExperienceId++, ...safePayload };
  experienceStore.push(record);
  return record;
}

module.exports = { listExperience, createExperience };
