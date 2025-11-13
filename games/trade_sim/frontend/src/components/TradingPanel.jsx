/**
 * Enhanced Trading UI
 * Detailed trading interface with price charts and market analysis
 */
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { useGameStore } from '@utils/store';
import { NetworkManager } from '@utils/NetworkManager';
import { AudioManager } from '@utils/AudioManager';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export default function TradingPanel({ cityId, onClose }) {
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [priceHistory, setPriceHistory] = useState([]);
  const [markets, setMarkets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tradeMode, setTradeMode] = useState('buy'); // 'buy' or 'sell'
  
  const player = useGameStore((state) => state.player);

  useEffect(() => {
    loadMarketData();
  }, [cityId]);

  const loadMarketData = async () => {
    try {
      setLoading(true);
      const data = await NetworkManager.getInstance().getCityMarket(cityId);
      setMarkets(data.markets || []);
      
      // Select first product by default
      if (data.markets && data.markets.length > 0) {
        setSelectedProduct(data.markets[0]);
        loadPriceHistory(data.markets[0].product.id);
      }
    } catch (error) {
      console.error('Failed to load market data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadPriceHistory = async (productId) => {
    try {
      // Simulate price history (would come from API in production)
      const history = Array.from({ length: 20 }, (_, i) => ({
        time: `${20 - i}h`,
        price: Math.random() * 200 + 100,
      }));
      setPriceHistory(history);
    } catch (error) {
      console.error('Failed to load price history:', error);
    }
  };

  const handleTrade = async () => {
    if (!selectedProduct) return;

    try {
      AudioManager.getInstance().playSound('click');
      
      const result = await NetworkManager.getInstance().executeTrade({
        city_id: cityId,
        product_id: selectedProduct.product.id,
        quantity: tradeMode === 'buy' ? quantity : -quantity,
      });

      if (result.success) {
        AudioManager.getInstance().playSound('trade');
        useGameStore.getState().updatePlayer({
          coins: result.new_balance,
        });
        
        // Show notification
        useGameStore.getState().addNotification({
          type: 'success',
          title: 'Ticaret Başarılı!',
          message: `${quantity} adet ${selectedProduct.product.name} ${tradeMode === 'buy' ? 'satın aldınız' : 'sattınız'}`,
          reward: { coins: Math.abs(result.profit) },
        });
        
        // Reload market data
        loadMarketData();
      }
    } catch (error) {
      AudioManager.getInstance().playSound('click');
      useGameStore.getState().addNotification({
        type: 'error',
        title: 'Ticaret Başarısız',
        message: error.message,
      });
    }
  };

  const calculateTotal = () => {
    if (!selectedProduct) return 0;
    return selectedProduct.price * quantity;
  };

  const canAfford = () => {
    if (tradeMode === 'sell') return true;
    return player.coins >= calculateTotal();
  };

  // Chart data
  const chartData = {
    labels: priceHistory.map((h) => h.time),
    datasets: [
      {
        label: 'Fiyat',
        data: priceHistory.map((h) => h.price),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: 'Fiyat Geçmişi (Son 20 Saat)',
        color: '#fff',
      },
    },
    scales: {
      y: {
        ticks: { color: '#fff' },
        grid: { color: 'rgba(255, 255, 255, 0.1)' },
      },
      x: {
        ticks: { color: '#fff' },
        grid: { color: 'rgba(255, 255, 255, 0.1)' },
      },
    },
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="fixed inset-0 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="glass max-w-6xl w-full max-h-[90vh] overflow-hidden rounded-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-game-primary to-game-secondary p-6">
          <div className="flex items-center justify-between">
            <h2 className="text-3xl font-bold text-white">Pazar Yeri</h2>
            <button
              onClick={onClose}
              className="w-10 h-10 rounded-lg bg-white/10 hover:bg-white/20 flex items-center justify-center text-white text-xl transition-colors"
            >
              ✕
            </button>
          </div>
          
          {/* Trade Mode Toggle */}
          <div className="mt-4 flex gap-2">
            <button
              onClick={() => setTradeMode('buy')}
              className={`px-6 py-2 rounded-lg font-semibold transition-all ${
                tradeMode === 'buy'
                  ? 'bg-green-500 text-white'
                  : 'bg-white/10 text-white/60 hover:bg-white/20'
              }`}
            >
              💰 Satın Al
            </button>
            <button
              onClick={() => setTradeMode('sell')}
              className={`px-6 py-2 rounded-lg font-semibold transition-all ${
                tradeMode === 'sell'
                  ? 'bg-orange-500 text-white'
                  : 'bg-white/10 text-white/60 hover:bg-white/20'
              }`}
            >
              🏷️ Sat
            </button>
          </div>
        </div>

        {loading ? (
          <div className="p-8 text-center text-white">
            <div className="animate-spin w-12 h-12 border-4 border-game-accent border-t-transparent rounded-full mx-auto" />
            <p className="mt-4">Pazar verileri yükleniyor...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 p-6 max-h-[calc(90vh-12rem)] overflow-y-auto">
            {/* Left: Product List */}
            <div className="space-y-2">
              <h3 className="text-white font-semibold mb-3">Ürünler</h3>
              {markets.map((market) => (
                <motion.div
                  key={market.product.id}
                  whileHover={{ scale: 1.02 }}
                  onClick={() => {
                    setSelectedProduct(market);
                    loadPriceHistory(market.product.id);
                    AudioManager.getInstance().playSound('click');
                  }}
                  className={`p-4 rounded-lg cursor-pointer transition-all ${
                    selectedProduct?.product.id === market.product.id
                      ? 'bg-game-accent/20 border-2 border-game-accent'
                      : 'bg-white/5 hover:bg-white/10 border-2 border-transparent'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="text-white font-semibold">
                        {market.product.name}
                      </h4>
                      <p className="text-xs text-gray-400 mt-1">
                        {market.product.category}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-game-accent font-bold">
                        {market.price} 💰
                      </p>
                      <p className="text-xs text-gray-400">
                        {market.product.unit}
                      </p>
                    </div>
                  </div>
                  
                  {/* Supply & Demand indicators */}
                  <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <div className="text-gray-400">Arz</div>
                      <div className="bg-white/10 rounded-full h-2 mt-1">
                        <div
                          className="bg-blue-500 h-2 rounded-full"
                          style={{ width: `${market.supply}%` }}
                        />
                      </div>
                    </div>
                    <div>
                      <div className="text-gray-400">Talep</div>
                      <div className="bg-white/10 rounded-full h-2 mt-1">
                        <div
                          className="bg-red-500 h-2 rounded-full"
                          style={{ width: `${market.demand}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Middle: Price Chart */}
            <div className="lg:col-span-2 space-y-4">
              {selectedProduct && (
                <>
                  {/* Product Detail */}
                  <div className="glass p-4 rounded-lg">
                    <h3 className="text-white text-xl font-bold mb-2">
                      {selectedProduct.product.name}
                    </h3>
                    <p className="text-gray-300 text-sm mb-4">
                      {selectedProduct.product.description || 'Ticaret için uygun ürün'}
                    </p>
                    
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-400">Mevcut Fiyat:</span>
                        <p className="text-game-accent text-2xl font-bold">
                          {selectedProduct.price} 💰
                        </p>
                      </div>
                      <div>
                        <span className="text-gray-400">Temel Fiyat:</span>
                        <p className="text-white text-xl">
                          {selectedProduct.product.base_price} 💰
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Price Chart */}
                  <div className="glass p-4 rounded-lg h-64">
                    <Line data={chartData} options={chartOptions} />
                  </div>

                  {/* Trade Form */}
                  <div className="glass p-6 rounded-lg">
                    <h3 className="text-white font-semibold mb-4">
                      {tradeMode === 'buy' ? 'Satın Alma' : 'Satış'} İşlemi
                    </h3>
                    
                    <div className="space-y-4">
                      {/* Quantity */}
                      <div>
                        <label className="text-gray-400 text-sm block mb-2">
                          Miktar
                        </label>
                        <div className="flex gap-2">
                          <button
                            onClick={() => setQuantity(Math.max(1, quantity - 1))}
                            className="w-12 h-12 bg-white/10 hover:bg-white/20 rounded-lg text-white text-xl font-bold transition-colors"
                          >
                            −
                          </button>
                          <input
                            type="number"
                            value={quantity}
                            onChange={(e) =>
                              setQuantity(Math.max(1, parseInt(e.target.value) || 1))
                            }
                            className="flex-1 bg-white/10 border border-white/20 rounded-lg px-4 text-white text-center text-xl font-bold focus:outline-none focus:border-game-accent"
                            min="1"
                          />
                          <button
                            onClick={() => setQuantity(quantity + 1)}
                            className="w-12 h-12 bg-white/10 hover:bg-white/20 rounded-lg text-white text-xl font-bold transition-colors"
                          >
                            +
                          </button>
                        </div>
                      </div>

                      {/* Total */}
                      <div className="bg-white/5 p-4 rounded-lg">
                        <div className="flex justify-between items-center text-lg">
                          <span className="text-gray-400">Toplam:</span>
                          <span className="text-white font-bold">
                            {calculateTotal()} 💰
                          </span>
                        </div>
                        <div className="flex justify-between items-center text-sm mt-2">
                          <span className="text-gray-400">Bakiyeniz:</span>
                          <span className={canAfford() ? 'text-green-400' : 'text-red-400'}>
                            {player.coins} 💰
                          </span>
                        </div>
                      </div>

                      {/* Trade Button */}
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={handleTrade}
                        disabled={!canAfford() && tradeMode === 'buy'}
                        className={`w-full py-4 rounded-lg font-bold text-lg transition-all ${
                          canAfford() || tradeMode === 'sell'
                            ? 'bg-gradient-to-r from-game-primary to-game-secondary text-white hover:shadow-xl'
                            : 'bg-gray-600 text-gray-400 cursor-not-allowed'
                        }`}
                      >
                        {tradeMode === 'buy' ? '💰 Satın Al' : '🏷️ Sat'}
                      </motion.button>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}
