import axios from "axios";
import React, { useEffect, useContext } from "react";
import { Card, Button } from "react-bootstrap";
import { useSelector, useDispatch } from "react-redux";

import { actions } from "../slices";
import { routes, flowStates, ClientContext, clientUidHeader } from "../consts";

const fetchApps = ({
  addApps,
  setFlowState,
  setErrorInfo,
  clientUid
}) => () => {
  const url = routes.getApps();
  axios
    .get(url, { headers: { [clientUidHeader]: clientUid } })
    .then(response => {
      const apps = response.data;
      addApps(apps);
      setFlowState(flowStates.ready);
    })
    .catch(error => {
      setFlowState(flowStates.error);
      setErrorInfo(error.message);
    });
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
          href={routes.visitApp(app)}
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
  const clientUid = useContext(ClientContext);

  const dispatch = useDispatch();

  const setModalInfo = info => dispatch(actions.modalInfo.setModalInfo(info));
  const handleAppAdd = () => setModalInfo({ type: "add" });
  const appManagementTools = {
    handleRemove: app => () => setModalInfo({ type: "remove", app }),
    handleUpdate: app => () => setModalInfo({ type: "update", app })
  };

  const addApps = apps => dispatch(actions.apps.addApps(apps));
  const setFlowState = newState =>
    dispatch(actions.flowState.setProcess(newState));
  const setErrorInfo = errorData =>
    dispatch(actions.errorInfo.setErrorInfo(errorData));

  const props = { addApps, setFlowState, setErrorInfo, clientUid };
  useEffect(fetchApps(props), []);

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
