const env = process.env.NODE_ENV || "development";

const apiHost = `${document.location.hostname}`;

const apiAddress = `http://${apiHost}`;

export const routes = {
  getApps: () => [apiAddress, "applications"].join("/").concat("/"),
  createApp: () => [apiAddress, "applications"].join("/").concat("/"),
  updateApp: id => [apiAddress, "applications", id].join("/").concat("/"),
  deleteApp: id => [apiAddress, "applications", id].join("/").concat("/"),
  visitApp: uid =>
    env === "development"
      ? `${apiAddress}:8888/${uid}`
      : `http://${uid}.app-storage.xyz`
};

export const flowStates = {
  loading: "loading",
  ready: "ready",
  error: "error"
};
