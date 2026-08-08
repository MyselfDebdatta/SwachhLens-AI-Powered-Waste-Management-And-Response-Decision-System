import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Fab,
  Paper,
  Typography,
  IconButton,
  Badge,
  Tooltip,
  Fade
} from '@mui/material';
import { Bot, X, Sparkles } from 'lucide-react';
import { ChatProvider } from './ChatContext';
import ChatWindow from './ChatWindow';
import './ChatWidget.css';

interface ChatWidgetContentProps {}

const ChatWidgetContent: React.FC<ChatWidgetContentProps> = () => {
  const [isOpen, setIsOpen] = useState(false);
  const widgetRef = useRef<HTMLDivElement>(null);

  const toggleChat = () => setIsOpen(prev => !prev);
  const handleClose = () => setIsOpen(false);

  // Keyboard accessibility: Close on Escape key press with clean listener teardown
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen) {
        handleClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen]);

  return (
    <Box
      ref={widgetRef}
      className="swachhlens-chat-widget-root"
      sx={{
        position: 'fixed',
        bottom: 24,
        right: 24,
        zIndex: 1400, // Elevated z-index above Leaflet maps (z-1000) and standard MUI headers (z-1100)
      }}
    >
      {/* Floating Action Button (MUI Fab) */}
      <Tooltip title={isOpen ? 'Close AI Assistant (Esc)' : 'Open SwachhLens AI Assistant'} placement="left">
        <Fab
          color="primary"
          onClick={toggleChat}
          aria-label={isOpen ? 'Close SwachhLens AI Assistant' : 'Open SwachhLens AI Assistant'}
          sx={{
            width: 56,
            height: 56,
            background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 50%, #8b5cf6 100%)',
            boxShadow: '0 8px 24px rgba(6, 182, 212, 0.4)',
            '&:hover': {
              background: 'linear-gradient(135deg, #0891b2 0%, #2563eb 50%, #7c3aed 100%)',
              transform: 'scale(1.06)',
            },
            transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
          }}
        >
          <Badge
            color="success"
            variant="dot"
            invisible={isOpen}
            anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
          >
            {isOpen ? <X size={24} style={{ color: '#ffffff' }} /> : <Bot size={26} style={{ color: '#ffffff' }} />}
          </Badge>
        </Fab>
      </Tooltip>

      {/* Floating Overlay Window (MUI Paper) */}
      <Fade in={isOpen} unmountOnExit timeout={250}>
        <Paper
          elevation={16}
          role="dialog"
          aria-label="SwachhLens AI Assistant Window"
          aria-modal="false"
          sx={{
            position: 'absolute',
            bottom: 72,
            right: 0,
            width: 380,
            height: 540,
            maxWidth: 'calc(100vw - 32px)',
            maxHeight: 'calc(100vh - 120px)',
            background: 'rgba(15, 23, 42, 0.94)',
            backdropFilter: 'blur(20px)',
            WebkitBackdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.12)',
            borderRadius: 3,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            boxShadow: '0 20px 50px rgba(0, 0, 0, 0.6), 0 0 30px rgba(6, 182, 212, 0.15)',
          }}
        >
          {/* Header */}
          <Box
            sx={{
              p: 2,
              background: 'rgba(30, 41, 59, 0.8)',
              borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <Box
                sx={{
                  width: 36,
                  height: 36,
                  borderRadius: 2,
                  background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(139, 92, 246, 0.2))',
                  border: '1px solid rgba(6, 182, 212, 0.4)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#38bdf8',
                }}
              >
                <Bot size={20} />
              </Box>
              <Box>
                <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#f8fafc', lineHeight: 1.2 }}>
                  SwachhLens AI
                </Typography>
                <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: '#38bdf8' }}>
                  <Sparkles size={12} className="swachhlens-sparkle-icon" /> Online Assistant
                </Typography>
              </Box>
            </Box>

            <IconButton
              size="small"
              onClick={handleClose}
              aria-label="Close Chat Window (Esc)"
              sx={{
                color: '#94a3b8',
                '&:hover': { color: '#f8fafc', background: 'rgba(255, 255, 255, 0.1)' },
              }}
            >
              <X size={18} />
            </IconButton>
          </Box>

          {/* Purely Presentational Body Container */}
          <ChatWindow />
        </Paper>
      </Fade>
    </Box>
  );
};

export interface ChatWidgetProps {
  userId?: string;
  quickPrompts?: string[];
}

export const ChatWidget: React.FC<ChatWidgetProps> = ({ userId = 'operator_1', quickPrompts }) => {
  return (
    <ChatProvider userId={userId} quickPrompts={quickPrompts}>
      <ChatWidgetContent />
    </ChatProvider>
  );
};

export default ChatWidget;
