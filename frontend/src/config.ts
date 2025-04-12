// API yapılandırması
export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// Uygulama yapılandırması
export const APP_CONFIG = {
  name: 'FinAsis',
  version: '1.0.0',
  description: 'Finansal Yönetim ve Muhasebe Sistemi',
  company: {
    name: 'FinAsis Teknoloji A.Ş.',
    website: 'https://finasis.com',
    email: 'info@finasis.com',
    phone: '+90 (212) 123 45 67',
    address: 'Levent, Büyükdere Cad. No:123, 34330 Beşiktaş/İstanbul',
    taxOffice: 'Beşiktaş Vergi Dairesi',
    taxNumber: '1234567890',
    logo: '/images/logo.png',
    socialMedia: {
      facebook: 'https://facebook.com/finasis',
      twitter: 'https://twitter.com/finasis',
      linkedin: 'https://linkedin.com/company/finasis',
      instagram: 'https://instagram.com/finasis'
    }
  },
  features: {
    accounting: true,
    virtualCompany: true,
    education: true,
    eArchive: true,
    eInvoice: true,
    reporting: true
  },
  support: {
    email: 'destek@finasis.com',
    phone: '+90 (212) 123 45 68',
    workingHours: '09:00 - 18:00 (Pazartesi - Cuma)'
  }
};

// Tema yapılandırması
export const THEME_CONFIG = {
  palette: {
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
      contrastText: '#ffffff'
    },
    secondary: {
      main: '#dc004e',
      light: '#ff4081',
      dark: '#c51162',
      contrastText: '#ffffff'
    },
    success: {
      main: '#2e7d32',
      light: '#4caf50',
      dark: '#1b5e20',
      contrastText: '#ffffff'
    },
    warning: {
      main: '#ed6c02',
      light: '#ff9800',
      dark: '#e65100',
      contrastText: '#ffffff'
    },
    error: {
      main: '#d32f2f',
      light: '#ef5350',
      dark: '#c62828',
      contrastText: '#ffffff'
    },
    info: {
      main: '#0288d1',
      light: '#03a9f4',
      dark: '#01579b',
      contrastText: '#ffffff'
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
      dark: '#e0e0e0'
    },
    text: {
      primary: '#333333',
      secondary: '#666666',
      disabled: '#999999'
    },
    divider: '#e0e0e0'
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 500,
      lineHeight: 1.2
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
      lineHeight: 1.3
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 500,
      lineHeight: 1.3
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 500,
      lineHeight: 1.4
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 500,
      lineHeight: 1.4
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 500,
      lineHeight: 1.4
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.5
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.5
    },
    button: {
      textTransform: 'none',
      fontWeight: 500
    }
  },
  shape: {
    borderRadius: 4
  },
  shadows: [
    'none',
    '0px 2px 1px -1px rgba(0,0,0,0.2),0px 1px 1px 0px rgba(0,0,0,0.14),0px 1px 3px 0px rgba(0,0,0,0.12)',
    '0px 3px 1px -2px rgba(0,0,0,0.2),0px 2px 2px 0px rgba(0,0,0,0.14),0px 1px 5px 0px rgba(0,0,0,0.12)',
    '0px 3px 3px -2px rgba(0,0,0,0.2),0px 3px 4px 0px rgba(0,0,0,0.14),0px 1px 8px 0px rgba(0,0,0,0.12)',
    '0px 2px 4px -1px rgba(0,0,0,0.2),0px 4px 5px 0px rgba(0,0,0,0.14),0px 1px 10px 0px rgba(0,0,0,0.12)'
  ],
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: '8px 16px'
        }
      }
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0px 2px 4px rgba(0,0,0,0.1)'
        }
      }
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12
        }
      }
    }
  }
};

