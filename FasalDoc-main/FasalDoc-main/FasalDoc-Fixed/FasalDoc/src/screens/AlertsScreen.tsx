import React, { useEffect, useCallback, useState } from 'react';
import {
  View, Text, StyleSheet, FlatList, ScrollView,
  TouchableOpacity, useColorScheme, RefreshControl,
} from 'react-native';
import { useTranslation } from 'react-i18next';
import { getAlerts } from '../services/api';
import { useAlertStore } from '../store/useAlertStore';
import { useLanguageStore } from '../store/useLanguageStore';
import { getColors } from '../constants/colors';
import { BorderRadius, Fonts, Spacing } from '../constants/fonts';
import AlertBadge from '../components/AlertBadge';

const REGIONS = [
  { key: 'punjab', label: 'Punjab' },
  { key: 'haryana', label: 'Haryana' },
  { key: 'up', label: 'UP' },
  { key: 'delhi', label: 'Delhi NCR' },
  { key: 'rajasthan', label: 'Rajasthan' },
  { key: 'mp', label: 'MP' },
  { key: 'maharashtra', label: 'Maharashtra' },
];

const AlertsScreen: React.FC = () => {
  const scheme = useColorScheme();
  const C = getColors(scheme);
  const { t } = useTranslation();
  const { language } = useLanguageStore();
  const { alerts, region, setAlerts, setRegion, markRead } = useAlertStore();
  const [isLoading, setIsLoading] = useState(false);

  const fetchAlerts = useCallback(async (reg: string) => {
    setIsLoading(true);
    try {
      const data = await getAlerts(reg, language);
      setAlerts(data);
    } catch (err) {
      console.warn('[Alerts] Fetch failed:', err);
      setAlerts([]);
    } finally {
      setIsLoading(false);
    }
  }, [language, setAlerts]);

  useEffect(() => { fetchAlerts(region); }, [region]);

  const handleRegionChange = (key: string) => {
    setRegion(key);
    fetchAlerts(key);
  };

  const formatTime = (ts: string) => {
    try {
      return new Date(ts).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
    } catch { return ts; }
  };

  return (
    <View style={[styles.flex, { backgroundColor: C.GRAY_BG }]}>
      {/* Header */}
      <View style={[styles.header, { backgroundColor: C.CARD_BG, borderBottomColor: C.BORDER }]}>
        <View style={styles.titleRow}>
          <Text style={[styles.title, { color: C.TEXT_PRIMARY }]}>{t('alerts.title')}</Text>
          <View style={[styles.locationPill, { backgroundColor: C.LIGHT_GREEN }]}>
            <Text style={[styles.locationText, { color: C.DARK_GREEN }]}>
              📍 {REGIONS.find((r) => r.key === region)?.label ?? region}
            </Text>
          </View>
        </View>

        {/* Region filter */}
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.regionScroll}>
          <View style={styles.regionRow}>
            {REGIONS.map((r) => (
              <TouchableOpacity
                key={r.key}
                onPress={() => handleRegionChange(r.key)}
                style={[
                  styles.regionPill,
                  {
                    backgroundColor: region === r.key ? C.PRIMARY_GREEN : C.GRAY_BG,
                    borderColor: region === r.key ? C.PRIMARY_GREEN : C.BORDER,
                  },
                ]}
              >
                <Text style={[styles.regionText, { color: region === r.key ? C.WHITE : C.TEXT_SECONDARY }]}>
                  {r.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </ScrollView>
      </View>

      {/* Alert list */}
      <FlatList
        data={alerts}
        keyExtractor={(item) => item.id}
        contentContainerStyle={[
          styles.listContent,
          alerts.length === 0 && styles.emptyContent,
        ]}
        refreshControl={
          <RefreshControl
            refreshing={isLoading}
            onRefresh={() => fetchAlerts(region)}
            tintColor={C.PRIMARY_GREEN}
            colors={[C.PRIMARY_GREEN]}
          />
        }
        renderItem={({ item }) => (
          <TouchableOpacity
            style={[
              styles.alertCard,
              {
                backgroundColor: item.read ? C.CARD_BG : C.LIGHT_GREEN,
                borderColor: C.BORDER,
              },
            ]}
            onPress={() => markRead(item.id)}
            activeOpacity={0.8}
          >
            <View style={styles.alertTop}>
              <AlertBadge type={item.type} />
              <Text style={[styles.alertTime, { color: C.TEXT_TERTIARY }]}>
                {formatTime(item.timestamp)}
              </Text>
            </View>
            <Text style={[styles.alertTitle, { color: C.TEXT_PRIMARY }]}>{item.title}</Text>
            <Text style={[styles.alertBody, { color: C.TEXT_SECONDARY }]}>{item.body}</Text>
          </TouchableOpacity>
        )}
        ListEmptyComponent={
          isLoading ? null : (
            <View style={styles.emptyState}>
              <Text style={styles.emptyEmoji}>✅</Text>
              <Text style={[styles.emptyText, { color: C.TEXT_SECONDARY }]}>
                {t('alerts.noAlerts')}
              </Text>
            </View>
          )
        }
      />
    </View>
  );
};

const styles = StyleSheet.create({
  flex: { flex: 1 },
  header: { paddingTop: Spacing.md, paddingHorizontal: Spacing.xl, borderBottomWidth: 0.5 },
  titleRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: Spacing.md },
  title: { ...Fonts.heading },
  locationPill: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: BorderRadius.pill },
  locationText: { ...Fonts.caption, fontWeight: '500' },
  regionScroll: { marginBottom: Spacing.md },
  regionRow: { flexDirection: 'row', gap: 8 },
  regionPill: { paddingHorizontal: Spacing.md, paddingVertical: 6, borderRadius: BorderRadius.pill, borderWidth: 1 },
  regionText: { ...Fonts.caption, fontWeight: '500' },
  listContent: { padding: Spacing.xl, gap: Spacing.md },
  emptyContent: { flex: 1 },
  alertCard: { borderRadius: BorderRadius.md, borderWidth: 0.5, padding: Spacing.lg },
  alertTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 },
  alertTime: { ...Fonts.caption },
  alertTitle: { ...Fonts.label, marginBottom: 4 },
  alertBody: { ...Fonts.body, lineHeight: 20 },
  emptyState: { alignItems: 'center', paddingVertical: 60 },
  emptyEmoji: { fontSize: 48, marginBottom: Spacing.md },
  emptyText: { ...Fonts.body, textAlign: 'center' },
});

export default AlertsScreen;
