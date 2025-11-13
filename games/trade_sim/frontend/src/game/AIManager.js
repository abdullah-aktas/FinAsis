// AIManager: Basit ticaret botları ve şehirler arası dinamik NPC hareketleri
import * as tf from '@tensorflow/tfjs';

export class TradeBot {
  constructor(name, city) {
    this.name = name;
    this.city = city;
    this.model = null;
  }
  async init() {
    // Basit model: fiyat tahmini
    this.model = tf.sequential();
    this.model.add(tf.layers.dense({ units: 8, inputShape: [2], activation: 'relu' }));
    this.model.add(tf.layers.dense({ units: 1 }));
    this.model.compile({ optimizer: 'adam', loss: 'meanSquaredError' });
  }
  async predict(price, volume) {
    if (!this.model) await this.init();
    const input = tf.tensor2d([[price, volume]]);
    const output = this.model.predict(input);
    return output.dataSync()[0];
  }
}

export function createNPCs(cityList) {
  // Şehirler arası dinamik NPC oluştur
  return cityList.map((city, i) => new TradeBot(`NPC_${i+1}`, city));
}
// AIManager ile NPC’lerin pazar analizi ve ticaret kararları
