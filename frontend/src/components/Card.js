import React from 'react';
import { Card as MuiCard, CardContent, Typography } from '@mui/material';

export default function Card({ title, children }) {
  return (
    <MuiCard sx={{ margin: 2 }}>
      <CardContent>
        {title && <Typography variant="h6" gutterBottom>{title}</Typography>}
        {children}
      </CardContent>
    </MuiCard>
  );
} 