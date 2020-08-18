import React from 'react';


class Form extends React.Component {
  constructor(props) {
    super(props);
    this.fileInput = React.createRef();
  }

  handleSubmit = (fileRef) => (event) => {
    event.preventDefault();
    const file = fileRef.current.files[0];
    console.log(file);
  }

  render() {
    return (
      <form onSubmit={this.handleSubmit(this.fileInput)}>
        <label>
          Upload file:
          <input type="file" ref={this.fileInput} />
        </label>
        <br />
        <button type="submit">Submit</button>
      </form>
    );
  }
}

export default Form;
