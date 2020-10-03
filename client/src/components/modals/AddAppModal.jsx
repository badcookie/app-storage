import React from "react";
import axios from "axios";
import { Modal } from "react-bootstrap";
import { useDispatch, useSelector } from "react-redux";

import { actions } from "../../slices";
import FileUploadModalBody from "./FileUploadModalBody";
import { routes, flowStates } from "../../consts";

const handleSubmit = ({
  addApp,
  hideModal,
  setFlowState,
  setErrorInfo,
  createDb
}) => async event => {
  event.preventDefault();

  hideModal();
  setFlowState(flowStates.loading);

  const formData = new FormData(event.target);
  formData.append("createDb", createDb);

  const url = routes.createApp();

  try {
    const response = await axios.post(url, formData, {
      headers: { "Content-Type": "multipart/form-data" }
    });
    const app = response.data;
    addApp(app);
    setFlowState(flowStates.ready);
  } catch (error) {
    const message = error.response ? error.response.data : error.message;
    setFlowState(flowStates.error);
    setErrorInfo(message);
  }
};

const getDbCreationChoice = ({ modalInfo }) => modalInfo.createDb;

const AddAppModal = () => {
  const dispatch = useDispatch();
  const addApp = app => dispatch(actions.apps.addApp(app));
  const hideModal = () => dispatch(actions.modalInfo.hideModal());
  const setFlowState = newState =>
    dispatch(actions.flowState.setState(newState));
  const setErrorInfo = errorData =>
    dispatch(actions.errorInfo.setErrorInfo(errorData));

  const createDb = useSelector(getDbCreationChoice);

  const submitProps = {
    addApp,
    hideModal,
    setFlowState,
    setErrorInfo,
    createDb
  };

  return (
    <Modal show onHide={hideModal} centered>
      <Modal.Header closeButton onHide={hideModal}>
        <Modal.Title>Load application</Modal.Title>
      </Modal.Header>
      <FileUploadModalBody submitHandler={handleSubmit(submitProps)} />
    </Modal>
  );
};

export default AddAppModal;
