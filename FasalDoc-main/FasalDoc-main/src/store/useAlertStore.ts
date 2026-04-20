import { create } from 'zustand';

export type AlertType = 'danger' | 'warning' | 'info';

export interface Alert {
  id: string;
  type: AlertType;
  title: string;
  body: string;
  cropName: string;
  region: string;
  timestamp: string;
  read: boolean;
}

interface AlertState {
  alerts: Alert[];
  unreadCount: number;
  region: string;
  setAlerts: (alerts: Alert[]) => void;
  markRead: (id: string) => void;
  markAllRead: () => void;
  setRegion: (region: string) => void;
}

export const useAlertStore = create<AlertState>((set) => ({
  alerts: [],
  unreadCount: 0,
  region: 'punjab',

  setAlerts: (alerts: Alert[]) =>
    set({
      alerts,
      unreadCount: alerts.filter((a) => !a.read).length,
    }),

  markRead: (id: string) =>
    set((state) => {
      const updated = state.alerts.map((a) => (a.id === id ? { ...a, read: true } : a));
      return {
        alerts: updated,
        unreadCount: updated.filter((a) => !a.read).length,
      };
    }),

  markAllRead: () =>
    set((state) => ({
      alerts: state.alerts.map((a) => ({ ...a, read: true })),
      unreadCount: 0,
    })),

  setRegion: (region: string) => set({ region }),
}));
