import axios from "axios";
import { Modal } from "react-bootstrap";
import React, { useContext } from "react";
import { useSelector, useDispatch } from "react-redux";

import { actions } from "../../slices";
import {
  routes,
  flowStates,
  ClientContext,
  clientUidHeader
} from "../../consts";
import FileUploadModalBody from "./FileUploadModalBody";

const handleSubmit = ({
  appId,
  updateApp,
  hideModal,
  setFlowState,
  setErrorInfo,
  clientUid
}) => async event => {
  event.preventDefault();

  hideModal();
  setFlowState(flowStates.loading);

  const formData = new FormData(event.target);
  const url = routes.updateApp(appId);

  try {
    const response = await axios.put(url, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
        [clientUidHeader]: clientUid
      }
    });

    const updatedAppData = response.data;
    updateApp(updatedAppData);

    setFlowState(flowStates.ready);
  } catch (error) {
    const message = error.response ? error.response.data : error.message;
    setFlowState(flowStates.error);
    setErrorInfo(message);
  }
};

const getModalInfo = ({ modalInfo }) => modalInfo;

const UpdateAppModal = () => {
  const dispatch = useDispatch();
  const hideModal = () => dispatch(actions.modalInfo.hideModal());
  const setFlowState = newState =>
    dispatch(actions.flowState.setProcess(newState));
  const setErrorInfo = errorData =>
    dispatch(actions.errorInfo.setErrorInfo(errorData));
  const updateApp = newAppData => dispatch(actions.apps.updateApp(newAppData));

  const clientUid = useContext(ClientContext);

  const { app } = useSelector(getModalInfo);
  const submitProps = {
    appId: app.id,
    hideModal,
    setFlowState,
    setErrorInfo,
    updateApp,
    clientUid
  };

  return (
    <Modal show onHide={hideModal} size="lg">
      <Modal.Header closeButton onHide={hideModal}>
        <Modal.Title>Update application</Modal.Title>
      </Modal.Header>
      <FileUploadModalBody
        submitHandler={handleSubmit(submitProps)}
        showDbOption={false}
      />
    </Modal>
  );
};

export default UpdateAppModal;
