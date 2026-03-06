const profileStore = [];

function listProfile() {
  return profileStore;
}

function createProfile(payload) {
  const record = { id: profileStore.length + 1, ...payload };
  profileStore.push(record);
  return record;
}

module.exports = { listProfile, createProfile };
