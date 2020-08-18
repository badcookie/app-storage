import React from 'react';
import axios from "axios";
import { connect } from 'react-redux';

import { actions } from '../slices';

const { addApp } = actions.apps;
const actionMap = { addApp };


class Form extends React.Component {
  constructor(props) {
    super(props);
    this.fileInput = React.createRef();
  }

  handleSubmit = (fileRef) => async (event) => {
    event.preventDefault();

    const formData = new FormData(event.target);
    console.log(event.target)

    const url = `http://${document.location.hostname}:8000/applications/`;

    try {
        const response = await axios.post(url, formData, {
            headers: {'Content-Type': 'multipart/form-data'}
        });
        const app = response.data;
        this.props.addApp(app);
    } catch (e) {
        console.log(e);
    }
  }

  render() {
    return (
      <form onSubmit={this.handleSubmit(this.fileInput)}>
        <label>
          Upload file:
          <input type="file" accept=".zip" name="zipfile" required ref={this.fileInput} />
        </label>
        <br />
        <button type="submit">Submit</button>
      </form>
    );
  }
}

export default connect(null, actionMap)(Form);
