import { Modal, Tabs, Tab, Row, Col, Nav } from "react-bootstrap";
import FileUploadForm from "../FileUploadForm";
import FileUploadTooltip from "../FileUploadTooltip";
import React from "react";

const FileUploadModalBody = ({ submitHandler }) => {
  return (
    <Modal.Body>
      <Tab.Container defaultActiveKey="form">
        <Row className="mb-3">
          <Col>
            <Nav variant="tabs" className="flex-row">
              <Nav.Item>
                <Nav.Link eventKey="form">Form</Nav.Link>
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
                <FileUploadForm handleSubmit={submitHandler} />
              </Tab.Pane>
              <Tab.Pane eventKey="help">
                <FileUploadTooltip />
              </Tab.Pane>
            </Tab.Content>
          </Col>
        </Row>
      </Tab.Container>

      {/*<Tabs defaultActiveKey="form">*/}
      {/*  <Tab eventKey="form" title="Form">*/}
      {/*    <FileUploadForm handleSubmit={submitHandler} />*/}
      {/*  </Tab>*/}
      {/*  <Tab eventKey="help" title="Help">*/}
      {/*    <FileUploadTooltip />*/}
      {/*  </Tab>*/}
      {/*</Tabs>*/}
    </Modal.Body>
  );
};

export default FileUploadModalBody;
