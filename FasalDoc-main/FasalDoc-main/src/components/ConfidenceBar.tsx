import React, { useEffect } from 'react';
import { View, Text, StyleSheet, useColorScheme } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withTiming,
  Easing,
} from 'react-native-reanimated';
import { useTranslation } from 'react-i18next';
import { getColors } from '../constants/colors';
import { Fonts } from '../constants/fonts';

interface ConfidenceBarProps {
  value: number; // 0–100
  showLabel?: boolean;
}

const ConfidenceBar: React.FC<ConfidenceBarProps> = ({ value, showLabel = true }) => {
  const scheme = useColorScheme();
  const C = getColors(scheme);
  const { t } = useTranslation();
  const width = useSharedValue(0);

  const barColor =
    value >= 80 ? C.PRIMARY_GREEN : value >= 60 ? C.AMBER : C.RED;

  useEffect(() => {
    width.value = withTiming(value, {
      duration: 800,
      easing: Easing.out(Easing.cubic),
    });
  }, [value]);

  const animatedStyle = useAnimatedStyle(() => ({
    width: `${width.value}%`,
  }));

  return (
    <View style={styles.container}>
      {showLabel && (
        <View style={styles.labelRow}>
          <Text style={[styles.label, { color: C.TEXT_SECONDARY }]}>
            {t('result.confidence')}
          </Text>
          <Text style={[styles.value, { color: barColor }]}>{value}%</Text>
        </View>
      )}
      <View style={[styles.track, { backgroundColor: C.GRAY_BG }]}>
        <Animated.View
          style={[styles.fill, { backgroundColor: barColor }, animatedStyle]}
        />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: 6,
  },
  labelRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  label: {
    ...Fonts.caption,
  },
  value: {
    ...Fonts.caption,
    fontWeight: '500',
  },
  track: {
    height: 5,
    borderRadius: 3,
    overflow: 'hidden',
  },
  fill: {
    height: '100%',
    borderRadius: 3,
  },
});

export default ConfidenceBar;
