import { useState, useEffect } from 'react';
import { uploadToVault, getVaultFiles, deleteVaultFile } from '../services/api';
import './Vault.css';

const Vault = ({ onFileUploaded }) => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    try {
      setLoading(true);
      const data = await getVaultFiles();
      setFiles(data.files || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load files');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Check file type
    const allowedTypes = ['.pdf', '.txt', '.docx'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    if (!allowedTypes.includes(fileExtension)) {
      setError('Only PDF, TXT, and DOCX files are allowed');
      return;
    }

    try {
      setUploading(true);
      setError('');
      await uploadToVault(file);
      await loadFiles();
      if (onFileUploaded) {
        onFileUploaded();
      }
      e.target.value = ''; // Reset input
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload file');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (fileId) => {
    if (!window.confirm('Are you sure you want to delete this file?')) {
      return;
    }

    try {
      await deleteVaultFile(fileId);
      await loadFiles();
      if (onFileUploaded) {
        onFileUploaded();
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete file');
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return 'Unknown';
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  const getFileIcon = (fileType) => {
    switch (fileType) {
      case 'pdf':
        return '📄';
      case 'txt':
        return '📝';
      case 'docx':
        return '📘';
      default:
        return '📎';
    }
  };

  return (
    <div className="vault-container">
      <div className="vault-header">
        <h2>📦 Vault</h2>
        <label className="upload-button">
          <input
            type="file"
            accept=".pdf,.txt,.docx"
            onChange={handleFileUpload}
            disabled={uploading}
            style={{ display: 'none' }}
          />
          {uploading ? 'Uploading...' : '+ Upload File'}
        </label>
      </div>

      {error && <div className="vault-error">{error}</div>}

      {loading ? (
        <div className="vault-loading">Loading files...</div>
      ) : files.length === 0 ? (
        <div className="vault-empty">
          <div className="empty-icon">📁</div>
          <p>No files in your vault</p>
          <p className="empty-hint">Upload files to start chatting with them</p>
        </div>
      ) : (
        <div className="vault-files">
          {files.map((file) => (
            <div key={file.id} className="vault-file-item">
              <div className="file-info">
                <span className="file-icon">{getFileIcon(file.file_type)}</span>
                <div className="file-details">
                  <div className="file-name">{file.filename}</div>
                  <div className="file-meta">
                    {formatFileSize(file.file_size)} • {file.file_type.toUpperCase()}
                    {file.processed && <span className="processed-badge">✓ Processed</span>}
                  </div>
                </div>
              </div>
              <button
                onClick={() => handleDelete(file.id)}
                className="delete-button"
                title="Delete file"
              >
                🗑️
              </button>
            </div>
          ))}
        </div>
      )}

      {files.length > 0 && (
        <div className="vault-footer">
          <p>{files.length} file{files.length !== 1 ? 's' : ''} in vault</p>
        </div>
      )}
    </div>
  );
};

export default Vault;
