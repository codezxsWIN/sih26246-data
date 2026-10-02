import React, { useState, useRef, useEffect } from 'react';
import { api } from '../apiClient';
import { Send, Bot, User } from 'lucide-react';
import { motion } from 'framer-motion';

const Copilot = () => {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello. I am the AI Policy Copilot. How can I assist you with labour market intelligence today?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userQuery = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userQuery }]);
    setLoading(true);

    try {
      const res = await api.askCopilot(userQuery);
      setMessages(prev => [...prev, { role: 'assistant', content: res.result }]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { role: 'assistant', content: "I'm sorry, I encountered an error connecting to the intelligence backend." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={{ height: 'calc(100vh - 4rem)', display: 'flex', flexDirection: 'column' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>AI Policy Copilot</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Ask natural-language questions about the labour market and policy recommendations.</p>
      </div>

      <div className="glass-panel" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <div style={{ flex: 1, overflowY: 'auto', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {messages.map((msg, idx) => (
            <motion.div 
              key={idx}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              style={{
                display: 'flex',
                gap: '1rem',
                alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '80%'
              }}
            >
              {msg.role === 'assistant' && (
                <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'linear-gradient(135deg, var(--color-demand), var(--color-policy))', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Bot size={20} color="white" />
                </div>
              )}
              
              <div style={{
                background: msg.role === 'user' ? 'var(--color-demand)' : 'rgba(255,255,255,0.05)',
                padding: '1rem 1.5rem',
                borderRadius: msg.role === 'user' ? '1.5rem 1.5rem 0 1.5rem' : '1.5rem 1.5rem 1.5rem 0',
                border: msg.role === 'assistant' ? '1px solid rgba(255,255,255,0.1)' : 'none',
                color: 'white',
                lineHeight: '1.5',
                whiteSpace: 'pre-wrap'
              }}>
                {msg.content}
              </div>

              {msg.role === 'user' && (
                <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'rgba(255,255,255,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <User size={20} color="white" />
                </div>
              )}
            </motion.div>
          ))}
          {loading && (
            <div style={{ display: 'flex', gap: '1rem', alignSelf: 'flex-start' }}>
              <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'linear-gradient(135deg, var(--color-demand), var(--color-policy))', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Bot size={20} color="white" />
              </div>
              <div style={{ padding: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span className="spinner" style={{ width: '20px', height: '20px', borderWidth: '2px' }}></span>
                <span style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Analyzing data...</span>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        <div style={{ paddingTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.1)', display: 'flex', gap: '1rem' }}>
          <textarea 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="E.g., Which sectors have the most critical shortage right now?"
            style={{
              flex: 1,
              background: 'rgba(0,0,0,0.2)',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: 'var(--radius-lg)',
              padding: '1rem',
              color: 'white',
              outline: 'none',
              resize: 'none',
              height: '56px',
              fontFamily: 'inherit'
            }}
          />
          <button 
            className="btn btn-primary"
            onClick={handleSend}
            disabled={!input.trim() || loading}
            style={{ width: '56px', height: '56px', padding: '0', borderRadius: 'var(--radius-lg)' }}
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default Copilot;
