import axios from 'axios';
import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';

import { actions } from '../slices';


const getApps = (state) => state.apps;

const Applications = () => {
  const dispatch = useDispatch();
  const addApps = (apps) => dispatch(actions.apps.addApps(apps));
  const apps = useSelector(getApps);

  useEffect(() => {
    const url = `http://${document.location.hostname}:8000/applications/`;
    axios.get(url)
      .then((response) => {
        const apps = response.data;
        addApps(apps);
    });
  }, []);

  return <ul>{apps.map((app) => <li key={app.id}>{app.uid} {app.port}</li>)}</ul>;
};

export default Applications;
