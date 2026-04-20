import React, { memo } from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity, useColorScheme } from 'react-native';
import { ScanStatus } from '../store/useHistoryStore';
import { getColors } from '../constants/colors';
import { BorderRadius, Fonts, Spacing } from '../constants/fonts';
import ConfidenceBar from './ConfidenceBar';

interface DiseaseCardProps {
  diseaseName: string;
  cropName: string;
  confidence: number;
  status?: ScanStatus;
  imageUri?: string;
  onPress?: () => void;
}

const DiseaseCard: React.FC<DiseaseCardProps> = memo(
  ({ diseaseName, cropName, confidence, status, imageUri, onPress }) => {
    const scheme = useColorScheme();
    const C = getColors(scheme);

    const statusColor =
      status === 'active'
        ? { bg: C.LIGHT_RED, text: C.RED }
        : status === 'treated'
        ? { bg: C.LIGHT_AMBER, text: C.AMBER }
        : { bg: C.LIGHT_GREEN, text: C.DARK_GREEN };

    return (
      <TouchableOpacity
        style={[
          styles.card,
          {
            backgroundColor: C.CARD_BG,
            borderColor: C.BORDER,
            shadowColor: C.SHADOW,
          },
        ]}
        onPress={onPress}
        activeOpacity={0.75}
      >
        <View style={styles.row}>
          {imageUri ? (
            <Image source={{ uri: imageUri }} style={styles.thumbnail} />
          ) : (
            <View style={[styles.thumbnail, { backgroundColor: C.LIGHT_GREEN }]}>
              <Text style={styles.thumbEmoji}>🌿</Text>
            </View>
          )}
          <View style={styles.info}>
            <Text style={[styles.diseaseName, { color: C.TEXT_PRIMARY }]} numberOfLines={1}>
              {diseaseName}
            </Text>
            <Text style={[styles.cropName, { color: C.TEXT_SECONDARY }]}>{cropName}</Text>
            {status && (
              <View
                style={[
                  styles.statusPill,
                  { backgroundColor: statusColor.bg },
                ]}
              >
                <Text style={[styles.statusText, { color: statusColor.text }]}>
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </Text>
              </View>
            )}
          </View>
        </View>
        <ConfidenceBar value={confidence} showLabel={false} />
      </TouchableOpacity>
    );
  },
);

const styles = StyleSheet.create({
  card: {
    borderRadius: BorderRadius.md,
    borderWidth: 0.5,
    padding: Spacing.md,
    marginRight: Spacing.md,
    width: 180,
    elevation: 2,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
  },
  row: {
    flexDirection: 'row',
    gap: Spacing.sm,
    marginBottom: Spacing.sm,
  },
  thumbnail: {
    width: 44,
    height: 44,
    borderRadius: BorderRadius.sm,
    alignItems: 'center',
    justifyContent: 'center',
  },
  thumbEmoji: {
    fontSize: 22,
  },
  info: {
    flex: 1,
    justifyContent: 'center',
  },
  diseaseName: {
    ...Fonts.label,
    marginBottom: 2,
  },
  cropName: {
    ...Fonts.caption,
    marginBottom: 4,
  },
  statusPill: {
    alignSelf: 'flex-start',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: BorderRadius.pill,
  },
  statusText: {
    fontSize: 10,
    fontWeight: '500',
  },
});

export default DiseaseCard;
