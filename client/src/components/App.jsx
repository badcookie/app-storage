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
      Processing failed due to the following error: {errorInfo}
    </Alert>
  );
};

const getErrorInfo = ({ errorInfo }) => errorInfo;
const getFlowState = ({ flowState }) => flowState.process;
const getModalInfo = ({ modalInfo }) => modalInfo;
const getFlowDetail = ({ flowState }) => flowState.detail;

const App = () => {
  const dispatch = useDispatch();
  const resetError = () => dispatch(actions.errorInfo.setErrorInfo(null));

  const modalInfo = useSelector(getModalInfo);
  const flowState = useSelector(getFlowState);
  const errorInfo = useSelector(getErrorInfo);

  const isLoaderActive = flowState === flowStates.loading;

  const uploadDetail = useSelector(getFlowDetail);

  return (
    <LoadingOverlay active={isLoaderActive} spinner text={uploadDetail}>
      {renderErrorInfo(errorInfo, resetError)}
      <Container className="vh-100 pt-5">
        <Row>
          <Col>
            <Applications />
          </Col>
        </Row>
      </Container>
      {renderModal(modalInfo)}
    </LoadingOverlay>
  );
};

export default App;
