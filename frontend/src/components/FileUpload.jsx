import { useState } from 'react';
import { uploadFile } from '../services/api';
import './FileUpload.css';

const FileUpload = ({ onUploadSuccess, onUploadError }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // Check file type
      const allowedTypes = ['.pdf', '.txt', '.docx'];
      const fileExtension = selectedFile.name.toLowerCase().substring(selectedFile.name.lastIndexOf('.'));
      
      if (!allowedTypes.includes(fileExtension)) {
        setUploadStatus({ type: 'error', message: 'Please upload a PDF, TXT, or DOCX file' });
        setFile(null);
        return;
      }
      
      setFile(selectedFile);
      setUploadStatus(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setUploadStatus({ type: 'error', message: 'Please select a file first' });
      return;
    }

    setUploading(true);
    setUploadStatus({ type: 'info', message: 'Uploading and processing file...' });

    try {
      const result = await uploadFile(file);
      setUploadStatus({ type: 'success', message: result.message || 'File uploaded successfully!' });
      if (onUploadSuccess) {
        onUploadSuccess(result);
      }
      setFile(null);
      // Reset file input
      document.getElementById('file-input').value = '';
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to upload file';
      setUploadStatus({ type: 'error', message: errorMessage });
      if (onUploadError) {
        onUploadError(error);
      }
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="file-upload-container">
      <div className="file-upload-card">
        <div className="upload-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="17 8 12 3 7 8"></polyline>
            <line x1="12" y1="3" x2="12" y2="15"></line>
          </svg>
        </div>
        
        <h2>Upload Document</h2>
        <p className="upload-description">
          Upload a PDF, TXT, or DOCX file to start chatting with your document
        </p>

        <div className="file-input-wrapper">
          <input
            id="file-input"
            type="file"
            accept=".pdf,.txt,.docx"
            onChange={handleFileChange}
            disabled={uploading}
            className="file-input"
          />
          <label htmlFor="file-input" className="file-input-label">
            {file ? file.name : 'Choose File'}
          </label>
        </div>

        {file && (
          <div className="file-info">
            <span className="file-name">{file.name}</span>
            <span className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
          </div>
        )}

        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="upload-button"
        >
          {uploading ? 'Processing...' : 'Upload & Process'}
        </button>

        {uploadStatus && (
          <div className={`upload-status ${uploadStatus.type}`}>
            {uploadStatus.message}
          </div>
        )}
      </div>
    </div>
  );
};

export default FileUpload;
