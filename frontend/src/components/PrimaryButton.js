import React from 'react';
import Button from '@mui/material/Button';

export default function PrimaryButton({ children, ...props }) {
  return (
    <Button variant="contained" color="primary" {...props}>
      {children}
    </Button>
  );
} 