import { createSlice } from "@reduxjs/toolkit";

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
    }
  }
});

const modalInfoSlice = createSlice({
  name: "modalInfo",
  initialState: { type: null, item: null },
  reducers: {
    setModalInfo: (state, action) => action.payload
  }
});

const reducers = {
  apps: appSlice.reducer,
  modalInfo: modalInfoSlice.reducer
};

const actions = {
  apps: appSlice.actions,
  modalInfo: modalInfoSlice.actions
};

export { reducers, actions };
