import React from "react";
import ReactDOM from "react-dom";
import { v4 as uuidv4 } from "uuid";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";

import App from "./components/App";
import { reducers, actions } from "./slices";
import { routes, ClientContext } from "./consts";

export default () => {
  const store = configureStore({ reducer: reducers });

  const clientUid = uuidv4();

  const baseWsRoute = routes.ws();
  const clientWsRoute = `${baseWsRoute}?client=${clientUid}`;
  const ws = new WebSocket(clientWsRoute);

  const setFlowDetail = detail => {
    store.dispatch(actions.flowState.setDetail(detail));
  };

  ws.onmessage = event => {
    setFlowDetail(event.data);
  };

  const mountNode = document.getElementById("root");
  ReactDOM.render(
    <Provider store={store}>
      <ClientContext.Provider value={clientUid}>
        <App />
      </ClientContext.Provider>
      ,
    </Provider>,
    mountNode
  );
};
