import * as tf from '@tensorflow/tfjs';
import '@tensorflow/tfjs-node';

export class RiskAnalysisModel {
    private model: tf.Sequential;

    constructor() {
        this.model = this.buildModel();
    }

    private buildModel(): tf.Sequential {
        const model = tf.sequential();
        
        // Giriş katmanı
        model.add(tf.layers.dense({
            units: 64,
            activation: 'relu',
            inputShape: [10] // 10 farklı risk faktörü
        }));

        // Gizli katmanlar
        model.add(tf.layers.dense({ units: 32, activation: 'relu' }));
        model.add(tf.layers.dropout({ rate: 0.2 }));
        model.add(tf.layers.dense({ units: 16, activation: 'relu' }));

        // Çıkış katmanı (risk skoru 0-1 arası)
        model.add(tf.layers.dense({ 
            units: 1, 
            activation: 'sigmoid' 
        }));

        model.compile({
            optimizer: tf.train.adam(0.001),
            loss: 'binaryCrossentropy',
            metrics: ['accuracy']
        });

        return model;
    }

    async train(riskFactors: number[][], riskLabels: number[]): Promise<void> {
        const xs = tf.tensor2d(riskFactors);
        const ys = tf.tensor1d(riskLabels);

        await this.model.fit(xs, ys, {
            epochs: 100,
            batchSize: 32,
            validationSplit: 0.2,
            callbacks: {
                onEpochEnd: (epoch, logs) => {
                    console.log(`Epoch ${epoch}: loss = ${logs?.loss}`);
                }
            }
        });

        xs.dispose();
        ys.dispose();
    }

    async analyzeRisk(factors: number[]): Promise<{
        riskScore: number;
        riskLevel: 'Düşük' | 'Orta' | 'Yüksek';
        recommendations: string[];
    }> {
        const input = tf.tensor2d([factors]);
        const prediction = await this.model.predict(input) as tf.Tensor;
        const riskScore = (await prediction.data())[0];
        
        input.dispose();
        prediction.dispose();

        let riskLevel: 'Düşük' | 'Orta' | 'Yüksek';
        let recommendations: string[] = [];

        if (riskScore < 0.3) {
            riskLevel = 'Düşük';
            recommendations = [
                'Normal portföy çeşitlendirmesi yeterli',
                'Düzenli takip önerilir'
            ];
        } else if (riskScore < 0.7) {
            riskLevel = 'Orta';
            recommendations = [
                'Portföy çeşitlendirmesi artırılmalı',
                'Risk yönetimi stratejileri uygulanmalı',
                'Stop-loss seviyeleri belirlenmeli'
            ];
        } else {
            riskLevel = 'Yüksek';
            recommendations = [
                'Acil risk azaltma önlemleri alınmalı',
                'Portföy yeniden dengelenmeli',
                'Hedge stratejileri uygulanmalı',
                'Yüksek riskli varlıklar azaltılmalı'
            ];
        }

        return {
            riskScore,
            riskLevel,
            recommendations
        };
    }

    calculateValueAtRisk(returns: number[], confidenceLevel: number = 0.95): number {
        const sortedReturns = [...returns].sort((a, b) => a - b);
        const index = Math.floor((1 - confidenceLevel) * sortedReturns.length);
        return sortedReturns[index];
    }

    calculateExpectedShortfall(returns: number[], confidenceLevel: number = 0.95): number {
        const varValue = this.calculateValueAtRisk(returns, confidenceLevel);
        const tailReturns = returns.filter(r => r <= varValue);
        return tailReturns.reduce((sum, r) => sum + r, 0) / tailReturns.length;
    }
} 