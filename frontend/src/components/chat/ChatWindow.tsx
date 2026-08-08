import React, { useEffect, useRef } from 'react';
import { Box, Typography, Chip, Alert, CircularProgress } from '@mui/material';
import { Sparkles } from 'lucide-react';
import { useChat } from './ChatContext';
import MessageBubble from './MessageBubble';
import MessageInput from './MessageInput';

export const ChatWindow: React.FC = () => {
  const {
    sessionId,
    messages,
    loading,
    sending,
    error,
    quickPrompts,
    sendMessage,
    clearError,
  } = useChat();

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, sending]);

  const handleSend = (text: string) => {
    sendMessage(text);
  };

  return (
    <Box
      sx={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        overflow: 'hidden',
        background: 'rgba(15, 23, 42, 0.7)',
      }}
    >
      {/* Error alert banner */}
      {error && (
        <Alert
          severity="error"
          onClose={clearError}
          sx={{
            m: 1,
            fontSize: '0.8rem',
            background: 'rgba(239, 68, 68, 0.15)',
            color: '#fca5a5',
            border: '1px solid rgba(239, 68, 68, 0.3)',
          }}
        >
          {error}
        </Alert>
      )}

      {/* Messages Scroll Area */}
      <Box
        sx={{
          flex: 1,
          overflowY: 'auto',
          p: 2,
          display: 'flex',
          flexDirection: 'column',
          '&::-webkit-scrollbar': { width: '6px' },
          '&::-webkit-scrollbar-track': { background: 'transparent' },
          '&::-webkit-scrollbar-thumb': { background: 'rgba(255, 255, 255, 0.15)', borderRadius: '3px' },
        }}
      >
        {loading ? (
          <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
            <CircularProgress size={28} sx={{ color: '#06b6d4' }} />
            <Typography variant="caption" sx={{ color: '#94a3b8' }}>
              Initializing session...
            </Typography>
          </Box>
        ) : (
          <>
            {messages.map((msg, index) => (
              <MessageBubble key={`${msg.session_id}-${index}`} message={msg} />
            ))}

            {sending && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: '#06b6d4', mb: 2 }}>
                <CircularProgress size={16} sx={{ color: '#06b6d4' }} />
                <Typography variant="caption" sx={{ color: '#94a3b8', fontStyle: 'italic' }}>
                  SwachhLens AI is thinking...
                </Typography>
              </Box>
            )}

            <div ref={messagesEndRef} />
          </>
        )}
      </Box>

      {/* Quick Prompts Container (Data-Driven from Context) */}
      {!loading && messages.length <= 2 && quickPrompts.length > 0 && (
        <Box sx={{ px: 1.5, pb: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          {quickPrompts.map((prompt, idx) => (
            <Chip
              key={idx}
              label={prompt}
              size="small"
              onClick={() => handleSend(prompt)}
              disabled={sending}
              icon={<Sparkles size={12} style={{ color: '#38bdf8' }} />}
              sx={{
                fontSize: '0.75rem',
                color: '#e2e8f0',
                background: 'rgba(30, 41, 59, 0.7)',
                border: '1px solid rgba(255, 255, 255, 0.12)',
                '&:hover': {
                  background: 'rgba(6, 182, 212, 0.2)',
                  borderColor: 'rgba(6, 182, 212, 0.5)',
                },
                cursor: 'pointer',
              }}
            />
          ))}
        </Box>
      )}

      {/* Input Footer */}
      <MessageInput onSendMessage={handleSend} disabled={loading || sending || !sessionId} />
    </Box>
  );
};

export default ChatWindow;
