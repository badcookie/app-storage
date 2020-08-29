import axios from "axios";
import React, { useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";

import { actions } from "../slices";

const handleAppRemove = (appId, removeApp) => () => {
  const url = `http://${document.location.hostname}:8000/applications/${appId}/`;
  axios
    .delete(url)
    .then(response => {
      removeApp(appId);
    })
    .catch(console.log);
};

const handleAppUpdate = appId => () => {};

const fetchApps = storeAppsCallback => () => {
  const url = `http://${document.location.hostname}:8000/applications/`;
  axios
    .get(url)
    .then(response => {
      const apps = response.data;
      console.log(apps);
      storeAppsCallback(apps);
    })
    .catch(console.log);
};

const getApps = state => state.apps;

const Applications = () => {
  const dispatch = useDispatch();

  const addApps = apps => dispatch(actions.apps.addApps(apps));
  const removeApp = appId => dispatch(actions.apps.removeApp(appId));

  useEffect(fetchApps(addApps), []);

  const apps = useSelector(getApps);

  if (apps.length === 0) {
    return <p>No apps yet</p>;
  }

  const appsList = (
    <ul>
      {apps.map(app => (
        <li key={app.id}>
          {app.uid} {app.port}
          <button onClick={handleAppRemove(app.id, removeApp)}>remove</button>
          <button onClick={handleAppUpdate(app.id)}>update</button>
        </li>
      ))}
    </ul>
  );

  return <div>{appsList}</div>;
};

export default Applications;
