import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useGameStore } from '@utils/store';
import { NetworkManager } from '@utils/NetworkManager';

export default function ChatPanel() {
  const { toggleUI } = useGameStore();
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [currentRoom, setCurrentRoom] = useState('global');
  const messagesEndRef = useRef(null);

  const rooms = [
    { id: 'global', name: '🌍 Genel', color: 'text-blue-400' },
    { id: 'trade', name: '💰 Ticaret', color: 'text-green-400' },
    { id: 'guild', name: '🏰 Lonca', color: 'text-purple-400' },
  ];

  useEffect(() => {
    // Load chat messages
    const loadMessages = async () => {
      const msgs = await NetworkManager.getInstance().getChatMessages(currentRoom);
      setMessages(msgs);
    };

    loadMessages();

    // Listen for new messages
    const network = NetworkManager.getInstance();
    network.on('chat:message', (data) => {
      if (data.room === currentRoom) {
        setMessages(prev => [...prev, data]);
      }
    });
  }, [currentRoom]);

  useEffect(() => {
    // Scroll to bottom when new message
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    try {
      await NetworkManager.getInstance().sendChatMessage(currentRoom, inputValue);
      setInputValue('');
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 50 }}
      className="absolute bottom-20 left-4 w-96 pointer-events-auto"
    >
      <div className="glass rounded-2xl overflow-hidden">
        {/* Header */}
        <div className="bg-white/5 p-4 flex items-center justify-between border-b border-white/10">
          <h2 className="text-xl font-bold gradient-text">
            💬 Sohbet
          </h2>
          <button
            onClick={() => toggleUI('showChat')}
            className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white/10 transition-colors text-gray-400 hover:text-white"
          >
            ✕
          </button>
        </div>

        {/* Room tabs */}
        <div className="flex space-x-2 p-2 bg-white/5 border-b border-white/10">
          {rooms.map(room => (
            <button
              key={room.id}
              onClick={() => setCurrentRoom(room.id)}
              className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                currentRoom === room.id
                  ? 'bg-white/20 ' + room.color
                  : 'hover:bg-white/10 text-gray-400'
              }`}
            >
              {room.name}
            </button>
          ))}
        </div>

        {/* Messages */}
        <div className="h-96 overflow-y-auto p-4 space-y-3">
          {messages.map((msg, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex flex-col"
            >
              <div className="flex items-baseline space-x-2 mb-1">
                <span className="font-bold text-sm text-game-accent">
                  {msg.user?.username || 'Anonim'}
                </span>
                <span className="text-xs text-gray-500">
                  {new Date(msg.created_at).toLocaleTimeString()}
                </span>
              </div>
              <div className="bg-white/5 rounded-lg px-3 py-2 text-sm text-white">
                {msg.message}
              </div>
            </motion.div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 bg-white/5 border-t border-white/10">
          <div className="flex space-x-2">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Mesaj yaz..."
              className="flex-1 px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-game-accent"
            />
            <button
              onClick={handleSend}
              className="px-4 py-2 bg-gradient-to-r from-game-accent to-game-purple rounded-lg font-semibold hover:opacity-90 transition-opacity"
            >
              Gönder
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
