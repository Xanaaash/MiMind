import { create } from 'zustand';

export type ToastType = 'success' | 'error' | 'warning';

export interface ToastItem {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
}

interface ToastState {
  toasts: ToastItem[];
  add: (type: ToastType, message: string, duration?: number) => void;
  dismiss: (id: string) => void;
}

let counter = 0;

export const useToastStore = create<ToastState>((set) => ({
  toasts: [],

  add: (type, message, duration = 3500) => {
    const id = `toast-${++counter}-${Date.now()}`;
    set((s) => ({ toasts: [...s.toasts, { id, type, message, duration }] }));

    if (duration > 0) {
      setTimeout(() => {
        set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) }));
      }, duration);
    }
  },

  dismiss: (id) => {
    set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) }));
  },
}));

export function toast(type: ToastType, message: string, duration?: number) {
  useToastStore.getState().add(type, message, duration);
}

toast.success = (msg: string, dur?: number) => toast('success', msg, dur);
toast.error = (msg: string, dur?: number) => toast('error', msg, dur);
toast.warning = (msg: string, dur?: number) => toast('warning', msg, dur);
