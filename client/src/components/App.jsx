import React from "react";
import { useSelector } from "react-redux";
import { Container, Row, Col } from "react-bootstrap";

import getModal from "./modals";
import Applications from "./Applications";

const renderModal = modalInfo => {
  if (!modalInfo.type) {
    return null;
  }

  const ModalComponent = getModal(modalInfo.type);
  return <ModalComponent />;
};

const getModalInfo = ({ modalInfo }) => modalInfo;

const App = () => {
  const modalInfo = useSelector(getModalInfo);
  return (
    <>
      <Container className="h-100 mt-5">
        <Row>
          <Col>
            <Applications />
          </Col>
        </Row>
      </Container>
      {renderModal(modalInfo)}
    </>
  );
};

export default App;
