import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management
export const getToken = () => localStorage.getItem('access_token');
export const setToken = (token) => localStorage.setItem('access_token', token);
export const removeToken = () => localStorage.removeItem('access_token');
export const getUserId = () => localStorage.getItem('user_id');
export const setUserId = (id) => localStorage.setItem('user_id', id);
export const removeUserId = () => localStorage.removeItem('user_id');

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle 401 errors (unauthorized)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      removeToken();
      removeUserId();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication
export const register = async (username, email, password) => {
  const response = await api.post('/register', {
    username,
    email,
    password,
  });
  return response.data;
};

export const login = async (username, password) => {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);
  
  const response = await api.post('/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  
  if (response.data.access_token) {
    setToken(response.data.access_token);
    setUserId(response.data.user_id);
  }
  
  return response.data;
};

export const logout = () => {
  removeToken();
  removeUserId();
};

export const getCurrentUser = async () => {
  const response = await api.get('/me');
  return response.data;
};

// Vault - Upload file
export const uploadToVault = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/vault/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

// Vault - Get all files
export const getVaultFiles = async () => {
  const response = await api.get('/vault/files');
  return response.data;
};

// Vault - Delete file
export const deleteVaultFile = async (fileId) => {
  const response = await api.delete(`/vault/files/${fileId}`);
  return response.data;
};

// Legacy file upload (for backward compatibility)
export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

// Chat with document (streaming)
export const sendChatMessageStream = async (query, generatePdf = false, useRag = true, onChunk) => {
  const token = getToken();
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : '',
    },
    body: JSON.stringify({
      query,
      generate_pdf: generatePdf,
      use_rag: useRag,
      stream: true,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get response');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let fullResponse = '';
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6));
          if (data.error) {
            throw new Error(data.error);
          }
          if (data.chunk) {
            fullResponse += data.chunk;
            if (onChunk) {
              // Call onChunk immediately for real-time streaming
              onChunk(data.chunk, fullResponse);
            }
          }
          if (data.done) {
            return {
              answer: data.full_response || fullResponse,
              mode: useRag ? 'rag' : 'generation',
              citations: data.citations || null,
              vault_files: data.vault_files || null,
            };
          }
        } catch (e) {
          console.error('Error parsing SSE data:', e);
        }
      }
    }
  }

  return {
    answer: fullResponse,
    mode: useRag ? 'rag' : 'generation',
  };
};

// Chat with document (non-streaming, for PDF generation)
export const sendChatMessage = async (query, generatePdf = false, useRag = true) => {
  const response = await api.post('/chat', {
    query,
    generate_pdf: generatePdf,
    use_rag: useRag,
    stream: false,
  });
  
  return response.data;
};

// Generate PDF from content
export const generatePdf = async (content, filename = null) => {
  const response = await api.post('/generate-pdf', {
    content,
    filename,
  });
  
  return response.data;
};

// Download PDF
export const downloadPdf = (filename) => {
  return `${API_BASE_URL}/download-pdf/${filename}`;
};

// Search for keyword in document
export const searchKeyword = async (keyword) => {
  const response = await api.post('/search-keyword', {
    keyword,
  });
  return response.data;
};

// Search for multiple keywords
export const searchKeywords = async (keywords) => {
  const response = await api.post('/search-keywords', {
    keywords,
  });
  return response.data;
};

// Get chat history
export const getChatHistory = async (skip = 0, limit = 50) => {
  const response = await api.get(`/chat-history?skip=${skip}&limit=${limit}`);
  return response.data;
};

// Get documents
export const getDocuments = async () => {
  const response = await api.get('/documents');
  return response.data;
};

export default api;
