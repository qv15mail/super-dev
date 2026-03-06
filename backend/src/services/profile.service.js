const repository = require('../repositories/profile.repository');

function listProfileItems() {
  return repository.listProfile();
}

function createProfileItem(payload) {
  return repository.createProfile(payload);
}

module.exports = { listProfileItems, createProfileItem };
