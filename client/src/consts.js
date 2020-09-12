const apiHost = `${document.location.hostname}`;
const apiPort = 8000;

const apiAddress = `http://${apiHost}:${apiPort}`;

export const routes = {
  getApps: () => [apiAddress, "applications"].join("/").concat("/"),
  createApp: () => [apiAddress, "applications"].join("/").concat("/"),
  updateApp: id => [apiAddress, "applications", id].join("/").concat("/"),
  deleteApp: id => [apiAddress, "applications", id].join("/").concat("/"),
  visitApp: port => [apiAddress, port].join(":").concat("/")
};

export const flowStates = {
  loading: "loading",
  ready: "ready",
  error: "error"
};
