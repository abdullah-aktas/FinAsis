import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import theme from './theme';
import { UserProvider } from './contexts/UserContext';
import './App.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <ThemeProvider theme={theme}>
    <CssBaseline />
    <UserProvider>
      <App />
    </UserProvider>
  </ThemeProvider>
); 