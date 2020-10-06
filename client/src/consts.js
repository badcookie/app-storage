import React from "react";

export const ClientContext = React.createContext(null);
export const clientUidHeader = "x-client";

const env = process.env.NODE_ENV || "development";

const apiPort = 8000;

const apiHost = `${document.location.hostname}`;
const apiAddress =
  env === "development" ? `http://${apiHost}:${apiPort}` : `http://${apiHost}`;

export const routes = {
  getApps: () => [apiAddress, "applications"].join("/").concat("/"),
  createApp: () => [apiAddress, "applications"].join("/").concat("/"),
  updateApp: id => [apiAddress, "applications", id].join("/").concat("/"),
  deleteApp: id => [apiAddress, "applications", id].join("/").concat("/"),
  visitApp: app =>
    env === "development"
      ? `http://${apiHost}:${app.port}/`
      : `http://${app.uid}.app-storage.xyz`,
  ws: () => `ws://${apiHost}:${apiPort}/ws/`
};

export const flowStates = {
  loading: "loading",
  ready: "ready",
  error: "error"
};
