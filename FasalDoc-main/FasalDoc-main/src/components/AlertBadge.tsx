import React, { memo } from 'react';
import { View, Text, StyleSheet, useColorScheme } from 'react-native';
import { useTranslation } from 'react-i18next';
import { AlertType } from '../store/useAlertStore';
import { getColors } from '../constants/colors';
import { BorderRadius, Fonts } from '../constants/fonts';

interface AlertBadgeProps {
  type: AlertType;
}

const AlertBadge: React.FC<AlertBadgeProps> = memo(({ type }) => {
  const scheme = useColorScheme();
  const C = getColors(scheme);
  const { t } = useTranslation();

  const config =
    type === 'danger'
      ? { dot: C.RED, bg: C.LIGHT_RED, text: C.RED }
      : type === 'warning'
      ? { dot: C.AMBER, bg: C.LIGHT_AMBER, text: C.AMBER }
      : { dot: C.PRIMARY_GREEN, bg: C.LIGHT_GREEN, text: C.DARK_GREEN };

  return (
    <View style={[styles.badge, { backgroundColor: config.bg }]}>
      <View style={[styles.dot, { backgroundColor: config.dot }]} />
      <Text style={[styles.label, { color: config.text }]}>
        {t(`alerts.type.${type}`)}
      </Text>
    </View>
  );
});

const styles = StyleSheet.create({
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: BorderRadius.pill,
    alignSelf: 'flex-start',
  },
  dot: {
    width: 7,
    height: 7,
    borderRadius: 4,
  },
  label: {
    ...Fonts.caption,
    fontWeight: '500',
  },
});

export default AlertBadge;
