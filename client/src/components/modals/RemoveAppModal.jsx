import React from "react";
import axios from "axios";
import { Modal, Button } from "react-bootstrap";
import { useSelector, useDispatch } from "react-redux";

import { actions } from "../../slices";

const handleSubmit = ({ appId, removeApp, hideModal }) => async () => {
  const url = `http://${document.location.hostname}:8000/applications/${appId}/`;
  await axios
    .delete(url)
    .then(response => {
      removeApp(appId);
    })
    .catch(console.log);

  hideModal();
};

const getModalInfo = ({ modalInfo }) => modalInfo;

const RemoveAppModal = () => {
  const dispatch = useDispatch();
  const removeApp = appId => dispatch(actions.apps.removeApp(appId));
  const hideModal = () => dispatch(actions.modalInfo.hideModal());

  const { app } = useSelector(getModalInfo);
  const sumbitProps = { appId: app.id, removeApp, hideModal };

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
