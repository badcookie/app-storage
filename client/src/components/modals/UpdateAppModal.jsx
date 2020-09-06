import React from "react";
import axios from "axios";
import { Modal } from "react-bootstrap";
import { useSelector, useDispatch } from "react-redux";

import { actions } from "../../slices";
import FileUploadForm from "../FileUploadForm";
import { routes, flowStates } from "../../consts";

const handleSumbit = ({
  appId,
  hideModal,
  setFlowState,
  setErrorInfo
}) => async event => {
  event.preventDefault();

  hideModal();
  setFlowState(flowStates.loading);

  const formData = new FormData(event.target);
  const url = routes.updateApp(appId);

  try {
    await axios.put(url, formData, {
      headers: { "Content-Type": "multipart/form-data" }
    });
    setFlowState(flowStates.ready);
  } catch (error) {
    setFlowState(flowStates.error);
    setErrorInfo(error);
  }
};

const getModalInfo = ({ modalInfo }) => modalInfo;

const UpdateAppModal = () => {
  const dispatch = useDispatch();
  const hideModal = () => dispatch(actions.modalInfo.hideModal());
  const setFlowState = newState =>
    dispatch(actions.flowState.setState(newState));
  const setErrorInfo = errorData =>
    dispatch(actions.errorInfo.setErrorInfo(errorData));

  const { app } = useSelector(getModalInfo);
  const sumbitProps = { appId: app.id, hideModal, setFlowState, setErrorInfo };

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
