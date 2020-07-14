import axios from 'axios';
import { connect } from 'react-redux';
import React, { useEffect } from 'react';

import { actions } from '../slices';


const mapStateToProps = (state) => {
  const { apps } = state;
  return { apps };
};

const { addApps } = actions.apps;
const actionMakers = { addApps };


const Applications = (props) => {
  const { apps, addApps } = props;

  useEffect(() => {
      axios.get('http://localhost:8000/applications')
        .then((response) => {
          const apps = response.data;
          console.log(apps);
          addApps(apps);
      });
  }, []);

  return <ul>{apps.map((app) => <li key={app.id}>{app.id}</li>)}</ul>;
};


export default connect(mapStateToProps, actionMakers)(Applications);
