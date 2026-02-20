import { create } from 'zustand';

interface ChatMessage {
  role: 'user' | 'coach' | 'system';
  content: string;
  timestamp: number;
}

interface CoachState {
  sessionId: string | null;
  styleId: string | null;
  messages: ChatMessage[];
  isActive: boolean;
  isLoading: boolean;
  halted: boolean;

  setSession: (sessionId: string, styleId: string) => void;
  addMessage: (role: ChatMessage['role'], content: string) => number;
  updateMessage: (index: number, content: string) => void;
  setLoading: (loading: boolean) => void;
  setHalted: (halted: boolean) => void;
  endSession: () => void;
  reset: () => void;
}

export const useCoachStore = create<CoachState>((set, get) => ({
  sessionId: null,
  styleId: null,
  messages: [],
  isActive: false,
  isLoading: false,
  halted: false,

  setSession: (sessionId, styleId) =>
    set({ sessionId, styleId, isActive: true, halted: false, messages: [] }),

  addMessage: (role, content) => {
    const index = get().messages.length;
    set((state) => ({
      messages: [...state.messages, { role, content, timestamp: Date.now() }],
    }));
    return index;
  },

  updateMessage: (index, content) =>
    set((state) => ({
      messages: state.messages.map((message, idx) =>
        idx === index ? { ...message, content } : message,
      ),
    })),

  setLoading: (isLoading) => set({ isLoading }),
  setHalted: (halted) => set({ halted, isActive: !halted }),

  endSession: () =>
    set({ isActive: false, sessionId: null }),

  reset: () =>
    set({
      sessionId: null,
      styleId: null,
      messages: [],
      isActive: false,
      isLoading: false,
      halted: false,
    }),
}));
