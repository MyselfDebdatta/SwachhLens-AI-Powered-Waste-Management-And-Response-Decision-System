import React from 'react';
import { Box, Typography, Avatar } from '@mui/material';
import { Bot, User } from 'lucide-react';
import { ChatReplyResponse } from '../../types/chat';

interface MessageBubbleProps {
  message: ChatReplyResponse;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isAssistant = message.role === 'assistant';

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: isAssistant ? 'row' : 'row-reverse',
        alignItems: 'flex-start',
        gap: 1.25,
        mb: 2,
      }}
    >
      {/* Role Avatar */}
      <Avatar
        sx={{
          width: 32,
          height: 32,
          background: isAssistant
            ? 'linear-gradient(135deg, #06b6d4, #8b5cf6)'
            : 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
        }}
      >
        {isAssistant ? <Bot size={18} style={{ color: '#fff' }} /> : <User size={18} style={{ color: '#fff' }} />}
      </Avatar>

      {/* Bubble Content */}
      <Box
        sx={{
          maxWidth: '78%',
          p: 1.5,
          borderRadius: 2.5,
          borderTopLeftRadius: isAssistant ? 0 : 2.5,
          borderTopRightRadius: isAssistant ? 2.5 : 0,
          background: isAssistant
            ? 'rgba(30, 41, 59, 0.85)'
            : 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
          backdropFilter: 'blur(10px)',
          border: '1px solid',
          borderColor: isAssistant ? 'rgba(255, 255, 255, 0.1)' : 'rgba(56, 189, 248, 0.3)',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.25)',
        }}
      >
        <Typography
          variant="body2"
          sx={{
            color: '#f8fafc',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
            fontSize: '0.875rem',
            lineHeight: 1.5,
          }}
        >
          {message.message}
        </Typography>

        <Typography
          variant="caption"
          sx={{
            display: 'block',
            mt: 0.5,
            textAlign: isAssistant ? 'left' : 'right',
            color: isAssistant ? '#94a3b8' : '#bae6fd',
            fontSize: '0.7rem',
          }}
        >
          {isAssistant ? 'SwachhLens AI' : message.user_id}
        </Typography>
      </Box>
    </Box>
  );
};

export default MessageBubble;
