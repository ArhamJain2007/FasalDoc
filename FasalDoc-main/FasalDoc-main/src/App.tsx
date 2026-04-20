import React, { useEffect, useState } from 'react';
import { View, ActivityIndicator, useColorScheme } from 'react-native';
import { initI18n } from './i18n';
import { initDB, getUnsyncedScans, markSynced } from './services/offlineDB';
import { setupNotifications } from './services/notifications';
import AppNavigator from './navigation/AppNavigator';
import { getColors } from './constants/colors';
import NetInfo from '@react-native-community/netinfo';
import { syncHistory } from './services/api';

const App: React.FC = () => {
  const scheme = useColorScheme();
  const C = getColors(scheme);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    let unsubscribe: (() => void) | undefined;

    const bootstrap = async () => {
      try {
        // ✅ Init i18n
        await initI18n();

        // ✅ Init SQLite (new sync API)
        initDB();

        // ✅ Setup notifications
        await setupNotifications();

        // ✅ Network sync listener — sync unsynced records when online
        unsubscribe = NetInfo.addEventListener(async (state) => {
          if (state.isConnected) {
            try {
              const unsynced = getUnsyncedScans();
              if (unsynced.length > 0) {
                await syncHistory(unsynced);
                unsynced.forEach((r) => markSynced(r.id));
                console.log(`✅ Synced ${unsynced.length} records`);
              }
            } catch {
              // silent fail — will retry on next connection
            }
          }
        });

        setIsReady(true);
      } catch (err) {
        console.error('[App] Bootstrap failed:', err);
        setIsReady(true); // still show app even if bootstrap partially fails
      }
    };

    bootstrap();

    return () => {
      unsubscribe?.();
    };
  }, []);

  if (!isReady) {
    return (
      <View
        style={{
          flex: 1,
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: C.GRAY_BG,
        }}
      >
        <ActivityIndicator size="large" color={C.PRIMARY_GREEN} />
      </View>
    );
  }

  return <AppNavigator />;
};

export default App;
