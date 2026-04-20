import React from 'react';
import { Text, useColorScheme } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import ScanScreen from '../screens/ScanScreen';
import ResultScreen from '../screens/ResultScreen';
import HistoryScreen from '../screens/HistoryScreen';
import AlertsScreen from '../screens/AlertsScreen';
import TreatmentScreen from '../screens/TreatmentScreen';
import SettingsScreen from '../screens/SettingsScreen';

import { useAlertStore } from '../store/useAlertStore';
import { getColors } from '../constants/colors';

export type RootStackParamList = {
  MainTabs: undefined;
  Result: {
    diseaseName: string;
    confidence: number;
    cropName: string;
    stage: string;
    imageUri: string;
    scanDate: string;
    treatmentId: string;
    description?: string;
    severity?: 'low' | 'medium' | 'high';
    scanId: string;
  };
  TreatmentDetail: {
    treatmentId: string;
    diseaseName: string;
    cropName: string;
    stage: string;
  };
};

export type TabParamList = {
  Scan: undefined;
  History: undefined;
  Alerts: undefined;
  Treatment: undefined;
  Settings: undefined;
};

const Tab = createBottomTabNavigator<TabParamList>();
const Stack = createNativeStackNavigator<RootStackParamList>();

const TabIcon = ({
  emoji,
  focused,
}: {
  emoji: string;
  focused: boolean;
}) => (
  <Text style={{ fontSize: focused ? 22 : 20, opacity: focused ? 1 : 0.6 }}>{emoji}</Text>
);

const MainTabs: React.FC = () => {
  const scheme = useColorScheme();
  const C = getColors(scheme);
  const unreadCount = useAlertStore((s) => s.unreadCount);

  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          backgroundColor: C.CARD_BG,
          borderTopWidth: 0.5,
          borderTopColor: C.BORDER,
          height: 60,
          paddingBottom: 8,
          paddingTop: 4,
        },
        tabBarActiveTintColor: C.PRIMARY_GREEN,
        tabBarInactiveTintColor: C.TEXT_TERTIARY,
        tabBarLabelStyle: {
          fontSize: 11,
          fontWeight: '500',
        },
      }}
    >
      <Tab.Screen
        name="Scan"
        component={ScanScreen}
        options={{
          tabBarLabel: 'Scan',
          tabBarIcon: ({ focused }) => (
            <TabIcon emoji="📷" focused={focused} />
          ),
        }}
      />
      <Tab.Screen
        name="History"
        component={HistoryScreen}
        options={{
          tabBarLabel: 'History',
          tabBarIcon: ({ focused }) => (
            <TabIcon emoji="📋" focused={focused} />
          ),
        }}
      />
      <Tab.Screen
        name="Alerts"
        component={AlertsScreen}
        options={{
          tabBarLabel: 'Alerts',
          tabBarIcon: ({ focused }) => (
            <TabIcon emoji="🔔" focused={focused} />
          ),
          tabBarBadge: unreadCount > 0 ? unreadCount : undefined,
          tabBarBadgeStyle: {
            backgroundColor: C.RED,
            fontSize: 10,
          },
        }}
      />
      <Tab.Screen
        name="Treatment"
        component={TreatmentScreen}
        options={{
          tabBarLabel: 'Treatment',
          tabBarIcon: ({ focused }) => (
            <TabIcon emoji="🌱" focused={focused} />
          ),
        }}
      />
      <Tab.Screen
        name="Settings"
        component={SettingsScreen}
        options={{
          tabBarLabel: 'Settings',
          tabBarIcon: ({ focused }) => (
            <TabIcon emoji="⚙️" focused={focused} />
          ),
        }}
      />
    </Tab.Navigator>
  );
};

const AppNavigator: React.FC = () => {
  const scheme = useColorScheme();
  const C = getColors(scheme);

  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerShown: false,
          contentStyle: { backgroundColor: C.GRAY_BG },
        }}
      >
        <Stack.Screen name="MainTabs" component={MainTabs} />
        <Stack.Screen
          name="Result"
          component={ResultScreen}
          options={{ animation: 'slide_from_bottom' }}
        />
        <Stack.Screen
          name="TreatmentDetail"
          component={TreatmentScreen}
          options={{ animation: 'slide_from_right' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default AppNavigator;
