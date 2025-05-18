import { createLogger } from '../utils/logger';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs';
import * as path from 'path';

const execAsync = promisify(exec);
const logger = createLogger('QualityControlService');

export class QualityControlService {
    private static instance: QualityControlService;
    private testConfig: any;

    private constructor() {
        this.testConfig = {
            cypress: {
                configFile: 'cypress.config.js',
                browser: 'chrome',
                headless: true,
            },
            sonar: {
                hostUrl: 'http://localhost:9000',
                projectKey: 'finasis',
                sources: 'src',
                exclusions: '**/node_modules/**,**/coverage/**,**/dist/**',
            },
            eslint: {
                configFile: '.eslintrc.json',
                extensions: ['.ts', '.tsx'],
                fix: true,
            },
        };
    }

    public static getInstance(): QualityControlService {
        if (!QualityControlService.instance) {
            QualityControlService.instance = new QualityControlService();
        }
        return QualityControlService.instance;
    }

    // E2E testleri çalıştır
    public async runE2ETests(): Promise<{
        passed: number;
        failed: number;
        duration: number;
    }> {
        try {
            const { stdout } = await execAsync(
                `npx cypress run --config-file=${this.testConfig.cypress.configFile} --browser=${this.testConfig.cypress.browser} --headless=${this.testConfig.cypress.headless}`
            );

            const results = this.parseCypressResults(stdout);
            logger.info('E2E testleri tamamlandı', results);
            return results;
        } catch (error) {
            logger.error('E2E test hatası:', error);
            throw new Error('E2E testleri başarısız oldu');
        }
    }

    // Kod kalitesi analizi
    public async runCodeQualityAnalysis(): Promise<{
        bugs: number;
        vulnerabilities: number;
        codeSmells: number;
        coverage: number;
    }> {
        try {
            const { stdout } = await execAsync(
                `npx sonar-scanner -Dsonar.host.url=${this.testConfig.sonar.hostUrl} -Dsonar.projectKey=${this.testConfig.sonar.projectKey} -Dsonar.sources=${this.testConfig.sonar.sources} -Dsonar.exclusions=${this.testConfig.sonar.exclusions}`
            );

            const results = this.parseSonarResults(stdout);
            logger.info('Kod kalitesi analizi tamamlandı', results);
            return results;
        } catch (error) {
            logger.error('Kod kalitesi analiz hatası:', error);
            throw new Error('Kod kalitesi analizi başarısız oldu');
        }
    }

    // Kod stil kontrolü
    public async runCodeStyleCheck(): Promise<{
        errors: number;
        warnings: number;
        fixed: number;
    }> {
        try {
            const { stdout } = await execAsync(
                `npx eslint ${this.testConfig.eslint.extensions.map(ext => `"src/**/*${ext}"`).join(' ')} --config ${this.testConfig.eslint.configFile} ${this.testConfig.eslint.fix ? '--fix' : ''}`
            );

            const results = this.parseESLintResults(stdout);
            logger.info('Kod stil kontrolü tamamlandı', results);
            return results;
        } catch (error) {
            logger.error('Kod stil kontrolü hatası:', error);
            throw new Error('Kod stil kontrolü başarısız oldu');
        }
    }

    // Test sonuçlarını parse et
    private parseCypressResults(output: string): {
        passed: number;
        failed: number;
        duration: number;
    } {
        const passed = (output.match(/✓/g) || []).length;
        const failed = (output.match(/✖/g) || []).length;
        const durationMatch = output.match(/Duration: (\d+\.\d+)s/);
        const duration = durationMatch ? parseFloat(durationMatch[1]) : 0;

        return { passed, failed, duration };
    }

    // Sonar sonuçlarını parse et
    private parseSonarResults(output: string): {
        bugs: number;
        vulnerabilities: number;
        codeSmells: number;
        coverage: number;
    } {
        const bugs = parseInt(output.match(/Bugs: (\d+)/)?.[1] || '0', 10);
        const vulnerabilities = parseInt(output.match(/Vulnerabilities: (\d+)/)?.[1] || '0', 10);
        const codeSmells = parseInt(output.match(/Code Smells: (\d+)/)?.[1] || '0', 10);
        const coverage = parseFloat(output.match(/Coverage: (\d+\.\d+)%/)?.[1] || '0');

        return { bugs, vulnerabilities, codeSmells, coverage };
    }

    // ESLint sonuçlarını parse et
    private parseESLintResults(output: string): {
        errors: number;
        warnings: number;
        fixed: number;
    } {
        const errors = (output.match(/error/g) || []).length;
        const warnings = (output.match(/warning/g) || []).length;
        const fixed = (output.match(/fixed/g) || []).length;

        return { errors, warnings, fixed };
    }

    // Test raporu oluştur
    public async generateTestReport(): Promise<string> {
        try {
            const e2eResults = await this.runE2ETests();
            const qualityResults = await this.runCodeQualityAnalysis();
            const styleResults = await this.runCodeStyleCheck();

            const report = {
                timestamp: new Date().toISOString(),
                e2e: e2eResults,
                quality: qualityResults,
                style: styleResults,
                summary: {
                    overallStatus: this.calculateOverallStatus(e2eResults, qualityResults, styleResults),
                    recommendations: this.generateRecommendations(e2eResults, qualityResults, styleResults),
                },
            };

            const reportPath = path.join(process.cwd(), 'reports', 'quality-report.json');
            await fs.promises.writeFile(reportPath, JSON.stringify(report, null, 2));

            logger.info('Test raporu oluşturuldu', { path: reportPath });
            return reportPath;
        } catch (error) {
            logger.error('Test raporu oluşturma hatası:', error);
            throw new Error('Test raporu oluşturma başarısız oldu');
        }
    }

    // Genel durumu hesapla
    private calculateOverallStatus(
        e2e: any,
        quality: any,
        style: any
    ): 'excellent' | 'good' | 'fair' | 'poor' {
        const e2eScore = e2e.passed / (e2e.passed + e2e.failed);
        const qualityScore = 1 - (quality.bugs + quality.vulnerabilities) / 100;
        const styleScore = 1 - (style.errors + style.warnings) / 100;

        const overallScore = (e2eScore + qualityScore + styleScore) / 3;

        if (overallScore >= 0.9) return 'excellent';
        if (overallScore >= 0.7) return 'good';
        if (overallScore >= 0.5) return 'fair';
        return 'poor';
    }

    // Öneriler oluştur
    private generateRecommendations(
        e2e: any,
        quality: any,
        style: any
    ): string[] {
        const recommendations: string[] = [];

        if (e2e.failed > 0) {
            recommendations.push(`${e2e.failed} başarısız E2E testi var. Testleri gözden geçirin.`);
        }

        if (quality.bugs > 0) {
            recommendations.push(`${quality.bugs} hata bulundu. Kod kalitesini artırın.`);
        }

        if (quality.vulnerabilities > 0) {
            recommendations.push(`${quality.vulnerabilities} güvenlik açığı bulundu. Güvenlik önlemlerini artırın.`);
        }

        if (quality.codeSmells > 0) {
            recommendations.push(`${quality.codeSmells} kod kokusu bulundu. Kod temizliği yapın.`);
        }

        if (style.errors > 0) {
            recommendations.push(`${style.errors} stil hatası var. Kod stilini düzeltin.`);
        }

        if (style.warnings > 0) {
            recommendations.push(`${style.warnings} stil uyarısı var. Kod stilini iyileştirin.`);
        }

        return recommendations;
    }
} 