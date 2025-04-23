import * as tf from '@tensorflow/tfjs';
import '@tensorflow/tfjs-node';

export class PortfolioOptimizationModel {
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
            inputShape: [10] // 10 farklı varlık
        }));

        // Gizli katmanlar
        model.add(tf.layers.dense({ units: 32, activation: 'relu' }));
        model.add(tf.layers.dropout({ rate: 0.2 }));
        model.add(tf.layers.dense({ units: 16, activation: 'relu' }));

        // Çıkış katmanı (softmax ile ağırlıkların toplamı 1 olacak)
        model.add(tf.layers.dense({ 
            units: 10, 
            activation: 'softmax' 
        }));

        model.compile({
            optimizer: tf.train.adam(0.001),
            loss: this.customLossFunction,
            metrics: ['accuracy']
        });

        return model;
    }

    private customLossFunction(yTrue: tf.Tensor, yPred: tf.Tensor): tf.Tensor {
        // Sharpe oranını maksimize et
        const returns = tf.mean(yTrue, 1);
        const risk = tf.sqrt(tf.variance(yTrue, 1));
        const sharpeRatio = tf.div(returns, risk);
        
        // Negatif Sharpe oranını minimize et
        return tf.neg(sharpeRatio);
    }

    async train(historicalData: number[][][]): Promise<void> {
        const xs = tf.tensor3d(historicalData);
        const ys = tf.ones([historicalData.length, 10]); // Hedef ağırlıklar

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

    async optimizePortfolio(currentData: number[][]): Promise<number[]> {
        const input = tf.tensor2d([currentData]);
        const weights = await this.model.predict(input) as tf.Tensor;
        const result = await weights.data();
        
        input.dispose();
        weights.dispose();

        return Array.from(result);
    }

    calculatePortfolioMetrics(weights: number[], returns: number[][]): {
        expectedReturn: number;
        risk: number;
        sharpeRatio: number;
    } {
        const portfolioReturns = returns.map(period => 
            period.reduce((sum, ret, i) => sum + ret * weights[i], 0)
        );

        const expectedReturn = portfolioReturns.reduce((sum, ret) => sum + ret, 0) / portfolioReturns.length;
        const risk = Math.sqrt(
            portfolioReturns.reduce((sum, ret) => sum + Math.pow(ret - expectedReturn, 2), 0) / 
            (portfolioReturns.length - 1)
        );
        const sharpeRatio = expectedReturn / risk;

        return {
            expectedReturn,
            risk,
            sharpeRatio
        };
    }
} 