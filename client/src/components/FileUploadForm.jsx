import React, { useEffect } from "react";
import { Form, Button } from "react-bootstrap";
import bsCustomFileInput from "bs-custom-file-input";

const FileUploadForm = ({ handleSubmit }) => {
  useEffect(() => {
    bsCustomFileInput.init();
  });

  return (
    <Form onSubmit={handleSubmit}>
      <Form.Group>
        <Form.Row>
          <Form.File
            id="custom-file"
            label="Upload file"
            accept=".zip"
            name="zipfile"
            custom
            required
          />
        </Form.Row>
      </Form.Group>
      <Button type="submit">Submit</Button>
    </Form>
  );
};

export default FileUploadForm;
