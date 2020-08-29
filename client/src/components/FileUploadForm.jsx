import React from "react";

const FileUploadForm = ({ handleSumbit }) => (
  <form onSubmit={handleSumbit}>
    <label>
      Upload file:
      <input type="file" accept=".zip" name="zipfile" required />
    </label>
    <br />
    <button type="submit">Submit</button>
  </form>
);

export default FileUploadForm;
