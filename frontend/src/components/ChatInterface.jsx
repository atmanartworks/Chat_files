import { useState, useRef, useEffect } from 'react';
import { sendChatMessage, sendChatMessageStream, downloadPdf } from '../services/api';
import './ChatInterface.css';

const ChatInterface = ({ isReady, selectedConversation, onNewChat }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [generatePdf, setGeneratePdf] = useState(false);
  const [useRag, setUseRag] = useState(true);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load conversation when selected
  useEffect(() => {
    if (selectedConversation) {
      // Parse citations if available
      let citations = null;
      try {
        if (selectedConversation.citations) {
          citations = typeof selectedConversation.citations === 'string' 
            ? JSON.parse(selectedConversation.citations) 
            : selectedConversation.citations;
        }
      } catch (e) {
        console.error('Error parsing citations:', e);
      }

      // Parse vault files if available (for greeting messages)
      let vaultFiles = null;
      if (selectedConversation.vault_files) {
        vaultFiles = selectedConversation.vault_files;
      }

      // Load the conversation messages
      const conversationMessages = [
        {
          role: 'user',
          content: selectedConversation.query,
        },
        {
          role: 'assistant',
          content: selectedConversation.response,
          mode: selectedConversation.mode || 'rag',
          citations: citations,
          vaultFiles: vaultFiles,
          pdfUrl: selectedConversation.pdf_url || null,
          pdfGenerated: selectedConversation.pdf_generated || false,
        }
      ];
      
      setMessages(conversationMessages);
    } else {
      // Clear messages when no conversation selected (new chat)
      setMessages([]);
    }
  }, [selectedConversation]);

  const handleSend = async () => {
    if (!input.trim() || loading || !isReady) return;

    const userMessage = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    // Detect greetings (hi, hello, hey) - use non-streaming for instant response
    const greetingKeywords = ["hi", "hello", "hey", "hai", "namaste", "greetings"];
    const userMessageLower = userMessage.toLowerCase().trim();
    const isGreeting = greetingKeywords.includes(userMessageLower) || 
                       greetingKeywords.some(g => userMessageLower === `${g}!` || userMessageLower === `${g}.`);

    // Auto-detect if user wants generation (keywords like "generate", "create", "write")
    const generationKeywords = ["generate", "create", "write", "make", "prepare", "draft"];
    const wantsGeneration = generationKeywords.some(keyword => userMessage.toLowerCase().includes(keyword));
    const shouldUseRag = useRag && !wantsGeneration;

    try {
      // Show typing indicator immediately (FounderGPT style - instant feedback)
      setMessages((prev) => [...prev, { role: 'assistant', content: '', mode: 'greeting', streaming: true, typing: true }]);
      setLoading(false); // Allow user to type next message immediately
      inputRef.current?.focus();
      
      // If greeting, use streaming for instant response
      if (isGreeting) {
        const streamResponse = await sendChatMessageStream(
          userMessage,
          false,
          false,
          (chunk, fullResponse) => {
            // Update message immediately as chunks arrive
            setMessages((prev) => {
              const newMessages = [...prev];
              if (newMessages.length > 0 && newMessages[newMessages.length - 1].role === 'assistant') {
                newMessages[newMessages.length - 1] = {
                  ...newMessages[newMessages.length - 1],
                  content: fullResponse,
                  streaming: true,
                  typing: false, // Remove typing once first chunk arrives
                };
              }
              return newMessages;
            });
            setTimeout(() => scrollToBottom(), 10);
          }
        );
        
        // Mark streaming complete and add vault files
        setMessages((prev) => {
          const newMessages = [...prev];
          if (newMessages.length > 0 && newMessages[newMessages.length - 1].role === 'assistant') {
            newMessages[newMessages.length - 1] = {
              ...newMessages[newMessages.length - 1],
              streaming: false,
              vaultFiles: streamResponse.vault_files || null,
            };
          }
          return newMessages;
        });
        return;
      }

      // If PDF generation is needed, use non-streaming
      if (generatePdf) {
        const response = await sendChatMessage(userMessage, generatePdf, shouldUseRag);
        
      const assistantMessage = {
        role: 'assistant',
        content: response.answer,
        pdfUrl: response.pdf_url || null,
        pdfGenerated: response.pdf_generated || false,
        mode: response.mode || 'rag',
        citations: response.citations || null,
      };

        setMessages((prev) => [...prev, assistantMessage]);
        setLoading(false);
        inputRef.current?.focus();
        return;
      }

      // Use streaming for faster perceived response (FounderGPT-like)
      // Typing indicator already shown above, just update mode
      setMessages((prev) => {
        const newMessages = [...prev];
        if (newMessages.length > 0 && newMessages[newMessages.length - 1].role === 'assistant') {
          newMessages[newMessages.length - 1] = {
            ...newMessages[newMessages.length - 1],
            mode: shouldUseRag ? 'rag' : 'generation',
            typing: true,
          };
        }
        return newMessages;
      });
      
      const streamResponse = await sendChatMessageStream(
        userMessage,
        false,
        shouldUseRag,
        (chunk, fullResponse) => {
          // Update the last message with streaming content in real-time (INSTANT)
          setMessages((prev) => {
            const newMessages = [...prev];
            if (newMessages.length > 0 && newMessages[newMessages.length - 1].role === 'assistant') {
              newMessages[newMessages.length - 1] = {
                ...newMessages[newMessages.length - 1],
                content: fullResponse,
                streaming: true,
                typing: false, // Remove typing indicator once first chunk arrives
              };
            }
            return newMessages;
          });
          // Auto-scroll during streaming (throttled for performance)
          requestAnimationFrame(() => scrollToBottom());
        }
      );
      
      // Mark streaming as complete
      setMessages((prev) => {
        const newMessages = [...prev];
        if (newMessages.length > 0 && newMessages[newMessages.length - 1].role === 'assistant') {
          newMessages[newMessages.length - 1] = {
            ...newMessages[newMessages.length - 1],
            streaming: false,
          };
        }
        return newMessages;
      });
      
      // Update message with citations if available
      if (streamResponse && streamResponse.citations) {
        setMessages((prev) => {
          const newMessages = [...prev];
          if (newMessages.length > 0) {
            newMessages[newMessages.length - 1] = {
              ...newMessages[newMessages.length - 1],
              citations: streamResponse.citations,
            };
          }
          return newMessages;
        });
      }
    } catch (error) {
      const errorMessage = error.message || error.response?.data?.detail || 'Failed to get response';
      setMessages((prev) => {
        const newMessages = [...prev];
        // Remove the empty assistant message if it exists
        if (newMessages[newMessages.length - 1]?.content === '') {
          newMessages.pop();
        }
        return [...newMessages, { role: 'assistant', content: `Error: ${errorMessage}`, isError: true }];
      });
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = `${Math.min(inputRef.current.scrollHeight, 200)}px`;
    }
  }, [input]);

  const formatMessage = (content, citations = null) => {
    // Parse inline citations like [1], [2], [3] (FounderGPT style)
    const citationRegex = /\[(\d+)\]/g;
    const parts = [];
    let lastIndex = 0;
    let match;
    
    // Find all citation references
    const citationMatches = [];
    while ((match = citationRegex.exec(content)) !== null) {
      citationMatches.push({
        index: match.index,
        number: parseInt(match[1]),
        fullMatch: match[0]
      });
    }
    
    // Process content with citations
    if (citationMatches.length > 0) {
      citationMatches.forEach((citation, idx) => {
        // Add text before citation
        if (citation.index > lastIndex) {
          const textBefore = content.substring(lastIndex, citation.index);
          if (textBefore) {
            parts.push({ type: 'text', content: textBefore, key: `text-${idx}` });
          }
        }
        
        // Add citation
        parts.push({
          type: 'citation',
          number: citation.number,
          fullMatch: citation.fullMatch,
          key: `citation-${idx}`
        });
        
        lastIndex = citation.index + citation.fullMatch.length;
      });
      
      // Add remaining text
      if (lastIndex < content.length) {
        const remainingText = content.substring(lastIndex);
        if (remainingText) {
          parts.push({ type: 'text', content: remainingText, key: 'text-final' });
        }
      }
    } else {
      // No citations found, just return text
      parts.push({ type: 'text', content: content, key: 'text-only' });
    }
    
    // Render parts with formatting
    const formatted = [];
    parts.forEach((part, partIdx) => {
      if (part.type === 'citation') {
        const citationInfo = citations?.find(c => c.id === part.number);
        formatted.push(
          <span
            key={part.key}
            className="inline-citation"
            title={citationInfo ? `${citationInfo.source}${citationInfo.page ? `, Page ${citationInfo.page}` : ''}` : ''}
          >
            {part.fullMatch}
          </span>
        );
      } else {
        // Format text with markdown and line breaks
        const lines = part.content.split('\n');
        lines.forEach((line, i) => {
          if (line.startsWith('```')) {
            formatted.push(<div key={`${part.key}-${i}`} className="code-block">{line}</div>);
          } else if (line.includes('**')) {
            // Format markdown bold
            const lineParts = line.split(/(\*\*.*?\*\*)/g);
            formatted.push(
              <p key={`${part.key}-${i}`} style={{ margin: '0.5rem 0' }}>
                {lineParts.map((linePart, j) => {
                  if (linePart.startsWith('**') && linePart.endsWith('**')) {
                    const keyword = linePart.slice(2, -2);
                    return <mark key={j} className="highlighted-keyword">{keyword}</mark>;
                  }
                  return <span key={j}>{linePart}</span>;
                })}
              </p>
            );
          } else if (line.trim()) {
            formatted.push(<p key={`${part.key}-${i}`} style={{ margin: '0.5rem 0' }}>{line}</p>);
          } else {
            formatted.push(<br key={`${part.key}-${i}`} />);
          }
        });
      }
    });
    
    return formatted;
  };

  return (
    <div className="chatgpt-interface">
      {/* Header */}
      <div className="chatgpt-header">
        <div className="header-title">
          <h1>FounderGPT</h1>
        </div>
        <div className="header-actions">
          <button 
            className="header-btn" 
            onClick={() => {
              setMessages([]);
              if (onNewChat) {
                onNewChat();
              }
            }} 
            title="New Chat"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 5v14M5 12h14"/>
            </svg>
          </button>
        </div>
      </div>

      {/* Messages Container */}
      <div className="chatgpt-messages">
        {messages.length === 0 ? (
          <div className="chatgpt-empty">
            <div className="empty-avatar">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
            </div>
            <h2>How can I help you today?</h2>
            <div className="empty-suggestions">
              <button className="suggestion-btn" onClick={() => setInput("What is this document about?")}>
                What is this document about?
              </button>
              <button className="suggestion-btn" onClick={() => setInput("Summarize the key points")}>
                Summarize the key points
              </button>
              <button className="suggestion-btn" onClick={() => setInput("Explain the main concepts")}>
                Explain the main concepts
              </button>
            </div>
          </div>
        ) : (
          <div className="messages-list">
            {messages.map((msg, idx) => (
              <div key={idx} className={`chatgpt-message ${msg.role}`}>
                <div className="message-avatar">
                  {msg.role === 'user' ? (
                    <div className="avatar-user">U</div>
                  ) : (
                    <div className="avatar-assistant">
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                      </svg>
                    </div>
                  )}
                </div>
                <div className="message-wrapper">
                  {msg.typing && !msg.content ? (
                    <div className="typing-dots">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  ) : (
                    <div className={`message-text ${msg.streaming ? 'streaming' : ''}`}>
                      {formatMessage(msg.content, msg.citations)}
                    </div>
                  )}
                  {msg.vaultFiles && msg.vaultFiles.length > 0 && (
                    <div className="message-vault-files">
                      <div className="vault-files-title">Files in your vault:</div>
                      <div className="vault-files-list">
                        {msg.vaultFiles.map((file, fileIdx) => (
                          <div key={fileIdx} className="vault-file-item">
                            <span className={`vault-file-status ${file.processed ? 'processed' : 'pending'}`}>
                            </span>
                            <span className="vault-file-name">{file.filename}</span>
                            <span className="vault-file-size">
                              {file.file_size > 0 ? `(${(file.file_size / (1024 * 1024)).toFixed(2)} MB)` : ''}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="message-citations">
                      <div className="citations-title">Sources:</div>
                      {msg.citations.map((citation, citIdx) => (
                        <div key={citIdx} className="citation-link">
                          [{citation.id}] {citation.source}
                          {citation.page && `, Page ${citation.page}`}
                        </div>
                      ))}
                    </div>
                  )}
                  {msg.pdfGenerated && msg.pdfUrl && (
                    <div className="message-pdf">
                      <a
                        href={downloadPdf(msg.pdfUrl.split('/').pop())}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="pdf-download-link"
                      >
                        Download PDF
                      </a>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && messages[messages.length - 1]?.role !== 'assistant' && (
              <div className="chatgpt-message assistant">
                <div className="message-avatar">
                  <div className="avatar-assistant">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                    </svg>
                  </div>
                </div>
                <div className="message-wrapper">
                  <div className="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="chatgpt-input-area">
        <div className="input-wrapper">
          <div className="input-controls">
            <button
              className={`control-btn ${useRag ? 'active' : ''}`}
              onClick={() => setUseRag(!useRag)}
              title="Toggle Document Mode"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
                <polyline points="10 9 9 9 8 9"/>
              </svg>
            </button>
            <button
              className={`control-btn ${generatePdf ? 'active' : ''}`}
              onClick={() => setGeneratePdf(!generatePdf)}
              title="Generate PDF"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
            </button>
          </div>
          <div className="input-container">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => {
                setInput(e.target.value);
                // Auto-resize
                e.target.style.height = 'auto';
                e.target.style.height = `${Math.min(e.target.scrollHeight, 200)}px`;
              }}
              onKeyPress={handleKeyPress}
              placeholder={isReady 
                ? "Message FounderGPT..." 
                : "Upload a document first to start chatting"}
              disabled={!isReady || loading}
              className="chatgpt-input"
              rows="1"
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || loading || !isReady}
              className="send-btn"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            </button>
          </div>
          <div className="input-footer">
            <span className="footer-text">FounderGPT can make mistakes. Check important info.</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
