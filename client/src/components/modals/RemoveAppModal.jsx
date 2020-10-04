import React from "react";
import axios from "axios";
import { Modal, Button } from "react-bootstrap";
import { useSelector, useDispatch } from "react-redux";

import { actions } from "../../slices";
import { routes, flowStates } from "../../consts";

const handleSubmit = ({
  appId,
  removeApp,
  hideModal,
  setFlowState,
  setErrorInfo
}) => async () => {
  hideModal();
  setFlowState(flowStates.loading);

  const url = routes.deleteApp(appId);

  try {
    await axios.delete(url);
    removeApp(appId);
    setFlowState(flowStates.ready);
  } catch (error) {
    setFlowState(flowStates.error);
    setErrorInfo(error.message);
  }
};

const getModalInfo = ({ modalInfo }) => modalInfo;

const RemoveAppModal = () => {
  const dispatch = useDispatch();
  const removeApp = appId => dispatch(actions.apps.removeApp(appId));
  const hideModal = () => dispatch(actions.modalInfo.hideModal());
  const setFlowState = newState =>
    dispatch(actions.flowState.setProcess(newState));
  const setErrorInfo = errorData =>
    dispatch(actions.errorInfo.setErrorInfo(errorData));

  const { app } = useSelector(getModalInfo);
  const sumbitProps = {
    appId: app.id,
    removeApp,
    hideModal,
    setFlowState,
    setErrorInfo
  };

  return (
    <Modal show onHide={hideModal} centered>
      <Modal.Header closeButton onHide={hideModal}>
        <Modal.Title>Remove application</Modal.Title>
      </Modal.Header>

      <Modal.Body>Are you sure?</Modal.Body>

      <Modal.Footer>
        <Button variant="primary" onClick={handleSubmit(sumbitProps)}>
          Yes
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default RemoveAppModal;
