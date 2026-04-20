import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  useColorScheme,
  ScrollView,
  SafeAreaView,
  RefreshControl,
} from 'react-native';
import { useTranslation } from 'react-i18next';
import { requestNotificationPermission } from '../services/notifications';
import { getAlerts } from '../services/api';
import { useAlertStore, Alert as AlertType } from '../store/useAlertStore';
import { getColors } from '../constants/colors';
import { BorderRadius, Fonts, Spacing } from '../constants/fonts';
import AlertBadge from '../components/AlertBadge';

const REGIONS = [
  { key: 'punjab', label: 'alerts.region.punjab' },
  { key: 'haryana', label: 'alerts.region.haryana' },
  { key: 'up', label: 'alerts.region.up' },
  { key: 'delhi', label: 'alerts.region.delhi' },
  { key: 'rajasthan', label: 'alerts.region.rajasthan' },
  { key: 'mp', label: 'alerts.region.mp' },
  { key: 'maharashtra', label: 'alerts.region.maharashtra' },
];

const AlertsScreen: React.FC = () => {
  const scheme = useColorScheme();
  const C = getColors(scheme);
  const { t } = useTranslation();
  const { alerts, region, setAlerts, setRegion, markRead } = useAlertStore();

  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    requestNotificationPermission();
    fetchAlerts(region);
  }, []);

  const fetchAlerts = useCallback(async (reg: string) => {
    setIsLoading(true);
    try {
      const data = await getAlerts(reg);
      setAlerts(data);
    } catch {
      // Use mock data when API unavailable
      setAlerts(MOCK_ALERTS);
    } finally {
      setIsLoading(false);
    }
  }, [setAlerts]);

  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    await fetchAlerts(region);
    setIsRefreshing(false);
  }, [region, fetchAlerts]);

  const handleRegionChange = useCallback(
    (reg: string) => {
      setRegion(reg);
      fetchAlerts(reg);
    },
    [setRegion, fetchAlerts],
  );

  const handleAlertPress = useCallback(
    (alert: AlertType) => {
      markRead(alert.id);
    },
    [markRead],
  );

  const renderAlert = useCallback(
    ({ item }: { item: AlertType }) => {
      const timestamp = new Date(item.timestamp).toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
      });

      return (
        <TouchableOpacity
          style={[
            styles.alertCard,
            {
              backgroundColor: item.read ? C.CARD_BG : C.LIGHT_GREEN,
              borderColor: C.BORDER,
            },
          ]}
          onPress={() => handleAlertPress(item)}
          activeOpacity={0.75}
        >
          <View style={styles.alertTop}>
            <AlertBadge type={item.type} />
            <Text style={[styles.timestamp, { color: C.TEXT_TERTIARY }]}>{timestamp}</Text>
          </View>
          <Text style={[styles.alertTitle, { color: C.TEXT_PRIMARY }]}>{item.title}</Text>
          <Text style={[styles.cropLabel, { color: C.TEXT_SECONDARY }]}>
            🌾 {item.cropName}
          </Text>
          <Text style={[styles.alertBody, { color: C.TEXT_SECONDARY }]}>{item.body}</Text>
        </TouchableOpacity>
      );
    },
    [C, handleAlertPress],
  );

  const keyExtractor = useCallback((item: AlertType) => item.id, []);

  const EmptyState = () => (
    <View style={styles.emptyState}>
      <Text style={styles.emptyEmoji}>🔔</Text>
      <Text style={[styles.emptyText, { color: C.TEXT_SECONDARY }]}>
        {t('alerts.noAlerts')}
      </Text>
    </View>
  );

  return (
    <SafeAreaView style={[styles.safeArea, { backgroundColor: C.GRAY_BG }]}>
      {/* Header */}
      <View
        style={[styles.header, { backgroundColor: C.CARD_BG, borderBottomColor: C.BORDER }]}
      >
        <Text style={[styles.title, { color: C.TEXT_PRIMARY }]}>{t('alerts.title')}</Text>
        <View style={[styles.locationPill, { backgroundColor: C.LIGHT_GREEN }]}>
          <View style={[styles.locationDot, { backgroundColor: C.PRIMARY_GREEN }]} />
          <Text style={[styles.locationText, { color: C.DARK_GREEN }]}>
            {t(`alerts.region.${region}`)}
          </Text>
        </View>
      </View>

      {/* Region filter */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={[styles.regionBar, { backgroundColor: C.CARD_BG, borderBottomColor: C.BORDER }]}
        contentContainerStyle={styles.regionContent}
      >
        {REGIONS.map((r) => {
          const isActive = region === r.key;
          return (
            <TouchableOpacity
              key={r.key}
              style={[
                styles.regionPill,
                {
                  backgroundColor: isActive ? C.PRIMARY_GREEN : C.GRAY_BG,
                  borderColor: isActive ? C.PRIMARY_GREEN : C.BORDER,
                },
              ]}
              onPress={() => handleRegionChange(r.key)}
              activeOpacity={0.7}
            >
              <Text
                style={[
                  styles.regionText,
                  { color: isActive ? C.WHITE : C.TEXT_SECONDARY },
                ]}
              >
                {t(r.label)}
              </Text>
            </TouchableOpacity>
          );
        })}
      </ScrollView>

      {/* Alerts list */}
      <FlatList
        data={alerts}
        keyExtractor={keyExtractor}
        renderItem={renderAlert}
        ListEmptyComponent={!isLoading ? <EmptyState /> : null}
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl
            refreshing={isRefreshing}
            onRefresh={handleRefresh}
            tintColor={C.PRIMARY_GREEN}
          />
        }
      />
    </SafeAreaView>
  );
};

