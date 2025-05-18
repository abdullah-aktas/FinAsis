import * as tf from '@tensorflow/tfjs';
import { FinancialAnalysisModel } from '../models/FinancialAnalysisModel';
import { AnomalyDetectionModel } from '../models/AnomalyDetectionModel';
import { PortfolioOptimizationModel } from '../models/PortfolioOptimizationModel';
import { RiskAnalysisModel } from '../models/RiskAnalysisModel';
import { createLogger } from '../../utils/logger';
import { ModelCache } from '../../utils/cache';
import { ModelMetrics } from '../types/modelTypes';

const logger = createLogger('ModelManagementService');

export class ModelManagementService {
    private models: {
        financial: FinancialAnalysisModel;
        anomaly: AnomalyDetectionModel;
        portfolio: PortfolioOptimizationModel;
        risk: RiskAnalysisModel;
    };

    private cache: ModelCache;
    private isInitialized: boolean = false;

    constructor() {
        this.models = {
            financial: new FinancialAnalysisModel(),
            anomaly: new AnomalyDetectionModel(),
            portfolio: new PortfolioOptimizationModel(),
            risk: new RiskAnalysisModel()
        };
        this.cache = new ModelCache();
    }

    // Model başlatma
    async initialize(): Promise<void> {
        if (this.isInitialized) {
            logger.info('Modeller zaten başlatılmış');
            return;
        }

        try {
            await tf.ready();
            await this.loadModels();
            this.isInitialized = true;
            logger.info('Modeller başarıyla başlatıldı');
        } catch (error) {
            logger.error('Model başlatma hatası:', error);
            throw new Error('Model başlatma başarısız oldu');
        }
    }

    // Model yükleme
    async loadModels(): Promise<void> {
        try {
            const cachedModels = await this.cache.getModels();
            if (cachedModels) {
                this.models = cachedModels;
                logger.info('Modeller önbellekten yüklendi');
                return;
            }

            await Promise.all([
                this.models.financial.loadModel('financial-model'),
                this.models.anomaly.loadModel('anomaly-model'),
                this.models.portfolio.loadModel('portfolio-model'),
                this.models.risk.loadModel('risk-model')
            ]);

            await this.cache.setModels(this.models);
            logger.info('Modeller başarıyla yüklendi ve önbelleğe alındı');
        } catch (error) {
            logger.error('Model yükleme hatası:', error);
            throw new Error('Model yükleme başarısız oldu');
        }
    }

    // Model kaydetme
    async saveModels(): Promise<void> {
        try {
            await Promise.all([
                this.models.financial.saveModel('financial-model'),
                this.models.anomaly.saveModel('anomaly-model'),
                this.models.portfolio.saveModel('portfolio-model'),
                this.models.risk.saveModel('risk-model')
            ]);

            await this.cache.setModels(this.models);
            logger.info('Modeller başarıyla kaydedildi ve önbelleğe alındı');
        } catch (error) {
            logger.error('Model kaydetme hatası:', error);
            throw new Error('Model kaydetme başarısız oldu');
        }
    }

    // Model güncelleme
    async updateModels(newData: {
        financialData: number[][];
        financialLabels: number[];
        anomalyData: number[][];
        portfolioData: number[][][];
        riskFactors: number[][];
        riskLabels: number[];
    }): Promise<void> {
        if (!this.isInitialized) {
            throw new Error('Modeller başlatılmamış');
        }

        try {
            const [financialMetrics, anomalyMetrics, portfolioMetrics, riskMetrics] = await Promise.all([
                this.models.financial.train(newData.financialData, newData.financialLabels),
                this.models.anomaly.train(newData.anomalyData),
                this.models.portfolio.train(newData.portfolioData),
                this.models.risk.train(newData.riskFactors, newData.riskLabels)
            ]);

            await this.saveModels();
            logger.info('Modeller başarıyla güncellendi', {
                financialMetrics,
                anomalyMetrics,
                portfolioMetrics,
                riskMetrics
            });
        } catch (error) {
            logger.error('Model güncelleme hatası:', error);
            throw new Error('Model güncelleme başarısız oldu');
        }
    }

