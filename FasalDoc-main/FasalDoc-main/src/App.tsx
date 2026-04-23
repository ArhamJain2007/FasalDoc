import React, { useEffect, useState, Component, ReactNode } from 'react';
import { View, Text, ActivityIndicator, useColorScheme, StyleSheet } from 'react-native';
import { initI18n } from './i18n';
import { setupNotifications } from './services/notifications';
import AppNavigator from './navigation/AppNavigator';
import { getColors } from './constants/colors';
import * as Network from 'expo-network';
import { AppState, AppStateStatus } from 'react-native';
import { syncHistory } from './services/api';

// ─── Error Boundary ────────────────────────────────────────────────────────────
interface EBState { hasError: boolean; error: string }
class ErrorBoundary extends Component<{ children: ReactNode }, EBState> {
  state: EBState = { hasError: false, error: '' };
  static getDerivedStateFromError(e: Error): EBState {
    return { hasError: true, error: e.message };
  }
  render() {
    if (this.state.hasError) {
      return (
        <View style={eb.container}>
          <Text style={eb.title}>Something went wrong</Text>
          <Text style={eb.msg}>{this.state.error}</Text>
        </View>
      );
    }
    return this.props.children;
  }
}
const eb = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 24 },
  title: { fontSize: 18, fontWeight: '600', color: '#E24B4A', marginBottom: 12 },
  msg: { fontSize: 13, color: '#555', textAlign: 'center' },
});

// ─── App ───────────────────────────────────────────────────────────────────────
const AppInner: React.FC = () => {
  const scheme = useColorScheme();
  const C = getColors(scheme);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    let unsubscribe: (() => void) | undefined;

    const bootstrap = async () => {
      try {
        await initI18n();

        // Lazy-require DB so a missing native module doesn't crash at module load time
        try {
          const { initDB } = require('./services/offlineDB');
          initDB();
        } catch (dbErr) {
          console.warn('[App] DB init failed (memory-only mode):', dbErr);
        }

        await setupNotifications();

        const syncIfOnline = async () => {
          try {
            const state = await Network.getNetworkStateAsync();
            if (state.isConnected) {
              const { getUnsyncedScans, markSynced } = require('./services/offlineDB');
              const unsynced = getUnsyncedScans();
              if (unsynced.length > 0) {
                await syncHistory(unsynced);
                unsynced.forEach((r: { id: string }) => markSynced(r.id));
              }
            }
          } catch { /* silent */ }
        };
        syncIfOnline();
        const appStateSub = AppState.addEventListener('change', (next: AppStateStatus) => {
          if (next === 'active') syncIfOnline();
        });
        unsubscribe = () => appStateSub.remove();
      } catch (err) {
        console.error('[App] Bootstrap failed:', err);
      } finally {
        setIsReady(true);
      }
    };

    bootstrap();
    return () => unsubscribe?.();
  }, []);

  if (!isReady) {
    return (
      <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: C.GRAY_BG }}>
        <ActivityIndicator size="large" color={C.PRIMARY_GREEN} />
      </View>
    );
  }

  return <AppNavigator />;
};

const App: React.FC = () => (
  <ErrorBoundary>
    <AppInner />
  </ErrorBoundary>
);

export default App;
