import React from 'react';
import { View, TouchableOpacity, Text, StyleSheet, useColorScheme } from 'react-native';
import { LANGUAGES, SupportedLanguage } from '../i18n';
import { useLanguageStore } from '../store/useLanguageStore';
import { getColors } from '../constants/colors';
import { BorderRadius, Fonts, Spacing } from '../constants/fonts';

const LanguageSwitcher: React.FC = () => {
  const scheme = useColorScheme();
  const C = getColors(scheme);
  const { language, setLanguage } = useLanguageStore();

  const handlePress = (code: SupportedLanguage) => {
    setLanguage(code);
  };

  return (
    <View style={styles.container}>
      {LANGUAGES.map((lang) => {
        const isActive = language === lang.code;
        return (
          <TouchableOpacity
            key={lang.code}
            onPress={() => handlePress(lang.code)}
            style={[
              styles.pill,
              {
                borderColor: isActive ? C.PRIMARY_GREEN : C.BORDER,
                backgroundColor: isActive ? C.LIGHT_GREEN : 'transparent',
              },
            ]}
            activeOpacity={0.7}
          >
            <Text
              style={[
                styles.pillText,
                { color: isActive ? C.PRIMARY_GREEN : C.TEXT_SECONDARY },
              ]}
            >
              {lang.nativeLabel}
            </Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    gap: Spacing.xs,
    alignItems: 'center',
  },
  pill: {
    paddingHorizontal: Spacing.sm,
    paddingVertical: 4,
    borderRadius: BorderRadius.pill,
    borderWidth: 1.5,
  },
  pillText: {
    ...Fonts.caption,
    fontWeight: '500',
  },
});

export default LanguageSwitcher;
