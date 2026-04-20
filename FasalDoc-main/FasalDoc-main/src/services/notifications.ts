import messaging, { FirebaseMessagingTypes } from '@react-native-firebase/messaging';
import { Platform, Alert } from 'react-native';
import { registerFCMToken } from './api';

type NavigationRef = {
  navigate: (screen: string) => void;
};

let navigationRef: NavigationRef | null = null;

export const setNavigationRef = (ref: NavigationRef): void => {
  navigationRef = ref;
};

export const requestNotificationPermission = async (): Promise<boolean> => {
  if (Platform.OS === 'ios') {
    const authStatus = await messaging().requestPermission();
    const enabled =
      authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
      authStatus === messaging.AuthorizationStatus.PROVISIONAL;
    return enabled;
  }
  // Android 13+ requires explicit permission
  if (Platform.OS === 'android' && Platform.Version >= 33) {
    const { PermissionsAndroid } = await import('react-native');
    const granted = await PermissionsAndroid.request(
      PermissionsAndroid.PERMISSIONS.POST_NOTIFICATIONS,
    );
    return granted === PermissionsAndroid.RESULTS.GRANTED;
  }
  return true;
};

export const getFCMToken = async (): Promise<string | null> => {
  try {
    const token = await messaging().getToken();
    return token;
  } catch (err) {
    console.error('[FCM] Failed to get token:', err);
    return null;
  }
};

export const registerDeviceToken = async (): Promise<void> => {
  const token = await getFCMToken();
  if (token) {
    try {
      await registerFCMToken(token);
      console.log('[FCM] Token registered');
    } catch (err) {
      console.warn('[FCM] Token registration failed:', err);
    }
  }
};

export const setupNotifications = async (): Promise<void> => {
  const hasPermission = await requestNotificationPermission();
  if (!hasPermission) {
    console.warn('[FCM] Notification permission not granted');
    return;
  }

  await registerDeviceToken();

  // Listen for token refresh
  messaging().onTokenRefresh(async (token) => {
    try {
      await registerFCMToken(token);
    } catch {
      // ignore
    }
  });

  // Handle foreground messages
  messaging().onMessage(async (remoteMessage: FirebaseMessagingTypes.RemoteMessage) => {
    const title = remoteMessage.notification?.title ?? 'FasalDoc Alert';
    const body = remoteMessage.notification?.body ?? '';

    Alert.alert(title, body, [
      {
        text: 'View Alerts',
        onPress: () => navigationRef?.navigate('Alerts'),
      },
      { text: 'Dismiss', style: 'cancel' },
    ]);
  });

  // Handle background/quit message tap
  messaging().onNotificationOpenedApp(() => {
    navigationRef?.navigate('Alerts');
  });

  // Handle quit state notification tap
  const initialMessage = await messaging().getInitialNotification();
  if (initialMessage) {
    setTimeout(() => {
      navigationRef?.navigate('Alerts');
    }, 1000);
  }
};
