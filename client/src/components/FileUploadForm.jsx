import React from "react";
import { Form, Button } from "react-bootstrap";

const FileUploadForm = ({ handleSumbit }) => (
  <Form>
    <Form.Group>
      <Form.Row onSubmit={handleSumbit}>
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

export default FileUploadForm;
