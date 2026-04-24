import React, { memo } from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  useColorScheme,
  ViewStyle,
} from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSequence,
  withTiming,
} from 'react-native-reanimated';
import { getColors } from '../constants/colors';
import { BorderRadius, Fonts } from '../constants/fonts';

// Safe haptics — silently ignored on Expo Go / web
const triggerHaptic = () => {
  try {
    const Haptics = require('expo-haptics');
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium).catch(() => {});
  } catch { /* unsupported environment */ }
};

interface ScanButtonProps {
  label: string;
  icon: string;
  variant?: 'primary' | 'secondary';
  onPress: () => void;
  style?: ViewStyle;
  disabled?: boolean;
}

const ScanButton: React.FC<ScanButtonProps> = memo(
  ({ label, icon, variant = 'primary', onPress, style, disabled }) => {
    const scheme = useColorScheme();
    const C = getColors(scheme);
    const scale = useSharedValue(1);

    const handlePress = () => {
      triggerHaptic();
      scale.value = withSequence(
        withTiming(0.94, { duration: 80 }),
        withTiming(1, { duration: 120 }),
      );
      onPress();
    };

    const animStyle = useAnimatedStyle(() => ({
      transform: [{ scale: scale.value }],
    }));

    const isPrimary = variant === 'primary';
    const bgColor = isPrimary ? C.PRIMARY_GREEN : C.LIGHT_BLUE;
    const textColor = isPrimary ? C.WHITE : C.BLUE;

    return (
      <Animated.View style={[animStyle, style]}>
        <TouchableOpacity
          style={[styles.button, { backgroundColor: bgColor, opacity: disabled ? 0.5 : 1 }]}
          onPress={handlePress}
          disabled={disabled}
          activeOpacity={0.85}
        >
          <Text style={styles.icon}>{icon}</Text>
          <Text style={[styles.label, { color: textColor }]}>{label}</Text>
        </TouchableOpacity>
      </Animated.View>
    );
  },
);

const styles = StyleSheet.create({
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: BorderRadius.sm,
  },
  icon: { fontSize: 16 },
  label: { ...Fonts.label },
});

export default ScanButton;
