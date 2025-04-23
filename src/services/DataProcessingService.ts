import * as tf from '@tensorflow/tfjs';
import { DataFrame } from 'pandas-js';
import { Chart, registerables } from 'chart.js';
import { createLogger } from '../utils/logger';

Chart.register(...registerables);
const logger = createLogger('DataProcessingService');

export class DataProcessingService {
    private static instance: DataProcessingService;
    private dataFrame: DataFrame | null = null;

    private constructor() {}

    public static getInstance(): DataProcessingService {
        if (!DataProcessingService.instance) {
            DataProcessingService.instance = new DataProcessingService();
        }
        return DataProcessingService.instance;
    }

    // Veri temizleme ve ön işleme
    public async preprocessData(data: any[]): Promise<DataFrame> {
        try {
            this.dataFrame = new DataFrame(data);
            
            // Eksik verileri doldur
            this.dataFrame = this.dataFrame.fillna(0);
            
            // Aykırı değerleri temizle
            this.dataFrame = this.removeOutliers(this.dataFrame);
            
            // Veri normalizasyonu
            this.dataFrame = this.normalizeData(this.dataFrame);
            
            logger.info('Veri ön işleme tamamlandı');
            return this.dataFrame;
        } catch (error) {
            logger.error('Veri ön işleme hatası:', error);
            throw new Error('Veri ön işleme başarısız oldu');
        }
    }

    // Aykırı değerleri temizleme
    private removeOutliers(df: DataFrame): DataFrame {
        const numericColumns = df.columns.filter(col => 
            df[col].dtype === 'number'
        );

        for (const col of numericColumns) {
            const q1 = df[col].quantile(0.25);
            const q3 = df[col].quantile(0.75);
            const iqr = q3 - q1;
            const lowerBound = q1 - 1.5 * iqr;
            const upperBound = q3 + 1.5 * iqr;

            df[col] = df[col].map((val: number) => {
                if (val < lowerBound) return lowerBound;
                if (val > upperBound) return upperBound;
                return val;
            });
        }

        return df;
    }

    // Veri normalizasyonu
    private normalizeData(df: DataFrame): DataFrame {
        const numericColumns = df.columns.filter(col => 
            df[col].dtype === 'number'
        );

        for (const col of numericColumns) {
            const mean = df[col].mean();
            const std = df[col].std();
            df[col] = df[col].map((val: number) => (val - mean) / std);
        }

        return df;
    }

    // TensorFlow.js tensörlerine dönüştürme
    public convertToTensors(df: DataFrame, targetColumn: string): {
        features: tf.Tensor;
        labels: tf.Tensor;
    } {
        try {
            const featureColumns = df.columns.filter(col => col !== targetColumn);
            const features = tf.tensor2d(
                df[featureColumns].values,
                [df.shape[0], featureColumns.length]
            );
            const labels = tf.tensor1d(df[targetColumn].values);

            return { features, labels };
        } catch (error) {
            logger.error('Tensör dönüşüm hatası:', error);
            throw new Error('Tensör dönüşümü başarısız oldu');
        }
    }

    // Görselleştirme fonksiyonları
    public createChart(
        canvas: HTMLCanvasElement,
        data: any,
        type: 'line' | 'bar' | 'scatter' = 'line',
        options: any = {}
    ): Chart {
        try {
            return new Chart(canvas, {
                type,
                data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                        },
                    },
                    ...options,
                },
            });
        } catch (error) {
            logger.error('Grafik oluşturma hatası:', error);
            throw new Error('Grafik oluşturma başarısız oldu');
        }
    }

    // İstatistiksel analiz
    public analyzeData(df: DataFrame): {
        summary: any;
        correlations: any;
        trends: any;
    } {
        try {
            const summary = {};
            const correlations = {};
            const trends = {};

            for (const col of df.columns) {
                if (df[col].dtype === 'number') {
                    summary[col] = {
                        mean: df[col].mean(),
                        median: df[col].median(),
                        std: df[col].std(),
                        min: df[col].min(),
                        max: df[col].max(),
                    };

                    // Korelasyon analizi
                    correlations[col] = {};
                    for (const otherCol of df.columns) {
                        if (otherCol !== col && df[otherCol].dtype === 'number') {
                            correlations[col][otherCol] = df[col].corr(df[otherCol]);
                        }
                    }

                    // Trend analizi
                    trends[col] = this.analyzeTrend(df[col].values);
                }
            }

            return { summary, correlations, trends };
        } catch (error) {
            logger.error('Veri analizi hatası:', error);
            throw new Error('Veri analizi başarısız oldu');
        }
    }

    // Trend analizi
    private analyzeTrend(values: number[]): {
        slope: number;
        direction: 'up' | 'down' | 'stable';
        strength: number;
    } {
        const n = values.length;
        const xMean = (n - 1) / 2;
        const yMean = values.reduce((a, b) => a + b, 0) / n;

        let numerator = 0;
        let denominator = 0;

        for (let i = 0; i < n; i++) {
            numerator += (i - xMean) * (values[i] - yMean);
            denominator += Math.pow(i - xMean, 2);
        }

        const slope = numerator / denominator;
        const direction = slope > 0 ? 'up' : slope < 0 ? 'down' : 'stable';
        const strength = Math.abs(slope);

        return { slope, direction, strength };
    }
} 