import React from "react";
import axios from "axios";
import { Modal, Button } from "react-bootstrap";
import { useDispatch } from "react-redux";

import { actions } from "../../slices";
import FileUploadForm from "../FileUploadForm";

const handleSumbit = addApp => async event => {
  event.preventDefault();

  const formData = new FormData(event.target);

  const url = `http://${document.location.hostname}:8000/applications/`;

  try {
    const response = await axios.post(url, formData, {
      headers: { "Content-Type": "multipart/form-data" }
    });
    const app = response.data;
    addApp(app);
  } catch (e) {
    console.log(e);
  }
};

const AddAppModal = () => {
  const dispatch = useDispatch();
  const addApp = app => dispatch(actions.apps.addApp(app));
  const hideModal = () => dispatch(actions.modalInfo.hideModal());

  return (
    <Modal.Dialog onHide={hideModal}>
      <Modal.Header closeButton onHide={hideModal}>
        <Modal.Title>Load application</Modal.Title>
      </Modal.Header>

      <Modal.Body>
        <FileUploadForm handleSumbit={handleSumbit(addApp)} />
      </Modal.Body>

      <Modal.Footer>
        <Button variant="secondary">Close</Button>
        <Button variant="primary">Save changes</Button>
      </Modal.Footer>
    </Modal.Dialog>
  );
};

export default AddAppModal;
