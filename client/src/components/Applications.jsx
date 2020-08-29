import axios from "axios";
import React, { useEffect } from "react";
import { ListGroup, Card, Button } from "react-bootstrap";
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

const fetchApps = addApps => () => {
  const url = `http://${document.location.hostname}:8000/applications/`;
  axios
    .get(url)
    .then(response => {
      const apps = response.data;
      addApps(apps);
    })
    .catch(console.log);
};

const getApps = state => state.apps;

const renderApps = (apps, removeApp) => {
  if (apps.length === 0) {
    return <Card body>No apps yet.</Card>;
  }

  return (
    <ListGroup variant="flush">
      {apps.map(app => (
        <ListGroup.Item key={app.id}>
          {app.uid} {app.port}
          <button onClick={handleAppRemove(app.id, removeApp)}>remove</button>
          <button onClick={handleAppUpdate(app.id)}>update</button>
        </ListGroup.Item>
      ))}
    </ListGroup>
  );
};

const Applications = () => {
  const dispatch = useDispatch();

  const addApps = apps => dispatch(actions.apps.addApps(apps));
  const removeApp = appId => dispatch(actions.apps.removeApp(appId));

  useEffect(fetchApps(addApps), []);

  const apps = useSelector(getApps);

  const breadcrumbs = (
    <div className="d-flex">
      <span className="pl-2 lead text-bottom">Applications</span>
      <Button variant="secondary" className="ml-auto">
        +
      </Button>
    </div>
  );

  return (
    <>
      {breadcrumbs}
      <div className="mt-2">{renderApps(apps, removeApp)}</div>
    </>
  );
};

export default Applications;
