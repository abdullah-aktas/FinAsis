import React from 'react';
import Alert from '@mui/material/Alert';

export default function ErrorMessage({ message }) {
  return (
    <Alert severity="error" sx={{ my: 2 }}>
      {message}
    </Alert>
  );
} 