import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Switch,
  TouchableOpacity,
  TextInput,
  KeyboardAvoidingView,
  Platform,
  useColorScheme,
  Linking,
  SafeAreaView,
} from 'react-native';
import { useTranslation } from 'react-i18next';
import { LANGUAGES, SupportedLanguage } from '../i18n';
import { useLanguageStore } from '../store/useLanguageStore';
import { getColors } from '../constants/colors';
import { BorderRadius, Fonts, Spacing } from '../constants/fonts';

const APP_VERSION = '1.0.0';
const MODEL_SIZE = '14 MB';

const CROP_OPTIONS = ['wheat', 'tomato', 'maize', 'rice', 'cotton', 'potato', 'mustard', 'soybean'];

const SettingsScreen: React.FC = () => {
  const scheme = useColorScheme();
  const C = getColors(scheme);
  const { t } = useTranslation();
  const { language, setLanguage } = useLanguageStore();

  const [seasonalAlerts, setSeasonalAlerts] = useState(true);
  const [weeklyTips, setWeeklyTips] = useState(true);
  const [highRisk, setHighRisk] = useState(true);
  const [farmerName, setFarmerName] = useState('');
  const [selectedCrops, setSelectedCrops] = useState<string[]>(['wheat']);

  const toggleCrop = (crop: string) => {
    setSelectedCrops((prev) =>
      prev.includes(crop) ? prev.filter((c) => c !== crop) : [...prev, crop],
    );
  };

  const cardStyle = {
    backgroundColor: C.CARD_BG,
    borderColor: C.BORDER,
  };

  const Section = ({ title, children }: { title: string; children: React.ReactNode }) => (
    <View style={styles.sectionGroup}>
      <Text style={[styles.sectionHeader, { color: C.TEXT_TERTIARY }]}>{title}</Text>
      <View style={[styles.sectionCard, cardStyle]}>{children}</View>
    </View>
  );

  const Row = ({
    label,
    right,
    noBorder,
  }: {
    label: string;
    right: React.ReactNode;
    noBorder?: boolean;
  }) => (
    <View
      style={[
        styles.row,
        !noBorder && { borderBottomWidth: 0.5, borderBottomColor: C.BORDER },
      ]}
    >
      <Text style={[styles.rowLabel, { color: C.TEXT_PRIMARY }]}>{label}</Text>
      {right}
    </View>
  );

  return (
    <SafeAreaView style={[styles.safeArea, { backgroundColor: C.GRAY_BG }]}>
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <ScrollView
          contentContainerStyle={styles.content}
          showsVerticalScrollIndicator={false}
        >
          <Text style={[styles.screenTitle, { color: C.TEXT_PRIMARY }]}>
            {t('settings.language')}
          </Text>

          {/* Language */}
          <Section title={t('settings.languageLabel')}>
            {LANGUAGES.map((lang, idx) => {
              const isLast = idx === LANGUAGES.length - 1;
              const isActive = language === lang.code;
              return (
                <TouchableOpacity
                  key={lang.code}
                  style={[
                    styles.row,
                    !isLast && { borderBottomWidth: 0.5, borderBottomColor: C.BORDER },
                  ]}
                  onPress={() => setLanguage(lang.code as SupportedLanguage)}
                  activeOpacity={0.7}
                >
                  <View style={styles.langRow}>
                    <View
                      style={[
                        styles.radio,
                        {
                          borderColor: isActive ? C.PRIMARY_GREEN : C.BORDER,
                          backgroundColor: isActive ? C.PRIMARY_GREEN : 'transparent',
                        },
                      ]}
                    />
                    <Text style={[styles.rowLabel, { color: C.TEXT_PRIMARY }]}>
                      {lang.nativeLabel}
                    </Text>
                  </View>
                  {isActive && (
                    <Text style={{ color: C.PRIMARY_GREEN, fontSize: 16 }}>✓</Text>
                  )}
                </TouchableOpacity>
              );
            })}
          </Section>

          {/* Notifications */}
          <Section title={t('settings.notifications')}>
            <Row
              label={t('settings.seasonalAlerts')}
              right={
                <Switch
                  value={seasonalAlerts}
                  onValueChange={setSeasonalAlerts}
                  trackColor={{ false: C.BORDER, true: C.PRIMARY_GREEN }}
                  thumbColor={C.WHITE}
                />
              }
            />
            <Row
              label={t('settings.weeklyTips')}
              right={
                <Switch
                  value={weeklyTips}
                  onValueChange={setWeeklyTips}
                  trackColor={{ false: C.BORDER, true: C.PRIMARY_GREEN }}
                  thumbColor={C.WHITE}
                />
              }
            />
            <Row
              label={t('settings.highRiskWarnings')}
              noBorder
              right={
                <Switch
                  value={highRisk}
                  onValueChange={setHighRisk}
                  trackColor={{ false: C.BORDER, true: C.PRIMARY_GREEN }}
                  thumbColor={C.WHITE}
                />
              }
            />
          </Section>

          {/* Offline model */}
          <Section title={t('settings.offlineModel')}>
            <Row
              label={t('settings.modelName')}
              noBorder
              right={
                <View style={styles.modelRight}>
                  <Text style={[styles.modelSize, { color: C.TEXT_TERTIARY }]}>
                    {MODEL_SIZE}
                  </Text>
                  <TouchableOpacity
                    style={[styles.updateBtn, { backgroundColor: C.LIGHT_GREEN }]}
                  >
                    <Text style={[styles.updateBtnText, { color: C.DARK_GREEN }]}>
                      {t('settings.updateModel')}
                    </Text>
                  </TouchableOpacity>
                </View>
              }
            />
          </Section>

          {/* Account */}
          <Section title={t('settings.account')}>
            <View
              style={[styles.row, { borderBottomWidth: 0.5, borderBottomColor: C.BORDER }]}
            >
              <Text style={[styles.rowLabel, { color: C.TEXT_PRIMARY }]}>
                {t('settings.farmerName')}
              </Text>
              <TextInput
                value={farmerName}
                onChangeText={setFarmerName}
                placeholder={t('settings.farmerName')}
                placeholderTextColor={C.TEXT_TERTIARY}
                style={[styles.input, { color: C.TEXT_PRIMARY, borderColor: C.BORDER }]}
              />
            </View>

            <View style={styles.cropSection}>
              <Text style={[styles.rowLabel, { color: C.TEXT_PRIMARY, marginBottom: 8 }]}>
                {t('settings.primaryCrops')}
              </Text>
              <View style={styles.cropGrid}>
                {CROP_OPTIONS.map((crop) => {
                  const isSelected = selectedCrops.includes(crop);
                  return (
                    <TouchableOpacity
                      key={crop}
                      style={[
                        styles.cropPill,
                        {
                          backgroundColor: isSelected ? C.PRIMARY_GREEN : C.GRAY_BG,
                          borderColor: isSelected ? C.PRIMARY_GREEN : C.BORDER,
                        },
                      ]}
                      onPress={() => toggleCrop(crop)}
                      activeOpacity={0.7}
                    >
                      <Text
                        style={[
                          styles.cropText,
                          { color: isSelected ? C.WHITE : C.TEXT_SECONDARY },
                        ]}
                      >
                        {t(`settings.crops.${crop}`)}
                      </Text>
                    </TouchableOpacity>
                  );
                })}
              </View>
            </View>
          </Section>

          {/* About */}
          <Section title={t('settings.about')}>
            <Row
              label={t('settings.version')}
              right={
                <Text style={[styles.versionText, { color: C.TEXT_TERTIARY }]}>
                  v{APP_VERSION}
                </Text>
              }
            />
            <TouchableOpacity
              style={[styles.row]}
              onPress={() => Linking.openURL('https://apps.apple.com')}
              activeOpacity={0.7}
            >
              <Text style={[styles.rowLabel, { color: C.PRIMARY_GREEN }]}>
                {t('settings.rateApp')} ⭐
              </Text>
            </TouchableOpacity>
          </Section>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: { flex: 1 },
  content: {
    padding: Spacing.lg,
    gap: Spacing.lg,
    paddingBottom: Spacing.xxxl,
  },
  screenTitle: {
    ...Fonts.heading,
    marginBottom: -Spacing.sm,
  },
  sectionGroup: {
    gap: Spacing.xs,
  },
  sectionHeader: {
    ...Fonts.caption,
    fontWeight: '500',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    paddingHorizontal: 4,
    marginBottom: 2,
  },
  sectionCard: {
    borderRadius: BorderRadius.md,
    borderWidth: 0.5,
    overflow: 'hidden',
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.md,
    minHeight: 48,
  },
  rowLabel: {
    ...Fonts.body,
    flex: 1,
  },
  langRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.md,
    flex: 1,
  },
  radio: {
    width: 18,
    height: 18,
    borderRadius: 9,
    borderWidth: 2,
  },
  modelRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
  },
  modelSize: {
    ...Fonts.caption,
  },
  updateBtn: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: BorderRadius.pill,
  },
  updateBtnText: {
    fontSize: 11,
    fontWeight: '500',
  },
  input: {
    ...Fonts.body,
    borderWidth: 0.5,
    borderRadius: BorderRadius.sm,
    paddingHorizontal: Spacing.sm,
    paddingVertical: 6,
    minWidth: 140,
    textAlign: 'right',
  },
  cropSection: {
    padding: Spacing.md,
  },
  cropGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.sm,
  },
  cropPill: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: BorderRadius.pill,
    borderWidth: 0.5,
  },
  cropText: {
    fontSize: 12,
    fontWeight: '500',
  },
  versionText: {
    ...Fonts.caption,
  },
});

export default SettingsScreen;
