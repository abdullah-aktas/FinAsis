import axios from 'axios';

const API_BASE = '/api/v2';

export const aiAssistantChat = (message) =>
  axios.post(`${API_BASE}/ai-assistant/assistant/chat/`, { message });

export const completeGamificationTask = (task) =>
  axios.post(`${API_BASE}/education/interactive-exercises/complete-task/`, { task });

export const getBlockchainTransactions = () =>
  axios.get(`${API_BASE}/blockchain/transactions/`);

// Diğer modüller için de benzer fonksiyonlar eklenebilir 