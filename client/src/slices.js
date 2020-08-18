import { createSlice } from '@reduxjs/toolkit';


const appSlice = createSlice({
  name: 'apps',
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
      return state.filter((app) => app.id !== appIdToRemove);
    },
  },
});


const reducers = { apps: appSlice.reducer };

const actions = { apps: appSlice.actions };

export { reducers, actions };
