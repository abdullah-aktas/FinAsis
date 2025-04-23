import * as tf from '@tensorflow/tfjs';

export class AnomalyDetectionModel {
    private model: tf.Sequential;
    private threshold: number;

    constructor() {
        this.model = this.buildModel();
        this.threshold = 0.1; // Varsayılan eşik değeri
    }

    private buildModel(): tf.Sequential {
        const model = tf.sequential();
        
        // Encoder
        model.add(tf.layers.dense({
            units: 32,
            activation: 'relu',
            inputShape: [10]
        }));
        model.add(tf.layers.dense({ units: 16, activation: 'relu' }));
        model.add(tf.layers.dense({ units: 8, activation: 'relu' }));

        // Decoder
        model.add(tf.layers.dense({ units: 16, activation: 'relu' }));
        model.add(tf.layers.dense({ units: 32, activation: 'relu' }));
        model.add(tf.layers.dense({ units: 10, activation: 'linear' }));

        model.compile({
            optimizer: tf.train.adam(0.001),
            loss: 'meanSquaredError'
        });

        return model;
    }

    async train(data: number[][]): Promise<void> {
        const xs = tf.tensor2d(data);
        
        await this.model.fit(xs, xs, {
            epochs: 100,
            batchSize: 32,
            validationSplit: 0.2,
            callbacks: {
                onEpochEnd: (epoch, logs) => {
                    console.log(`Epoch ${epoch}: loss = ${logs?.loss}`);
                }
            }
        });

        // Eşik değerini belirle
        const reconstructions = await this.model.predict(xs) as tf.Tensor;
        const errors = tf.mean(tf.square(tf.sub(xs, reconstructions)), 1);
        const errorData = await errors.data();
        this.threshold = Math.max(...errorData) * 1.5;

        xs.dispose();
        reconstructions.dispose();
        errors.dispose();
    }

    async detectAnomaly(data: number[]): Promise<{ isAnomaly: boolean; score: number }> {
        const input = tf.tensor2d([data]);
        const reconstruction = await this.model.predict(input) as tf.Tensor;
        const error = tf.mean(tf.square(tf.sub(input, reconstruction)), 1);
        const errorData = await error.data();
        
        input.dispose();
        reconstruction.dispose();
        error.dispose();

        return {
            isAnomaly: errorData[0] > this.threshold,
            score: errorData[0]
        };
    }

    async saveModel(path: string): Promise<void> {
        await this.model.save(`localstorage://${path}`);
    }

    async loadModel(path: string): Promise<void> {
        this.model = await tf.loadLayersModel(`localstorage://${path}`);
    }
} 