import React from 'react';
import { useColorScheme, Text } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { useAlertStore } from '../store/useAlertStore';
import { getColors } from '../constants/colors';
import type { DetectResult } from '../services/api';

import ScanScreen      from '../screens/ScanScreen';
import ResultScreen    from '../screens/ResultScreen';
import HistoryScreen   from '../screens/HistoryScreen';
import AlertsScreen    from '../screens/AlertsScreen';
import TreatmentScreen from '../screens/TreatmentScreen';
import SettingsScreen  from '../screens/SettingsScreen';

// ─── Route param types ────────────────────────────────────────────────────────

export type RootStackParamList = {
  MainTabs: undefined;
  Result: { result: DetectResult; imageUri: string };
  Treatment: { treatmentId: string; diseaseName: string; cropName: string; stage: string };
};

export type TabParamList = {
  Scan:      undefined;
  History:   undefined;
  Alerts:    undefined;
  Treatment: undefined;
  Settings:  undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();
const Tab   = createBottomTabNavigator<TabParamList>();

// ─── Tab icon helper ──────────────────────────────────────────────────────────

const TAB_ICONS: Record<keyof TabParamList, string> = {
  Scan:      '📷',
  History:   '📋',
  Alerts:    '🔔',
  Treatment: '💊',
  Settings:  '⚙️',
};

const TAB_LABELS: Record<keyof TabParamList, string> = {
  Scan:      'Scan',
  History:   'History',
  Alerts:    'Alerts',
  Treatment: 'Treatment',
  Settings:  'Settings',
};

// ─── Bottom tab navigator ─────────────────────────────────────────────────────

const MainTabs: React.FC = () => {
  const scheme = useColorScheme();
  const C = getColors(scheme);
  const { unreadCount } = useAlertStore();

  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused }) => (
          <Text style={{ fontSize: focused ? 20 : 18 }}>
            {TAB_ICONS[route.name as keyof TabParamList]}
          </Text>
        ),
        tabBarLabel: TAB_LABELS[route.name as keyof TabParamList],
        tabBarActiveTintColor:   C.PRIMARY_GREEN,
        tabBarInactiveTintColor: C.TEXT_TERTIARY,
        tabBarStyle: {
          backgroundColor:  C.CARD_BG,
          borderTopWidth:   0.5,
          borderTopColor:   C.BORDER,
          height:           60,
          paddingBottom:    8,
        },
        tabBarLabelStyle: { fontSize: 11, fontWeight: '500' },
        headerShown: false,
      })}
    >
      <Tab.Screen name="Scan"      component={ScanScreen} />
      <Tab.Screen name="History"   component={HistoryScreen} />
      <Tab.Screen
        name="Alerts"
        component={AlertsScreen}
        options={{
          tabBarBadge: unreadCount > 0 ? unreadCount : undefined,
          tabBarBadgeStyle: { backgroundColor: C.RED, fontSize: 10 },
        }}
      />
      <Tab.Screen name="Treatment" component={TreatmentScreen}
        listeners={({ navigation }) => ({
          tabPress: (e) => {
            // Treatment tab on its own has no params — prevent crash
            e.preventDefault();
          },
        })}
        options={{ tabBarButton: () => null }}  // Hide — only accessible from Result
      />
      <Tab.Screen name="Settings"  component={SettingsScreen} />
    </Tab.Navigator>
  );
};

// ─── Root stack navigator ─────────────────────────────────────────────────────

const AppNavigator: React.FC = () => {
  const scheme = useColorScheme();
  const C = getColors(scheme);

  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerStyle:      { backgroundColor: C.CARD_BG },
          headerTintColor:  C.TEXT_PRIMARY,
          headerTitleStyle: { fontWeight: '500', fontSize: 16 },
          headerShadowVisible: false,
          contentStyle:     { backgroundColor: C.GRAY_BG },
        }}
      >
        <Stack.Screen name="MainTabs"  component={MainTabs}  options={{ headerShown: false }} />
        <Stack.Screen name="Result"    component={ResultScreen}
          options={{ title: 'Scan Result', headerBackTitle: 'Back' }} />
        <Stack.Screen name="Treatment" component={TreatmentScreen}
          options={{ title: 'Treatment Plan', headerBackTitle: 'Back' }} />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default AppNavigator;
