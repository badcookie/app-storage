import axios from 'axios';
import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';

import { actions } from '../slices';


const getApps = (state) => state.apps;

const Applications = () => {
  const dispatch = useDispatch();
  const addApps = () => dispatch(actions.apps.addApps());

  const apps = useSelector(getApps);

  useEffect(() => {
      const url = `http://${document.location.hostname}:8000/applications/`;
      console.log(url);
      axios.get(url)
        .then((response) => {
          const apps = response.data;
          console.log('what we received', apps);
          addApps(apps);
      });
  });

  return <ul>{apps.map((app) => <li key={app.id}>{app.id}</li>)}</ul>;
};

export default Applications;
