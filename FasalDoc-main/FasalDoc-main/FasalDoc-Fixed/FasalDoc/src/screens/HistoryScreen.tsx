import React, { useEffect, useState, useCallback } from 'react';
import {
  View, Text, StyleSheet, FlatList, ScrollView,
  TouchableOpacity, useColorScheme, RefreshControl,
} from 'react-native';
import { useTranslation } from 'react-i18next';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useHistoryStore, ScanRecord, ScanStatus } from '../store/useHistoryStore';
import { getColors } from '../constants/colors';
import { BorderRadius, Fonts, Spacing } from '../constants/fonts';
import HistoryItem from '../components/HistoryItem';
import type { RootStackParamList } from '../navigation/AppNavigator';

type NavProp = NativeStackNavigationProp<RootStackParamList, 'MainTabs'>;

type Filter = 'all' | ScanStatus;
const FILTERS: Filter[] = ['all', 'active', 'treated', 'resolved'];

const HistoryScreen: React.FC = () => {
  const scheme = useColorScheme();
  const C = getColors(scheme);
  const { t } = useTranslation();
  const navigation = useNavigation<NavProp>();
  const { scans, isLoading, loadFromDB } = useHistoryStore();
  const [filter, setFilter] = useState<Filter>('all');

  useEffect(() => { loadFromDB(); }, []);

  const filtered = filter === 'all' ? scans : scans.filter((s) => s.status === filter);

  const handlePress = useCallback((item: ScanRecord) => {
    navigation.navigate('Result', {
      result: {
        scan_id: item.id,
        diseaseName: item.diseaseName,
        cropName: item.cropName,
        confidence: item.confidence,
        stage: item.stage,
        treatmentId: item.treatmentId,
        description: item.description ?? '',
        severity: item.severity ?? 'medium',
        image_url: item.imageUri,
        scan_date: item.scanDate,
      },
      imageUri: item.imageUri,
    });
  }, [navigation]);

  return (
    <View style={[styles.flex, { backgroundColor: C.GRAY_BG }]}>
      {/* Header */}
      <View style={[styles.header, { backgroundColor: C.CARD_BG, borderBottomColor: C.BORDER }]}>
        <Text style={[styles.title, { color: C.TEXT_PRIMARY }]}>{t('history.title')}</Text>

        {/* Filter pills */}
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterScroll}>
          <View style={styles.filterRow}>
            {FILTERS.map((f) => (
              <TouchableOpacity
                key={f}
                onPress={() => setFilter(f)}
                style={[
                  styles.filterPill,
                  {
                    backgroundColor: filter === f ? C.PRIMARY_GREEN : C.GRAY_BG,
                    borderColor: filter === f ? C.PRIMARY_GREEN : C.BORDER,
                  },
                ]}
              >
                <Text
                  style={[
                    styles.filterText,
                    { color: filter === f ? C.WHITE : C.TEXT_SECONDARY },
                  ]}
                >
                  {t(`history.filter.${f}`)}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </ScrollView>
      </View>

      {/* List */}
      <FlatList
        data={filtered}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <HistoryItem item={item} onPress={handlePress} />}
        contentContainerStyle={[
          styles.listContent,
          { backgroundColor: C.CARD_BG },
          filtered.length === 0 && styles.emptyContent,
        ]}
        refreshControl={
          <RefreshControl
            refreshing={isLoading}
            onRefresh={loadFromDB}
            tintColor={C.PRIMARY_GREEN}
            colors={[C.PRIMARY_GREEN]}
          />
        }
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <Text style={styles.emptyEmoji}>🌱</Text>
            <Text style={[styles.emptyText, { color: C.TEXT_SECONDARY }]}>
              {t('history.empty')}
            </Text>
          </View>
        }
        ListFooterComponent={
          filtered.length > 0 ? (
            <Text style={[styles.footer, { color: C.TEXT_TERTIARY }]}>
              {t('history.synced')}
            </Text>
          ) : null
        }
      />
    </View>
  );
};

const styles = StyleSheet.create({
  flex: { flex: 1 },
  header: { paddingTop: Spacing.md, paddingHorizontal: Spacing.xl, borderBottomWidth: 0.5 },
  title: { ...Fonts.heading, marginBottom: Spacing.md },
  filterScroll: { marginBottom: Spacing.md },
  filterRow: { flexDirection: 'row', gap: 8, paddingBottom: 2 },
  filterPill: {
    paddingHorizontal: Spacing.md, paddingVertical: 6,
    borderRadius: BorderRadius.pill, borderWidth: 1,
  },
  filterText: { ...Fonts.caption, fontWeight: '500' },
  listContent: { paddingHorizontal: Spacing.xl, paddingBottom: 32 },
  emptyContent: { flex: 1 },
  emptyState: { alignItems: 'center', paddingVertical: 60 },
  emptyEmoji: { fontSize: 48, marginBottom: Spacing.md },
  emptyText: { ...Fonts.body, textAlign: 'center' },
  footer: { ...Fonts.caption, textAlign: 'center', paddingVertical: Spacing.xl },
});

export default HistoryScreen;
