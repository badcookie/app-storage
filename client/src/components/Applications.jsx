import axios from "axios";
import React, { useEffect } from "react";
import { ListGroup, Card, Button } from "react-bootstrap";
import { useSelector, useDispatch } from "react-redux";

import { actions } from "../slices";

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

const getApps = ({ apps }) => apps;

const renderApps = (apps, appManagementTools) => {
  const { handleRemove, handleUpdate } = appManagementTools;

  if (apps.length === 0) {
    return <Card body>No apps yet.</Card>;
  }

  return (
    <ListGroup variant="flush">
      {apps.map(app => (
        <ListGroup.Item key={app.id} className="d-flex">
          {app.uid} {app.port}
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
            onClick={handleUpdate(app)}
            className="mr-1"
          >
            Update
          </Button>
          <Button variant="danger" onClick={handleRemove(app)}>
            Remove
          </Button>
        </ListGroup.Item>
      ))}
    </ListGroup>
  );
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
