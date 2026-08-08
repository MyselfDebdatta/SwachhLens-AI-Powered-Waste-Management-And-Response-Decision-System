export interface SessionCreatePayload {
  user_id: string;
  context?: Record<string, unknown>;
}

export interface SessionCreateResponse {
  session_id: string;
  user_id: string;
}

export interface ChatMessagePayload {
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  user_id: string;
  message: string;
  context?: Record<string, unknown>;
}

export interface ChatReplyResponse {
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  user_id: string;
  message: string;
  context?: Record<string, unknown>;
}

export interface ChatPingResponse {
  status: string;
}
