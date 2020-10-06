import { Modal, Tab, Row, Col, Nav } from "react-bootstrap";
import AppForm from "../AppForm";
import AppUploadHelpCards from "../AppUploadHelpCards";
import React from "react";

const FileUploadModalBody = ({ submitHandler, showDbOption }) => {
  return (
    <Modal.Body>
      <Tab.Container defaultActiveKey="form">
        <Row className="mb-3">
          <Col>
            <Nav variant="tabs" className="flex-row">
              <Nav.Item>
                <Nav.Link eventKey="form">Upload</Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="help">Help</Nav.Link>
              </Nav.Item>
            </Nav>
          </Col>
        </Row>
        <Row>
          <Col>
            <Tab.Content>
              <Tab.Pane eventKey="form">
                <AppForm
                  handleSubmit={submitHandler}
                  showDbOption={showDbOption}
                />
              </Tab.Pane>
              <Tab.Pane eventKey="help">
                <AppUploadHelpCards />
              </Tab.Pane>
            </Tab.Content>
          </Col>
        </Row>
      </Tab.Container>
    </Modal.Body>
  );
};

export default FileUploadModalBody;