// Sayfalama yapılandırması
export const PAGINATION_CONFIG = {
  defaultPageSize: 25,
  pageSizeOptions: [10, 25, 50, 100],
  rowsPerPageText: 'Sayfa başına satır:',
  labelDisplayedRows: '{from}-{to} / {count}',
  labelRowsSelect: 'Satır',
  firstAriaLabel: 'İlk sayfa',
  firstTooltip: 'İlk sayfa',
  previousAriaLabel: 'Önceki sayfa',
  previousTooltip: 'Önceki sayfa',
  nextAriaLabel: 'Sonraki sayfa',
  nextTooltip: 'Sonraki sayfa',
  lastAriaLabel: 'Son sayfa',
  lastTooltip: 'Son sayfa'
};

// Tarih formatı yapılandırması
export const DATE_FORMAT = {
  display: 'DD.MM.YYYY',
  api: 'YYYY-MM-DD',
  datetime: 'DD.MM.YYYY HH:mm:ss',
  time: 'HH:mm',
  monthYear: 'MMMM YYYY',
  shortMonth: 'MMM',
  longMonth: 'MMMM',
  shortDay: 'ddd',
  longDay: 'dddd',
  shortYear: 'YY',
  longYear: 'YYYY',
  quarter: '[Q]Q YYYY',
  fiscalYear: 'YYYY-YYYY',
  relative: 'relative',
  fromNow: 'fromNow',
  calendar: 'calendar',
  iso: 'YYYY-MM-DDTHH:mm:ss.SSSZ'
};

// Para birimi yapılandırması
export const CURRENCY_CONFIG = {
  default: 'TRY',
  format: {
    style: 'currency',
    currency: 'TRY',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  },
  availableCurrencies: [
    { code: 'TRY', symbol: '₺', name: 'Türk Lirası' },
    { code: 'USD', symbol: '$', name: 'Amerikan Doları' },
    { code: 'EUR', symbol: '€', name: 'Euro' },
    { code: 'GBP', symbol: '£', name: 'İngiliz Sterlini' },
    { code: 'JPY', symbol: '¥', name: 'Japon Yeni' },
    { code: 'CHF', symbol: 'Fr', name: 'İsviçre Frangı' },
    { code: 'AUD', symbol: 'A$', name: 'Avustralya Doları' },
    { code: 'CAD', symbol: 'C$', name: 'Kanada Doları' },
    { code: 'CNY', symbol: '¥', name: 'Çin Yuanı' },
    { code: 'INR', symbol: '₹', name: 'Hint Rupisi' }
  ],
  exchangeRateAPI: 'https://api.exchangerate-api.com/v4/latest/TRY',
  exchangeRateUpdateInterval: 24 * 60 * 60 * 1000, // 24 saat
  exchangeRateCacheKey: 'finasis_exchange_rates',
  exchangeRateCacheExpiry: 24 * 60 * 60 * 1000, // 24 saat
  defaultLocale: 'tr-TR',
  locales: {
    'tr-TR': {
      currency: 'TRY',
      format: {
        style: 'currency',
        currency: 'TRY',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }
    },
    'en-US': {
      currency: 'USD',
      format: {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }
    },
    'de-DE': {
      currency: 'EUR',
      format: {
        style: 'currency',
        currency: 'EUR',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }
    }
  }
};

// Sayfa boyutları
export const PAGE_SIZES = [10, 25, 50, 100];

// Varsayılan sayfa boyutu
export const DEFAULT_PAGE_SIZE = 25;

// Dosya yükleme limitleri
export const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
export const ALLOWED_FILE_TYPES = ['image/jpeg', 'image/png', 'application/pdf'];

// Oturum ayarları
export const TOKEN_KEY = 'finasis_token';
export const REFRESH_TOKEN_KEY = 'finasis_refresh_token';
export const TOKEN_EXPIRY = 24 * 60 * 60 * 1000; // 24 saat

// Tema ayarları
export const THEME = {
  primary: '#1976d2',
  secondary: '#dc004e',
  error: '#f44336',
  warning: '#ff9800',
  info: '#2196f3',
  success: '#4caf50'
}; 