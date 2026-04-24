import React, { useEffect, useState } from 'react';
import { View, ActivityIndicator, useColorScheme } from 'react-native';
import { initI18n } from './i18n';
import { initDB } from './services/offlineDB';
import { setupNotifications } from './services/notifications';
import { useAuthStore } from './store/useAuthStore';
import { getColors } from './constants/colors';
import AppNavigator from './navigation/AppNavigator';
import AuthScreen from './screens/AuthScreen';

const App: React.FC = () => {
  const scheme = useColorScheme();
  const C = getColors(scheme);
  const { isLoggedIn } = useAuthStore();
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const bootstrap = async () => {
      try {
        await initI18n();
        initDB();
        await setupNotifications();
      } catch (err) {
        console.warn('[App] Bootstrap error:', err);
      } finally {
        setIsReady(true);
      }
    };
    bootstrap();
  }, []);

  if (!isReady) {
    return (
      <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: C.GRAY_BG }}>
        <ActivityIndicator size="large" color={C.PRIMARY_GREEN} />
      </View>
    );
  }

  if (!isLoggedIn) {
    return <AuthScreen />;
  }

  return <AppNavigator />;
};

export default App;