const MOCK_ALERTS: AlertType[] = [
  {
    id: '1',
    type: 'danger',
    title: 'Yellow Rust outbreak risk',
    body: 'High humidity + mild temperatures this week create ideal conditions. Inspect lower leaves immediately.',
    cropName: 'Wheat',
    region: 'punjab',
    timestamp: new Date().toISOString(),
    read: false,
  },
  {
    id: '2',
    type: 'warning',
    title: 'Aphid pressure rising',
    body: 'Warm nights forecast for next 5 days. Scout field borders first.',
    cropName: 'Mustard, Chickpea',
    region: 'punjab',
    timestamp: new Date(Date.now() - 86400000).toISOString(),
    read: false,
  },
  {
    id: '3',
    type: 'info',
    title: 'Pre-harvest fungicide window',
    body: 'Optimal spray timing this week. See treatment guide for recommended options.',
    cropName: 'Wheat',
    region: 'punjab',
    timestamp: new Date(Date.now() - 172800000).toISOString(),
    read: true,
  },
];

const styles = StyleSheet.create({
  safeArea: { flex: 1 },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md,
    borderBottomWidth: 0.5,
  },
  title: {
    ...Fonts.heading,
  },
  locationPill: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: BorderRadius.pill,
  },
  locationDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
  },
  locationText: {
    ...Fonts.caption,
    fontWeight: '500',
  },
  regionBar: {
    maxHeight: 52,
    borderBottomWidth: 0.5,
  },
  regionContent: {
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.sm,
    gap: Spacing.sm,
    flexDirection: 'row',
    alignItems: 'center',
  },
  regionPill: {
    paddingHorizontal: 14,
    paddingVertical: 5,
    borderRadius: BorderRadius.pill,
    borderWidth: 0.5,
  },
  regionText: {
    ...Fonts.caption,
    fontWeight: '500',
  },
  listContent: {
    padding: Spacing.lg,
    gap: Spacing.md,
    flexGrow: 1,
  },
  alertCard: {
    borderRadius: BorderRadius.md,
    borderWidth: 0.5,
    padding: Spacing.md,
    gap: Spacing.xs,
    marginBottom: Spacing.md,
  },
  alertTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 2,
  },
  timestamp: {
    ...Fonts.caption,
  },
  alertTitle: {
    ...Fonts.subheading,
  },
  cropLabel: {
    ...Fonts.caption,
  },
  alertBody: {
    ...Fonts.body,
  },
  emptyState: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingTop: 80,
    gap: Spacing.md,
  },
  emptyEmoji: {
    fontSize: 56,
  },
  emptyText: {
    ...Fonts.body,
    textAlign: 'center',
  },
});

export default AlertsScreen;
