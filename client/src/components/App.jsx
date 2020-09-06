import React from "react";
import LoadingOverlay from "react-loading-overlay";
import { useSelector, useDispatch } from "react-redux";
import { Container, Row, Col, Alert } from "react-bootstrap";

import getModal from "./modals";
import { actions } from "../slices";
import { flowStates } from "../consts";
import Applications from "./Applications";

const renderModal = modalInfo => {
  if (!modalInfo.type) {
    return null;
  }

  const ModalComponent = getModal(modalInfo.type);
  return <ModalComponent />;
};

const renderErrorInfo = (errorInfo, resetError) => {
  if (errorInfo === null) {
    return null;
  }

  return (
    <Alert variant="danger" onClose={resetError} dismissible>
      <Alert.Heading>Oops...</Alert.Heading>
      <p>{errorInfo}</p>
    </Alert>
  );
};

const getErrorInfo = ({ errorInfo }) => errorInfo;
const getFlowState = ({ flowState }) => flowState;
const getModalInfo = ({ modalInfo }) => modalInfo;

const App = () => {
  const dispatch = useDispatch();
  const resetError = () => dispatch(actions.errorInfo.setErrorInfo(null));

  const modalInfo = useSelector(getModalInfo);
  const flowState = useSelector(getFlowState);
  const errorInfo = useSelector(getErrorInfo);

  const isLoaderActive = flowState === flowStates.loading;

  return (
    <LoadingOverlay active={isLoaderActive} spinner className="h-100">
      <Container className="vh-100 pt-5">
        <Row>
          <Col>
            <Applications />
          </Col>
        </Row>
      </Container>
      {renderModal(modalInfo)}
      {renderErrorInfo(errorInfo, resetError)}
    </LoadingOverlay>
  );
};

export default App;
