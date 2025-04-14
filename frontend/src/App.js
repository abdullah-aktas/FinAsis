import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import theme from './theme';

// Layout bileşenleri
import MainLayout from './layouts/MainLayout';
import AuthLayout from './layouts/AuthLayout';

// Sayfa bileşenleri
import Dashboard from './pages/Dashboard';
import Transactions from './pages/Transactions';
import Budget from './pages/Budget';
import Reports from './pages/Reports';
import Login from './pages/Login';
import Register from './pages/Register';
import NotFound from './pages/NotFound';

// Deep linking için özel bileşen
const DeepLinkHandler = ({ children }) => {
  React.useEffect(() => {
    // URL'den deep link parametrelerini al
    const params = new URLSearchParams(window.location.search);
    const action = params.get('action');
    const id = params.get('id');

    if (action && id) {
      // Deep link işlemlerini gerçekleştir
      switch (action) {
        case 'transaction':
          // İşlem detayına git
          window.location.href = `/transactions/${id}`;
          break;
        case 'budget':
          // Bütçe detayına git
          window.location.href = `/budget/${id}`;
          break;
        case 'report':
          // Rapor detayına git
          window.location.href = `/reports/${id}`;
          break;
        default:
          break;
      }
    }
  }, []);

  return children;
};

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <DeepLinkHandler>
          <Routes>
            {/* Auth routes */}
            <Route element={<AuthLayout />}>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
            </Route>

            {/* Protected routes */}
            <Route element={<MainLayout />}>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/transactions" element={<Transactions />} />
              <Route path="/transactions/:id" element={<Transactions />} />
              <Route path="/budget" element={<Budget />} />
              <Route path="/budget/:id" element={<Budget />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/reports/:id" element={<Reports />} />
            </Route>

            {/* 404 route */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </DeepLinkHandler>
      </Router>
    </ThemeProvider>
  );
}

export default App; 