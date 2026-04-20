import React, { useEffect, useState } from 'react';
import { View, ActivityIndicator, useColorScheme } from 'react-native';
import { initI18n } from './i18n';
import { initDB } from './services/offlineDB'; // ✅ updated
import { loadModel } from './services/tflite';
import { setupNotifications } from './services/notifications';
import AppNavigator from './navigation/AppNavigator';
import { getColors } from './constants/colors';
import NetInfo from '@react-native-community/netinfo';
import { getAllScans } from './services/offlineDB'; // ⚠️ placeholder if needed
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

        // ✅ Init SQLite (sync function, no await needed)
        initDB();

        // ✅ Load TFLite model (non-blocking)
        loadModel().catch((e) =>
          console.warn('[App] Model load failed:', e)
        );

        // ✅ Setup notifications
        await setupNotifications();

        // ✅ Network sync listener
        unsubscribe = NetInfo.addEventListener(async (state) => {
          if (state.isConnected) {
            try {
              // ⚠️ TEMP: replace with your actual unsynced logic
              // (since we removed old DB functions)
              getAllScans(async (records) => {
                if (records.length > 0) {
                  try {
                    await syncHistory(records);
                    console.log('✅ Synced data');
                  } catch {
                    console.log('❌ Sync failed');
                  }
                }
              });
            } catch {
              // silent fail
            }
          }
        });

        setIsReady(true);
      } catch (err) {
        console.error('[App] Bootstrap failed:', err);
        setIsReady(true);
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