import React from "react";
import axios from "axios";
import { Modal, Button } from "react-bootstrap";
import { useSelector, useDispatch } from "react-redux";

import { actions } from "../../slices";
import FileUploadForm from "../FileUploadForm";

const handleSumbit = ({ appId, hideModal }) => async event => {
  event.preventDefault();

  const formData = new FormData(event.target);
  const url = `http://${document.location.hostname}:8000/applications/${appId}/`;

  try {
    await axios.put(url, formData, {
      headers: { "Content-Type": "multipart/form-data" }
    });
  } catch (e) {
    console.log(e);
  }

  hideModal();
};

const getModalInfo = ({ modalInfo }) => modalInfo;

const UpdateAppModal = () => {
  const dispatch = useDispatch();
  const hideModal = () => dispatch(actions.modalInfo.hideModal());

  const { app } = useSelector(getModalInfo);
  const sumbitProps = { appId: app.id, hideModal };

  return (
    <Modal show onHide={hideModal}>
      <Modal.Header closeButton onHide={hideModal}>
        <Modal.Title>Update application</Modal.Title>
      </Modal.Header>

      <Modal.Body>
        <FileUploadForm handleSumbit={handleSumbit(sumbitProps)} />
      </Modal.Body>
    </Modal>
  );
};

export default UpdateAppModal;
