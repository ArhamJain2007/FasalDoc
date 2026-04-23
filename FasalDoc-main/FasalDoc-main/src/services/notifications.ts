import { Platform, Alert } from 'react-native';
import * as Notifications from 'expo-notifications';
import { registerFCMToken } from './api';

type NavigationRef = {
  navigate: (screen: string) => void;
};

let navigationRef: NavigationRef | null = null;

export const setNavigationRef = (ref: NavigationRef): void => {
  navigationRef = ref;
};

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

export const requestNotificationPermission = async (): Promise<boolean> => {
  try {
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
    const token = await Notifications.getExpoPushTokenAsync();
    return token.data;
  } catch (err) {
    console.warn('[Notifications] Failed to get token:', err);
    return null;
  }
};

export const registerDeviceToken = async (): Promise<void> => {
  const token = await getFCMToken();
  if (token) {
    try {
      await registerFCMToken(token);
    } catch (err) {
      console.warn('[Notifications] Token registration failed:', err);
    }
  }
};

export const setupNotifications = async (): Promise<void> => {
  try {
    const hasPermission = await requestNotificationPermission();
    if (!hasPermission) {
      console.warn('[Notifications] Permission not granted');
      return;
    }

    await registerDeviceToken();

    // Handle foreground notifications
    Notifications.addNotificationReceivedListener((notification) => {
      const title = notification.request.content.title ?? 'FasalDoc Alert';
      const body = notification.request.content.body ?? '';
      Alert.alert(title, body, [
        { text: 'View Alerts', onPress: () => navigationRef?.navigate('Alerts') },
        { text: 'Dismiss', style: 'cancel' },
      ]);
    });

    // Handle notification tap
    Notifications.addNotificationResponseReceivedListener(() => {
      navigationRef?.navigate('Alerts');
    });
  } catch (err) {
    console.warn('[Notifications] Setup skipped:', err);
  }
};
