import { createSlice } from "@reduxjs/toolkit";

import { flowStates } from "./consts";

const appSlice = createSlice({
  name: "apps",
  initialState: [],
  reducers: {
    addApps: (state, action) => {
      state.push(...action.payload);
    },
    addApp: (state, action) => {
      state.push(action.payload);
    },
    removeApp: (state, action) => {
      const appIdToRemove = action.payload;
      return state.filter(app => app.id !== appIdToRemove);
    },
    updateApp: (state, action) => {
      const appIdToUpdate = action.payload.id;
      const app = state.find(({ id }) => id === appIdToUpdate);

      const newAppsState = state.filter(app => app.id !== appIdToUpdate);
      const updatedApp = { ...app, ...action.payload };
      newAppsState.push(updatedApp);

      return newAppsState;
    }
  }
});

const flowStateSlice = createSlice({
  name: "flowState",
  initialState: flowStates.loading,
  reducers: {
    setState: (state, action) => action.payload
  }
});

const errorSlice = createSlice({
  name: "errorInfo",
  initialState: null,
  reducers: {
    setErrorInfo: (state, action) => action.payload
  }
});

const modalInfoSlice = createSlice({
  name: "modalInfo",
  initialState: { type: null, app: null, createDb: false },
  reducers: {
    setModalInfo: (state, action) => ({ ...state, ...action.payload }),
    hideModal: () => ({ type: null, app: null, createDb: false })
  }
});

const reducers = {
  apps: appSlice.reducer,
  flowState: flowStateSlice.reducer,
  modalInfo: modalInfoSlice.reducer,
  errorInfo: errorSlice.reducer
};

const actions = {
  apps: appSlice.actions,
  flowState: flowStateSlice.actions,
  modalInfo: modalInfoSlice.actions,
  errorInfo: errorSlice.actions
};

export { reducers, actions };
