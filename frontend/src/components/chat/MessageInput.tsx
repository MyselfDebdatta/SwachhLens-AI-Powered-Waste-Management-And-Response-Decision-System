import React, { useState } from 'react';
import { Box, TextField, IconButton, CircularProgress } from '@mui/material';
import { Send } from 'lucide-react';

interface MessageInputProps {
  onSendMessage: (text: string) => void;
  disabled?: boolean;
}

export const MessageInput: React.FC<MessageInputProps> = ({ onSendMessage, disabled = false }) => {
  const [text, setText] = useState('');

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const trimmed = text.trim();
    if (trimmed && !disabled) {
      onSendMessage(trimmed);
      setText('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{
        p: 1.5,
        background: 'rgba(15, 23, 42, 0.95)',
        borderTop: '1px solid rgba(255, 255, 255, 0.08)',
        display: 'flex',
        alignItems: 'center',
        gap: 1,
      }}
    >
      <TextField
        fullWidth
        size="small"
        placeholder="Type a message..."
        value={text}
        disabled={disabled}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        variant="outlined"
        sx={{
          '& .MuiOutlinedInput-root': {
            borderRadius: 3,
            color: '#f8fafc',
            backgroundColor: 'rgba(30, 41, 59, 0.6)',
            fontSize: '0.875rem',
            '& fieldset': {
              borderColor: 'rgba(255, 255, 255, 0.15)',
            },
            '&:hover fieldset': {
              borderColor: 'rgba(6, 182, 212, 0.5)',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#06b6d4',
            },
          },
          '& .MuiInputBase-input::placeholder': {
            color: '#94a3b8',
            opacity: 1,
          },
        }}
      />

      <IconButton
        type="submit"
        disabled={disabled || !text.trim()}
        aria-label="Send Message"
        sx={{
          background: text.trim() && !disabled
            ? 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)'
            : 'rgba(255, 255, 255, 0.08)',
          color: text.trim() && !disabled ? '#ffffff' : '#64748b',
          borderRadius: 2.5,
          p: 1,
          '&:hover': {
            background: text.trim() && !disabled
              ? 'linear-gradient(135deg, #0891b2 0%, #2563eb 100%)'
              : 'rgba(255, 255, 255, 0.12)',
          },
          transition: 'all 0.2s ease',
        }}
      >
        {disabled ? (
          <CircularProgress size={18} sx={{ color: '#38bdf8' }} />
        ) : (
          <Send size={18} />
        )}
      </IconButton>
    </Box>
  );
};

export default MessageInput;
