import React, { memo } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  useColorScheme,
} from 'react-native';
import { useTranslation } from 'react-i18next';
import { ScanRecord } from '../store/useHistoryStore';
import { getColors } from '../constants/colors';
import { BorderRadius, Fonts, Spacing } from '../constants/fonts';

interface HistoryItemProps {
  item: ScanRecord;
  onPress: (item: ScanRecord) => void;
}

const CROP_EMOJI: Record<string, string> = {
  Apple: '🍎',
  Maize: '🌽',
  Tomato: '🍅',
  Potato: '🥔',
  Grape: '🍇',
  Wheat: '🌾',
  Rice: '🌾',
  Cotton: '🌿',
  Pepper: '🫑',
  Peach: '🍑',
  Orange: '🍊',
  Squash: '🎃',
  Strawberry: '🍓',
  Cherry: '🍒',
  Soybean: '🌱',
  Blueberry: '🫐',
  Raspberry: '🫐',
  Default: '🌿',
};

const HistoryItem: React.FC<HistoryItemProps> = memo(({ item, onPress }) => {
  const scheme = useColorScheme();
  const C = getColors(scheme);
  const { t } = useTranslation();

  const statusStyle =
    item.status === 'active'
      ? { bg: C.LIGHT_RED, text: C.RED }
      : item.status === 'treated'
      ? { bg: C.LIGHT_AMBER, text: C.AMBER }
      : { bg: C.LIGHT_GREEN, text: C.DARK_GREEN };

  const emoji = CROP_EMOJI[item.cropName] ?? CROP_EMOJI.Default;

  const formattedDate = new Date(item.scanDate).toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });

  return (
    <TouchableOpacity
      style={[styles.container, { borderBottomColor: C.BORDER }]}
      onPress={() => onPress(item)}
      activeOpacity={0.7}
    >
      {item.imageUri ? (
        <Image source={{ uri: item.imageUri }} style={styles.thumbnail} />
      ) : (
        <View style={[styles.thumbnail, { backgroundColor: C.LIGHT_GREEN }]}>
          <Text style={styles.emoji}>{emoji}</Text>
        </View>
      )}

      <View style={styles.meta}>
        <Text style={[styles.diseaseName, { color: C.TEXT_PRIMARY }]} numberOfLines={1}>
          {item.diseaseName}
        </Text>
        <Text style={[styles.subtitle, { color: C.TEXT_SECONDARY }]}>
          {item.cropName} · {formattedDate}
        </Text>
      </View>

      <View style={[styles.statusPill, { backgroundColor: statusStyle.bg }]}>
        <Text style={[styles.statusText, { color: statusStyle.text }]}>
          {t(`history.status.${item.status}`)}
        </Text>
      </View>
    </TouchableOpacity>
  );
});

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: Spacing.md,
    gap: Spacing.md,
    borderBottomWidth: 0.5,
  },
  thumbnail: {
    width: 44,
    height: 44,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
  },
  emoji: {
    fontSize: 22,
  },
  meta: {
    flex: 1,
  },
  diseaseName: {
    ...Fonts.subheading,
    marginBottom: 2,
  },
  subtitle: {
    ...Fonts.caption,
  },
  statusPill: {
    paddingHorizontal: Spacing.sm,
    paddingVertical: 3,
    borderRadius: BorderRadius.pill,
    flexShrink: 0,
  },
  statusText: {
    fontSize: 11,
    fontWeight: '500',
  },
});

export default HistoryItem;
