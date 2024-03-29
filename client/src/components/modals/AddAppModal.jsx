import axios from "axios";
import { Modal } from "react-bootstrap";
import React, { useContext } from "react";
import { useDispatch, useSelector } from "react-redux";

import { actions } from "../../slices";
import FileUploadModalBody from "./FileUploadModalBody";
import {
  routes,
  flowStates,
  ClientContext,
  clientUidHeader
} from "../../consts";

const handleSubmit = ({
  addApp,
  hideModal,
  setFlowState,
  setErrorInfo,
  createDb,
  clientUid
}) => async event => {
  event.preventDefault();

  hideModal();
  setFlowState(flowStates.loading);

  const formData = new FormData(event.target);
  const options = { createDb };
  formData.append("options", JSON.stringify(options));

  const url = routes.createApp();

  try {
    const response = await axios.post(url, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
        [clientUidHeader]: clientUid
      }
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
    dispatch(actions.flowState.setProcess(newState));
  const setErrorInfo = errorData =>
    dispatch(actions.errorInfo.setErrorInfo(errorData));

  const createDb = useSelector(getDbCreationChoice);

  const clientUid = useContext(ClientContext);

  const submitProps = {
    addApp,
    hideModal,
    setFlowState,
    setErrorInfo,
    createDb,
    clientUid
  };

  return (
    <Modal show onHide={hideModal} centered size="lg">
      <Modal.Header closeButton onHide={hideModal}>
        <Modal.Title>Add application</Modal.Title>
      </Modal.Header>
      <FileUploadModalBody
        submitHandler={handleSubmit(submitProps)}
        showDbOption={true}
      />
    </Modal>
  );
};

export default AddAppModal;
