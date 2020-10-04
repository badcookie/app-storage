import React, { useEffect } from "react";
import { useDispatch } from "react-redux";
import { Form, Button } from "react-bootstrap";
import bsCustomFileInput from "bs-custom-file-input";

import { actions } from "../slices";

const handleCheck = setDbCreationChoice => event => {
  const createDb = event.target.checked;
  setDbCreationChoice(createDb);
};

const AppForm = ({ handleSubmit }) => {
  const dispatch = useDispatch();
  const setDbCreationChoice = createDb =>
    dispatch(actions.modalInfo.setModalInfo({ createDb }));

  useEffect(() => {
    bsCustomFileInput.init();
  });

  return (
    <Form onSubmit={handleSubmit}>
      <Form.Group controlId="formBasicFile">
        <Form.Row>
          <Form.File
            id="custom-file"
            label="..."
            accept=".zip"
            name="zipfile"
            custom
            required
          />
        </Form.Row>
      </Form.Group>
      <Form.Group controlId="formBasicCheckbox">
        <Form.Check
          type="checkbox"
          label="Create PostgreSQL instance"
          onChange={handleCheck(setDbCreationChoice)}
        />
      </Form.Group>
      <Button type="submit">Upload</Button>
    </Form>
  );
};

export default AppForm;
