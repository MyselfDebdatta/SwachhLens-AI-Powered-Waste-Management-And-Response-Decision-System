import {
  SessionCreatePayload,
  SessionCreateResponse,
  ChatMessagePayload,
  ChatReplyResponse,
  ChatPingResponse
} from '../types/chat';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

const CHAT_ENDPOINTS = {
  PING: '/api/chat/ping',
  SESSION: '/api/chat/session',
  MESSAGE: '/api/chat/message',
  HISTORY: (sessionId: string) => `/api/chat/history/${encodeURIComponent(sessionId)}`,
} as const;

/**
 * Generic request helper with consistent error handling and strict return types.
 */
async function request<T>(url: string, options?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${url}`, options);
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : 'Network failure';
    throw new Error(`Chat service network error: ${errorMsg}`);
  }

  if (!response.ok) {
    let errorDetail = response.statusText;
    try {
      const errJson = await response.json();
      if (errJson && typeof errJson.detail === 'string') {
        errorDetail = errJson.detail;
      }
    } catch {
      // JSON parsing failed, use statusText fallback
    }
    throw new Error(`Chat API error (${response.status}): ${errorDetail}`);
  }

  return response.json() as Promise<T>;
}

export async function pingChat(): Promise<ChatPingResponse> {
  return request<ChatPingResponse>(CHAT_ENDPOINTS.PING);
}

export async function createChatSession(
  userId: string,
  context: Record<string, unknown> = {}
): Promise<SessionCreateResponse> {
  const payload: SessionCreatePayload = { user_id: userId, context };
  return request<SessionCreateResponse>(CHAT_ENDPOINTS.SESSION, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
}

export async function sendChatMessage(
  sessionId: string,
  userId: string,
  message: string,
  context: Record<string, unknown> = {}
): Promise<ChatReplyResponse> {
  const payload: ChatMessagePayload = {
    session_id: sessionId,
    role: 'user',
    user_id: userId,
    message,
    context
  };
  return request<ChatReplyResponse>(CHAT_ENDPOINTS.MESSAGE, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
}

export async function fetchChatHistory(sessionId: string): Promise<ChatReplyResponse[]> {
  return request<ChatReplyResponse[]>(CHAT_ENDPOINTS.HISTORY(sessionId));
}
