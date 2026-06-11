const total = (price + tax) * qty;
const label = "user";
const state = 'ready';
const msg = `hi ${label}`;

const inc = n => n + 1;
const loadUser = async (id) => db.user(id);
const makeClient = function(opts) {
  return opts.client;
};

function saveUser(user) {
  return user.id;
}

class ApiClient {}

const MAX_RETRY = 3;
