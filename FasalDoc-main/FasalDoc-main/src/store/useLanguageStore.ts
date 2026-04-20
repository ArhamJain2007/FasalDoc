import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import i18n, { SupportedLanguage, saveLanguage } from '../i18n';

interface LanguageState {
  language: SupportedLanguage;
  setLanguage: (lang: SupportedLanguage) => Promise<void>;
}

export const useLanguageStore = create<LanguageState>()(
  persist(
    (set) => ({
      language: 'en',
      setLanguage: async (lang: SupportedLanguage) => {
        set({ language: lang });
        await i18n.changeLanguage(lang);
        await saveLanguage(lang);
      },
    }),
    {
      name: 'language-store',
      storage: createJSONStorage(() => AsyncStorage),
    },
  ),
);
