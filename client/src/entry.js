import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';

import App from './components/App';
import { reducers } from './slices';


export default () => {
  const store = configureStore({ reducer: reducers });

  const mountNode = document.getElementById('root');
  ReactDOM.render(
      <Provider store={store}><App /></Provider>,
      mountNode,
  );
};
