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
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useTranslation } from 'react-i18next';

import { RootStackParamList } from '../navigation/AppNavigator';
import { getColors } from '../constants/colors';
import { BorderRadius, Fonts, Spacing } from '../constants/fonts';
import HistoryItem from '../components/HistoryItem';
import { useHistoryStore, ScanRecord, ScanStatus } from '../store/useHistoryStore';

type NavProp = NativeStackNavigationProp<RootStackParamList>;
type FilterKey = 'all' | ScanStatus;

const FILTERS: FilterKey[] = ['all', 'active', 'treated', 'resolved'];

const HistoryScreen: React.FC = () => {
  const scheme = useColorScheme();
  const C = getColors(scheme);
  const { t } = useTranslation();
  const navigation = useNavigation<NavProp>();
  const { scans, isLoading, loadFromDB } = useHistoryStore();

  const [activeFilter, setActiveFilter] = useState<FilterKey>('all');

  useEffect(() => {
    loadFromDB();
  }, []);

  const filtered =
    activeFilter === 'all' ? scans : scans.filter((s) => s.status === activeFilter);

  const handleItemPress = useCallback(
    (item: ScanRecord) => {
      navigation.navigate('Result', {
        diseaseName: item.diseaseName,
        confidence: item.confidence,
        cropName: item.cropName,
        stage: item.stage,
        imageUri: item.imageUri,
        scanDate: item.scanDate,
        treatmentId: item.treatmentId,
        description: item.description,
        severity: item.severity,
        scanId: item.id,
      });
    },
    [navigation],
  );

  const renderItem = useCallback(
    ({ item }: { item: ScanRecord }) => (
      <HistoryItem item={item} onPress={handleItemPress} />
    ),
    [handleItemPress],
  );

  const keyExtractor = useCallback((item: ScanRecord) => item.id, []);

  const EmptyState = () => (
    <View style={styles.emptyState}>
      <Text style={styles.emptyEmoji}>🌿</Text>
      <Text style={[styles.emptyText, { color: C.TEXT_SECONDARY }]}>
        {t('history.empty')}
      </Text>
    </View>
  );

  return (
    <SafeAreaView style={[styles.safeArea, { backgroundColor: C.GRAY_BG }]}>
      {/* Header */}
      <View style={[styles.header, { backgroundColor: C.CARD_BG, borderBottomColor: C.BORDER }]}>
        <Text style={[styles.title, { color: C.TEXT_PRIMARY }]}>{t('history.title')}</Text>
      </View>

      {/* Filter pills */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={[styles.filterBar, { backgroundColor: C.CARD_BG }]}
        contentContainerStyle={styles.filterContent}
      >
        {FILTERS.map((f) => {
          const isActive = activeFilter === f;
          return (
            <TouchableOpacity
              key={f}
              style={[
                styles.filterPill,
                {
                  backgroundColor: isActive ? C.PRIMARY_GREEN : C.GRAY_BG,
                  borderColor: isActive ? C.PRIMARY_GREEN : C.BORDER,
                },
              ]}
              onPress={() => setActiveFilter(f)}
              activeOpacity={0.7}
            >
              <Text
                style={[
                  styles.filterText,
                  { color: isActive ? C.WHITE : C.TEXT_SECONDARY },
                ]}
              >
                {t(`history.filter.${f}`)}
              </Text>
            </TouchableOpacity>
          );
        })}
      </ScrollView>

      {/* List */}
      <FlatList
        data={filtered}
        keyExtractor={keyExtractor}
        renderItem={renderItem}
        ListEmptyComponent={isLoading ? null : <EmptyState />}
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={false}
        refreshing={isLoading}
        onRefresh={loadFromDB}
        ListFooterComponent={
          filtered.length > 0 ? (
            <Text style={[styles.footer, { color: C.TEXT_TERTIARY }]}>
              {t('history.synced')}
            </Text>
          ) : null
        }
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: { flex: 1 },
  header: {
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md,
    borderBottomWidth: 0.5,
  },
  title: {
    ...Fonts.heading,
  },
  filterBar: {
    maxHeight: 56,
    borderBottomWidth: 0.5,
  },
  filterContent: {
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.sm,
    gap: Spacing.sm,
    flexDirection: 'row',
    alignItems: 'center',
  },
  filterPill: {
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: BorderRadius.pill,
    borderWidth: 0.5,
  },
  filterText: {
    ...Fonts.caption,
    fontWeight: '500',
  },
  listContent: {
    paddingHorizontal: Spacing.lg,
    paddingBottom: Spacing.xxxl,
    flexGrow: 1,
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
    maxWidth: 260,
  },
  footer: {
    ...Fonts.caption,
    textAlign: 'center',
    marginTop: Spacing.xl,
    marginBottom: Spacing.md,
  },
});

export default HistoryScreen;
