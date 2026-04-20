import React, { memo } from 'react';
import { View, Text, StyleSheet, useColorScheme } from 'react-native';
import { getColors } from '../constants/colors';
import { BorderRadius, Fonts } from '../constants/fonts';

interface TreatmentTagProps {
  label: string;
  type: 'organic' | 'chemical' | 'neutral';
}

const TreatmentTag: React.FC<TreatmentTagProps> = memo(({ label, type }) => {
  const scheme = useColorScheme();
  const C = getColors(scheme);

  const config =
    type === 'organic'
      ? { bg: C.LIGHT_GREEN, text: C.DARK_GREEN }
      : type === 'chemical'
      ? { bg: C.LIGHT_AMBER, text: C.AMBER }
      : { bg: C.LIGHT_BLUE, text: C.BLUE };

  return (
    <View style={[styles.tag, { backgroundColor: config.bg }]}>
      <Text style={[styles.label, { color: config.text }]}>{label}</Text>
    </View>
  );
});

const styles = StyleSheet.create({
  tag: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: BorderRadius.pill,
    margin: 4,
  },
  label: {
    ...Fonts.caption,
    fontWeight: '500',
  },
});

export default TreatmentTag;
