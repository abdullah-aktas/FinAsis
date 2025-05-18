import helmet from 'helmet';
import compression from 'compression';
import rateLimit from 'express-rate-limit';
import { createLogger } from '../utils/logger';

const logger = createLogger('SecurityService');

export class SecurityService {
    private static instance: SecurityService;
    private securityConfig: any;

    private constructor() {
        this.securityConfig = {
            helmet: {
                contentSecurityPolicy: {
                    directives: {
                        defaultSrc: ["'self'"],
                        scriptSrc: ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
                        styleSrc: ["'self'", "'unsafe-inline'"],
                        imgSrc: ["'self'", 'data:', 'https:'],
                        connectSrc: ["'self'", 'https://api.example.com'],
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
            compression: {
                level: 6,
                threshold: 10 * 1024,
                filter: (req: any, res: any) => {
                    if (req.headers['x-no-compression']) {
                        return false;
                    }
                    return compression.filter(req, res);
                },
            },
            rateLimit: {
                windowMs: 15 * 60 * 1000, // 15 dakika
                max: 100, // IP başına limit
                standardHeaders: true,
                legacyHeaders: false,
                message: 'Çok fazla istek gönderdiniz. Lütfen daha sonra tekrar deneyin.',
            },
        };
    }

    public static getInstance(): SecurityService {
        if (!SecurityService.instance) {
            SecurityService.instance = new SecurityService();
        }
        return SecurityService.instance;
    }

    // Güvenlik middleware'lerini al
    public getSecurityMiddlewares(): any[] {
        try {
            return [
                helmet(this.securityConfig.helmet),
                compression(this.securityConfig.compression),
                rateLimit(this.securityConfig.rateLimit),
            ];
        } catch (error) {
            logger.error('Güvenlik middleware oluşturma hatası:', error);
            throw new Error('Güvenlik middleware oluşturma başarısız oldu');
        }
    }

    // Güvenlik ayarlarını güncelle
    public updateSecurityConfig(newConfig: any): void {
        try {
            this.securityConfig = {
                ...this.securityConfig,
                ...newConfig,
            };
            logger.info('Güvenlik ayarları güncellendi');
        } catch (error) {
            logger.error('Güvenlik ayarları güncelleme hatası:', error);
            throw new Error('Güvenlik ayarları güncelleme başarısız oldu');
        }
    }

    // Güvenlik durumunu kontrol et
    public checkSecurityStatus(): {
        helmet: boolean;
        compression: boolean;
        rateLimit: boolean;
    } {
        try {
            return {
                helmet: this.securityConfig.helmet !== undefined,
                compression: this.securityConfig.compression !== undefined,
                rateLimit: this.securityConfig.rateLimit !== undefined,
            };
        } catch (error) {
            logger.error('Güvenlik durumu kontrol hatası:', error);
            throw new Error('Güvenlik durumu kontrolü başarısız oldu');
        }
    }

    // Güvenlik loglarını al
    public getSecurityLogs(): any[] {
        try {
            // Burada gerçek bir log sistemi entegre edilebilir
            return [
                {
                    timestamp: new Date(),
                    type: 'security',
                    message: 'Güvenlik servisi aktif',
                },
            ];
        } catch (error) {
            logger.error('Güvenlik logları alma hatası:', error);
            throw new Error('Güvenlik logları alma başarısız oldu');
        }
    }

    // Güvenlik olaylarını izle
    public monitorSecurityEvents(callback: (event: any) => void): void {
        try {
            // Burada gerçek bir event monitoring sistemi entegre edilebilir
            setInterval(() => {
                const event = {
                    timestamp: new Date(),
                    type: 'security_check',
                    status: 'ok',
                };
                callback(event);
            }, 60000); // Her dakika kontrol et
        } catch (error) {
            logger.error('Güvenlik izleme hatası:', error);
            throw new Error('Güvenlik izleme başarısız oldu');
        }
    }
} 