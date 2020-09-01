import axios from "axios";
import React, { useEffect } from "react";
import { Card, Button } from "react-bootstrap";
import { useSelector, useDispatch } from "react-redux";

import { actions } from "../slices";

const fetchApps = addApps => () => {
  const url = `http://localhost:8000/applications/`;
  axios
    .get(url)
    .then(response => {
      const apps = response.data;
      addApps(apps);
    })
    .catch(console.log);
};

const getApps = ({ apps }) => apps;

const renderSingleApp = props => app => {
  const appName = app.name || app.uid;
  const appDescription = app.description || "No description";

  return (
    <Card key={app.id} className="mb-2">
      <Card.Header className="d-flex">
        <span className="d-inline-flex align-items-center">{appName}</span>
        <Button
          variant="success"
          href={`http://${document.location.hostname}:${app.port}`}
          target="_blank"
          className="ml-auto mr-1"
        >
          Visit
        </Button>
        <Button
          variant="primary"
          onClick={props.handleUpdate(app)}
          className="mr-1"
        >
          Update
        </Button>
        <Button variant="danger" onClick={props.handleRemove(app)}>
          Remove
        </Button>
      </Card.Header>
      <Card.Body>
        <Card.Text>
          <span className="text-muted">{appDescription}</span>
        </Card.Text>
      </Card.Body>
    </Card>
  );
};

const renderApps = (apps, appManagementTools) => {
  if (apps.length === 0) {
    return <Card body>No apps yet.</Card>;
  }

  const renderApp = renderSingleApp(appManagementTools);
  return <div>{apps.map(renderApp)}</div>;
};

const Applications = () => {
  const dispatch = useDispatch();
  const addApps = apps => dispatch(actions.apps.addApps(apps));
  const setModalInfo = info => dispatch(actions.modalInfo.setModalInfo(info));

  const handleAppAdd = () => setModalInfo({ type: "add" });

  const appManagementTools = {
    handleRemove: app => () => setModalInfo({ type: "remove", app }),
    handleUpdate: app => () => setModalInfo({ type: "update", app })
  };

  useEffect(fetchApps(addApps), []);

  const apps = useSelector(getApps);

  return (
    <>
      <div className="d-flex">
        <span className="pl-2 lead text-bottom">Applications</span>
        <Button variant="secondary" className="ml-auto" onClick={handleAppAdd}>
          +
        </Button>
      </div>
      <div className="mt-4">{renderApps(apps, appManagementTools)}</div>
    </>
  );
};

export default Applications;
