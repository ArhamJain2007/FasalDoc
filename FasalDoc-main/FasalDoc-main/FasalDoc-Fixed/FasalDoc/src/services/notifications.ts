import { Platform } from 'react-native';
import { registerFCMToken } from './api';

// Lazy-load expo-notifications to avoid crashes on unsupported environments
const getNotifications = () => require('expo-notifications');

export const requestNotificationPermission = async (): Promise<boolean> => {
  try {
    const Notifications = getNotifications();
    if (Platform.OS === 'android') {
      await Notifications.setNotificationChannelAsync('default', {
        name: 'default',
        importance: Notifications.AndroidImportance.MAX,
      });
    }
    const { status } = await Notifications.requestPermissionsAsync();
    return status === 'granted';
  } catch (err) {
    console.warn('[Notifications] Permission request failed:', err);
    return false;
  }
};

export const getFCMToken = async (): Promise<string | null> => {
  try {
    const Notifications = getNotifications();
    const token = await Notifications.getExpoPushTokenAsync();
    return token.data;
  } catch (err) {
    console.warn('[Notifications] Failed to get token:', err);
    return null;
  }
};

export const setupNotifications = async (): Promise<void> => {
  try {
    const Notifications = getNotifications();

    Notifications.setNotificationHandler({
      handleNotification: async () => ({
        shouldShowAlert: true,
        shouldPlaySound: true,
        shouldSetBadge: false,
      }),
    });

    const hasPermission = await requestNotificationPermission();
    if (!hasPermission) return;

    const token = await getFCMToken();
    if (token) {
      await registerFCMToken(token).catch(() => { /* non-fatal */ });
    }
  } catch (err) {
    console.warn('[Notifications] Setup skipped:', err);
  }
};
