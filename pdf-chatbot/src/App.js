import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  // Handle file selection
  const handleFileChange = (event) => {
    setSelectedFiles(Array.from(event.target.files));
    const files = Array.from(event.target.files).map((file) => file.name).join(', ');
    setMessages((prevMessages) => [...prevMessages, { text: `Selected files: ${files}`, type: 'user' }]);
  };

  // Upload PDFs to backend
  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      alert('Please select files first!');
      return;
    }

    const formData = new FormData();
    selectedFiles.forEach((file) => formData.append('files', file));
    formData.append('user_id', 'default_user');

    try {
      setUploading(true);
      const response = await axios.post('http://localhost:8000/upload_pdfs/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(progress);
        },
      });
      setMessages((prevMessages) => [...prevMessages, { text: response.data.message, type: 'bot' }]);
      setSelectedFiles([]);
      setUploadProgress(0);
    } catch (error) {
      setMessages((prevMessages) => [...prevMessages, { text: 'Error uploading PDFs', type: 'bot' }]);
      console.error('Error uploading PDFs:', error);
    } finally {
      setUploading(false);
    }
  };

  // Handle sending questions
  const handleSendMessage = async () => {
    if (inputMessage.trim() !== '') {
      setMessages((prevMessages) => [...prevMessages, { text: inputMessage, type: 'user' }]);
      setInputMessage('');

      // Simulate bot response based on the question (replace this with an API call in real projects)
      try {
        const response = await axios.post('http://localhost:8000/ask/', {
          user_id: 'default_user',
          question: inputMessage,
        });
        setMessages((prevMessages) => [...prevMessages, { text: response.data.answer, type: 'bot' }]);
      } catch (error) {
        setMessages((prevMessages) => [...prevMessages, { text: 'Error fetching answer', type: 'bot' }]);
      }
    }
  };

  return (
    <div className="app-container">
      {/* Chatbot Interface */}
      <div className="chat-container">
        <div className="chat-header">
          <h2>BOT</h2>
        </div>

        {/* Chat Window */}
        <div className="chat-messages">
          {messages.map((message, index) => (
            <div key={index} className={`chat-message ${message.type}`}>
              {message.text}
            </div>
          ))}
        </div>

        {/* Input and File Upload Section */}
        <div className="input-controls">
          <div className="chat-input">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Ask a Question..."
            />
            <button onClick={handleSendMessage}>Send</button>
          </div>

          <div className="file-upload-controls">
            <input
              id="file-upload"
              type="file"
              multiple
              onChange={handleFileChange}
              className="file-input"
            />
            <label htmlFor="file-upload" className="custom-file-upload">
              Browse Files
            </label>
            <button onClick={handleUpload} disabled={uploading || selectedFiles.length === 0} className="action-btn">
              {uploading ? 'Uploading...' : 'Upload PDFs'}
            </button>
            {uploading && (
              <div className="progress-bar-container">
                <div className="progress-bar" style={{ width: `${uploadProgress}%` }}></div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
