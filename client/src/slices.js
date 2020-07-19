import { createSlice } from '@reduxjs/toolkit';


const appSlice = createSlice({
  name: 'apps',
  initialState: [],
  reducers: {
    addApps: (state, action) => {
        state.push(...action.payload);
    },
  },
});


const reducers = { apps: appSlice.reducer };

const actions = { apps: appSlice.actions };

export { reducers, actions };