    // Model tahminleri
    async getPredictions(data: {
        financialInput: number[];
        anomalyInput: number[];
        portfolioInput: number[][];
        riskInput: number[];
    }): Promise<{
        financialPrediction: number;
        anomalyResult: { isAnomaly: boolean; score: number };
        portfolioWeights: number[];
        riskAnalysis: { riskScore: number; riskLevel: string; recommendations: string[] };
    }> {
        if (!this.isInitialized) {
            throw new Error('Modeller başlatılmamış');
        }

        try {
            const cacheKey = JSON.stringify(data);
            const cachedResult = await this.cache.getPrediction(cacheKey);
            if (cachedResult) {
                logger.info('Tahmin sonuçları önbellekten alındı');
                return cachedResult;
            }

            const [
                financialPrediction,
                anomalyResult,
                portfolioWeights,
                riskAnalysis
            ] = await Promise.all([
                this.models.financial.predict(data.financialInput),
                this.models.anomaly.detectAnomaly(data.anomalyInput),
                this.models.portfolio.optimizePortfolio(data.portfolioInput),
                this.models.risk.analyzeRisk(data.riskInput)
            ]);

            const result = {
                financialPrediction,
                anomalyResult,
                portfolioWeights,
                riskAnalysis
            };

            await this.cache.setPrediction(cacheKey, result);
            return result;
        } catch (error) {
            logger.error('Tahmin hatası:', error);
            throw new Error('Tahmin işlemi başarısız oldu');
        }
    }

    // Model performans metrikleri
    async getModelMetrics(testData: {
        financialData: number[][];
        financialLabels: number[];
        anomalyData: number[][];
        portfolioData: number[][][];
        riskFactors: number[][];
        riskLabels: number[];
    }): Promise<ModelMetrics> {
        if (!this.isInitialized) {
            throw new Error('Modeller başlatılmamış');
        }

        try {
            const cacheKey = JSON.stringify(testData);
            const cachedMetrics = await this.cache.getMetrics(cacheKey);
            if (cachedMetrics) {
                logger.info('Model metrikleri önbellekten alındı');
                return cachedMetrics;
            }

            const [
                financialPredictions,
                anomalyResults,
                portfolioMetrics,
                riskMetrics
            ] = await Promise.all([
                Promise.all(testData.financialData.map(data => 
                    this.models.financial.predict(data)
                )),
                Promise.all(testData.anomalyData.map(data => 
                    this.models.anomaly.detectAnomaly(data)
                )),
                this.models.portfolio.calculatePortfolioMetrics(
                    await this.models.portfolio.optimizePortfolio(testData.portfolioData[0]),
                    testData.portfolioData
                ),
                this.calculateRiskMetrics(testData.riskFactors, testData.riskLabels)
            ]);

            const metrics = {
                financialMetrics: this.calculateFinancialMetrics(
                    financialPredictions,
                    testData.financialLabels
                ),
                anomalyMetrics: this.calculateAnomalyMetrics(anomalyResults),
                portfolioMetrics,
                riskMetrics
            };

            await this.cache.setMetrics(cacheKey, metrics);
            return metrics;
        } catch (error) {
            logger.error('Metrik hesaplama hatası:', error);
            throw new Error('Metrik hesaplama başarısız oldu');
        }
    }

    // Yardımcı fonksiyonlar
    private calculateFinancialMetrics(
        predictions: number[],
        actual: number[]
    ): { mse: number; mae: number } {
        const mse = predictions.reduce((sum, pred, i) => 
            sum + Math.pow(pred - actual[i], 2), 0) / predictions.length;
        const mae = predictions.reduce((sum, pred, i) => 
            sum + Math.abs(pred - actual[i]), 0) / predictions.length;
        return { mse, mae };
    }

    private calculateAnomalyMetrics(results: { isAnomaly: boolean; score: number }[]): {
        accuracy: number;
        precision: number;
        recall: number;
    } {
        const truePositives = results.filter(r => r.isAnomaly).length;
        const falsePositives = results.filter(r => !r.isAnomaly).length;
        const falseNegatives = results.length - truePositives - falsePositives;

        const accuracy = (truePositives + falsePositives) / results.length;
        const precision = truePositives / (truePositives + falsePositives);
        const recall = truePositives / (truePositives + falseNegatives);

        return { accuracy, precision, recall };
    }

    private async calculateRiskMetrics(
        riskFactors: number[][],
        riskLabels: number[]
    ): Promise<{ accuracy: number; f1Score: number }> {
        const predictions = await Promise.all(
            riskFactors.map(factors => this.models.risk.analyzeRisk(factors))
        );

        const truePositives = predictions.filter(p => p.riskLevel === 'Yüksek').length;
        const falsePositives = predictions.filter(p => p.riskLevel === 'Orta').length;
        const falseNegatives = predictions.filter(p => p.riskLevel === 'Düşük').length;

        const precision = truePositives / (truePositives + falsePositives);
        const recall = truePositives / (truePositives + falseNegatives);
        const f1Score = 2 * (precision * recall) / (precision + recall);

        return {
            accuracy: (truePositives + falsePositives) / predictions.length,
            f1Score
        };
    }
} 