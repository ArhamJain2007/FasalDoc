import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { clearToken } from '../services/api';

interface AuthState {
  isLoggedIn: boolean;
  userId: string | null;
  userName: string | null;
  userRegion: string | null;
  setAuth: (userId: string, name: string, region: string) => void;
  logout: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      isLoggedIn: false,
      userId: null,
      userName: null,
      userRegion: null,

      setAuth: (userId, name, region) =>
        set({ isLoggedIn: true, userId, userName: name, userRegion: region }),

      logout: async () => {
        await clearToken();
        set({ isLoggedIn: false, userId: null, userName: null, userRegion: null });
      },
    }),
    {
      name: 'auth-store',
      storage: createJSONStorage(() => AsyncStorage),
    },
  ),
);
