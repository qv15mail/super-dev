const profileStore = [];
let nextProfileId = 1;

function listProfile() {
  return [...profileStore];
}

function createProfile(payload) {
  const { id, ...safePayload } = payload;
  const record = { id: nextProfileId++, ...safePayload };
  profileStore.push(record);
  return record;
}

module.exports = { listProfile, createProfile };
