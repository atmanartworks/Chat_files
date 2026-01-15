import { useState, useEffect } from 'react';
import { getChatHistory } from '../services/api';
import './ChatHistory.css';

const ChatHistory = ({ onSelectHistory, selectedId }) => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      setLoading(true);
      const data = await getChatHistory(0, 50);
      setHistory(data.history || []);
    } catch (err) {
      console.error('Failed to load chat history:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (historyItem) => {
    if (onSelectHistory) {
      onSelectHistory(historyItem);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
  };

  const truncateText = (text, maxLength = 50) => {
    if (!text) return 'No content';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <div className="chat-history-container">
      <div className="chat-history-header">
        <h2>History</h2>
        <button onClick={loadHistory} className="refresh-button" title="Refresh">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0 1 14.85-3.48L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
          </svg>
        </button>
      </div>

      {loading ? (
        <div className="chat-history-loading">Loading...</div>
      ) : history.length === 0 ? (
        <div className="chat-history-empty">
          <p>No chat history yet</p>
          <p className="empty-hint">Start a conversation to see history</p>
        </div>
      ) : (
        <div className="chat-history-list">
          {history.map((item) => (
            <div
              key={item.id}
              className={`chat-history-item ${selectedId === item.id ? 'selected' : ''}`}
              onClick={() => handleSelect(item)}
            >
              <div className="history-query">{truncateText(item.query)}</div>
              <div className="history-meta">
                <span className="history-mode">{item.mode}</span>
                <span className="history-date">{formatDate(item.created_at)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ChatHistory;
