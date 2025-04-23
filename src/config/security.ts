import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import { createLogger } from '../utils/logger';

const logger = createLogger('SecurityConfig');

export const securityConfig = {
  helmet: {
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        scriptSrc: ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
        styleSrc: ["'self'", "'unsafe-inline'"],
        imgSrc: ["'self'", 'data:', 'https:'],
        connectSrc: ["'self'", 'https://api.example.com'],
        fontSrc: ["'self'", 'data:', 'https:'],
        objectSrc: ["'none'"],
        mediaSrc: ["'self'"],
        frameSrc: ["'none'"],
      },
    },
    crossOriginEmbedderPolicy: true,
    crossOriginOpenerPolicy: true,
    crossOriginResourcePolicy: { policy: 'same-site' },
    dnsPrefetchControl: { allow: false },
    frameguard: { action: 'deny' },
    hidePoweredBy: true,
    hsts: { maxAge: 31536000, includeSubDomains: true, preload: true },
    ieNoOpen: true,
    noSniff: true,
    originAgentCluster: true,
    permittedCrossDomainPolicies: { permittedPolicies: 'none' },
    referrerPolicy: { policy: 'no-referrer' },
    xssFilter: true,
  },
  rateLimit: {
    windowMs: 15 * 60 * 1000, // 15 dakika
    max: 100, // IP başına limit
    standardHeaders: true,
    legacyHeaders: false,
    message: 'Çok fazla istek gönderdiniz. Lütfen daha sonra tekrar deneyin.',
  },
  cors: {
    origin: process.env.NODE_ENV === 'production' 
      ? ['https://finasis.com'] 
      : ['http://localhost:3000'],
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization'],
    credentials: true,
    maxAge: 86400, // 24 saat
  },
  session: {
    secret: process.env.SESSION_SECRET || 'your-secret-key',
    resave: false,
    saveUninitialized: false,
    cookie: {
      secure: process.env.NODE_ENV === 'production',
      httpOnly: true,
      maxAge: 24 * 60 * 60 * 1000, // 24 saat
      sameSite: 'strict',
    },
  },
};

export const applySecurityMiddleware = (app: any) => {
  try {
    // Helmet middleware
    app.use(helmet(securityConfig.helmet));

    // Rate limiting
    app.use(rateLimit(securityConfig.rateLimit));

    // CORS
    app.use((req: any, res: any, next: any) => {
      const origin = req.headers.origin;
      if (securityConfig.cors.origin.includes(origin)) {
        res.setHeader('Access-Control-Allow-Origin', origin);
        res.setHeader('Access-Control-Allow-Methods', securityConfig.cors.methods.join(','));
        res.setHeader('Access-Control-Allow-Headers', securityConfig.cors.allowedHeaders.join(','));
        res.setHeader('Access-Control-Allow-Credentials', 'true');
        res.setHeader('Access-Control-Max-Age', securityConfig.cors.maxAge);
      }
      next();
    });

    // Security headers
    app.use((req: any, res: any, next: any) => {
      res.setHeader('X-Content-Type-Options', 'nosniff');
      res.setHeader('X-Frame-Options', 'DENY');
      res.setHeader('X-XSS-Protection', '1; mode=block');
      res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
      res.setHeader('Referrer-Policy', 'no-referrer');
      next();
    });

    logger.info('Güvenlik middleware\'leri başarıyla uygulandı');
  } catch (error) {
    logger.error('Güvenlik middleware\'leri uygulanırken hata oluştu:', error);
    throw error;
  }
}; 