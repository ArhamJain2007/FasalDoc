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
  withRepeat,
  withTiming,
  withSequence,
} from 'react-native-reanimated';
import ReactNativeHapticFeedback from 'react-native-haptic-feedback';
import { getColors } from '../constants/colors';
import { BorderRadius, Fonts } from '../constants/fonts';

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

    const isPrimary = variant === 'primary';

    const handlePress = () => {
      ReactNativeHapticFeedback.trigger('impactMedium', {
        enableVibrateFallback: true,
        ignoreAndroidSystemSettings: false,
      });

      scale.value = withSequence(
        withTiming(0.94, { duration: 80 }),
        withTiming(1, { duration: 120 }),
      );

      onPress();
    };

    const animatedStyle = useAnimatedStyle(() => ({
      transform: [{ scale: scale.value }],
    }));

    const bgColor = isPrimary ? C.PRIMARY_GREEN : C.LIGHT_BLUE;
    const textColor = isPrimary ? C.WHITE : C.BLUE;

    return (
      <Animated.View style={animatedStyle}>
        <TouchableOpacity
          style={[
            styles.button,
            { backgroundColor: bgColor, opacity: disabled ? 0.5 : 1 },
            style,
          ]}
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

export const PulsingScanButton: React.FC<ScanButtonProps> = (props) => {
  const pulse = useSharedValue(1);

  React.useEffect(() => {
    pulse.value = withRepeat(
      withSequence(
        withTiming(1.06, { duration: 700 }),
        withTiming(1, { duration: 700 }),
      ),
      -1,
      false,
    );
  }, []);

  const pulseStyle = useAnimatedStyle(() => ({
    transform: [{ scale: pulse.value }],
  }));

  return (
    <Animated.View style={pulseStyle}>
      <ScanButton {...props} />
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: BorderRadius.sm,
  },
  icon: {
    fontSize: 16,
  },
  label: {
    ...Fonts.label,
  },
});

export default ScanButton;
