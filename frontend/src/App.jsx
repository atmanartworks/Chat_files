import { useState, useEffect } from 'react';
import Login from './components/Login';
import Vault from './components/Vault';
import ChatHistory from './components/ChatHistory';
import ChatInterface from './components/ChatInterface';
import { getToken, getCurrentUser, logout } from './services/api';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showVault, setShowVault] = useState(true);
  const [showHistory, setShowHistory] = useState(true);
  const [selectedConversation, setSelectedConversation] = useState(null);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = getToken();
    if (token) {
      try {
        const userData = await getCurrentUser();
        setUser(userData);
        setIsAuthenticated(true);
      } catch (err) {
        // Token invalid, clear it
        logout();
      }
    }
    setLoading(false);
  };

  const handleLoginSuccess = async () => {
    const userData = await getCurrentUser();
    setUser(userData);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    logout();
    setIsAuthenticated(false);
    setUser(null);
  };

  const handleFileUploaded = () => {
    // Refresh vault or chat interface if needed
  };

  const handleSelectConversation = (historyItem) => {
    // Load the conversation into chat interface
    setSelectedConversation(historyItem);
  };

  const handleNewChat = () => {
    // Clear selected conversation for new chat
    setSelectedConversation(null);
  };

  if (loading) {
    return (
      <div className="app-loading">
        <div className="loading-spinner">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div className="app">
      <div className="app-layout">
        {/* Sidebar with Vault and History */}
        <div className="app-sidebar">
          {showVault && <Vault onFileUploaded={handleFileUploaded} />}
          {showHistory && <ChatHistory onSelectHistory={handleSelectConversation} selectedId={selectedConversation?.id} />}
        </div>

        {/* Main Chat Interface */}
        <div className="app-main-content">
          <div className="app-topbar">
            <div className="topbar-left">
              <button
                onClick={() => setShowVault(!showVault)}
                className="toggle-button"
                title={showVault ? 'Hide Vault' : 'Show Vault'}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                  <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
                  <line x1="12" y1="22.08" x2="12" y2="12"/>
                </svg>
              </button>
              <button
                onClick={() => setShowHistory(!showHistory)}
                className="toggle-button"
                title={showHistory ? 'Hide History' : 'Show History'}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
              </button>
      </div>
            <div className="topbar-right">
              <span className="user-info">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginRight: '0.5rem', verticalAlign: 'middle' }}>
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                  <circle cx="12" cy="7" r="4"/>
                </svg>
                {user?.username}
              </span>
              <button onClick={handleLogout} className="logout-button">
                Logout
        </button>
            </div>
          </div>
          <ChatInterface 
            isReady={true} 
            selectedConversation={selectedConversation}
            onNewChat={handleNewChat}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
