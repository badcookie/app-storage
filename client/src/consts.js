const env = process.env.NODE_ENV || "development";

const apiHost = `${document.location.hostname}`;
const apiPort = 8000;

const apiAddress = `http://${apiHost}:${apiPort}`;

export const routes = {
  getApps: () => [apiAddress, "applications"].join("/").concat("/"),
  createApp: () => [apiAddress, "applications"].join("/").concat("/"),
  updateApp: id => [apiAddress, "applications", id].join("/").concat("/"),
  deleteApp: id => [apiAddress, "applications", id].join("/").concat("/"),
  visitApp: uid =>
    env === "development" ? `${apiHost}:9000/${uid}` : `${uid}.app-storage.xyz`
};

export const flowStates = {
  loading: "loading",
  ready: "ready",
  error: "error"
};
