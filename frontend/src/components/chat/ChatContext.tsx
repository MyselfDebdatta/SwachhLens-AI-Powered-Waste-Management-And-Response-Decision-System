import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { ChatReplyResponse } from '../../types/chat';
import { createChatSession, sendChatMessage } from '../../services/chatService';

export interface ChatContextValue {
  sessionId: string | null;
  messages: ChatReplyResponse[];
  loading: boolean;
  sending: boolean;
  error: string | null;
  userId: string;
  quickPrompts: string[];
  sendMessage: (text: string) => Promise<void>;
  clearError: () => void;
  resetSession: () => Promise<void>;
}

const DEFAULT_QUICK_PROMPTS = [
  'Show bins above 80%',
  'What is today route summary?',
  'Check maintenance logs',
];

const ChatContext = createContext<ChatContextValue | undefined>(undefined);

export interface ChatProviderProps {
  userId: string;
  quickPrompts?: string[];
  children: ReactNode;
}

export const ChatProvider: React.FC<ChatProviderProps> = ({
  userId,
  quickPrompts = DEFAULT_QUICK_PROMPTS,
  children,
}) => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatReplyResponse[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [sending, setSending] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const initSession = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const sessionRes = await createChatSession(userId, { source: 'ChatProvider' });
      setSessionId(sessionRes.session_id);
      setMessages([
        {
          session_id: sessionRes.session_id,
          role: 'assistant',
          user_id: 'system',
          message: 'Hello! I am SwachhLens AI Assistant. How can I help you today?',
          context: {},
        },
      ]);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to establish chat session';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  // Initialize session once on mount or when userId changes
  useEffect(() => {
    if (!sessionId) {
      initSession();
    }
  }, [userId, sessionId, initSession]);

  const sendMessage = useCallback(
    async (text: string) => {
      if (!sessionId || sending) return;

      setError(null);
      const userMsg: ChatReplyResponse = {
        session_id: sessionId,
        role: 'user',
        user_id: userId,
        message: text,
        context: {},
      };

      setMessages(prev => [...prev, userMsg]);
      setSending(true);

      try {
        const replyRes = await sendChatMessage(sessionId, userId, text, { source: 'ChatProvider' });
        setMessages(prev => [...prev, replyRes]);
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Failed to send message';
        setError(msg);
      } finally {
        setSending(false);
      }
    },
    [sessionId, sending, userId]
  );

  const clearError = useCallback(() => setError(null), []);

  const resetSession = useCallback(async () => {
    setSessionId(null);
    setMessages([]);
    await initSession();
  }, [initSession]);

  const value: ChatContextValue = {
    sessionId,
    messages,
    loading,
    sending,
    error,
    userId,
    quickPrompts,
    sendMessage,
    clearError,
    resetSession,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};

export const useChat = (): ChatContextValue => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};
