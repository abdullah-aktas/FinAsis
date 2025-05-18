import React from 'react';
import { AppBar, Toolbar, IconButton, Typography, Button } from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import SchoolIcon from '@mui/icons-material/School';
import GamesIcon from '@mui/icons-material/Games';
import CurrencyBitcoinIcon from '@mui/icons-material/CurrencyBitcoin';

export default function MainMenu({ onNavigate }) {
  return (
    <AppBar position="static">
      <Toolbar>
        <IconButton color="inherit" onClick={() => onNavigate('home')}><HomeIcon /></IconButton>
        <Button color="inherit" startIcon={<SmartToyIcon />} onClick={() => onNavigate('ai')}>AI Asistanı</Button>
        <Button color="inherit" startIcon={<CurrencyBitcoinIcon />} onClick={() => onNavigate('blockchain')}>Blockchain</Button>
        <Button color="inherit" startIcon={<SchoolIcon />} onClick={() => onNavigate('education')}>Eğitim</Button>
        <Button color="inherit" startIcon={<GamesIcon />} onClick={() => onNavigate('games')}>Oyunlaştırma</Button>
        <Button color="inherit" startIcon={<AccountCircleIcon />} onClick={() => onNavigate('profile')}>Profil</Button>
      </Toolbar>
    </AppBar>
  );
} 