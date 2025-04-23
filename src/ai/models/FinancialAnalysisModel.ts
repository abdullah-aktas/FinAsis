import * as tf from '@tensorflow/tfjs';

export class FinancialAnalysisModel {
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
            inputShape: [10] // Son 10 günlük veri
        }));

        // Gizli katmanlar
        model.add(tf.layers.dense({ units: 32, activation: 'relu' }));
        model.add(tf.layers.dropout({ rate: 0.2 }));
        model.add(tf.layers.dense({ units: 16, activation: 'relu' }));

        // Çıkış katmanı
        model.add(tf.layers.dense({ units: 1, activation: 'linear' }));

        // Model derleme
        model.compile({
            optimizer: tf.train.adam(0.001),
            loss: 'meanSquaredError',
            metrics: ['mae']
        });

        return model;
    }

    async train(data: number[][], labels: number[]): Promise<void> {
        const xs = tf.tensor2d(data);
        const ys = tf.tensor1d(labels);

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

    async predict(data: number[]): Promise<number> {
        const input = tf.tensor2d([data]);
        const prediction = this.model.predict(input) as tf.Tensor;
        const result = await prediction.data();
        input.dispose();
        prediction.dispose();
        return result[0];
    }

    async saveModel(path: string): Promise<void> {
        await this.model.save(`localstorage://${path}`);
    }

    async loadModel(path: string): Promise<void> {
        this.model = await tf.loadLayersModel(`localstorage://${path}`);
    }
} 