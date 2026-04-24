import React, { useState } from 'react';
import {
  View, Text, StyleSheet, ScrollView, Switch,
  TouchableOpacity, useColorScheme, Alert, TextInput,
} from 'react-native';
import { useTranslation } from 'react-i18next';
import { LANGUAGES, SupportedLanguage } from '../i18n';
import { useLanguageStore } from '../store/useLanguageStore';
import { useAuthStore } from '../store/useAuthStore';
import { getColors } from '../constants/colors';
import { BorderRadius, Fonts, Spacing } from '../constants/fonts';

const CROPS = ['wheat', 'tomato', 'maize', 'rice', 'cotton', 'potato', 'mustard', 'soybean'];

const SettingsScreen: React.FC = () => {
  const scheme = useColorScheme();
  const C = getColors(scheme);
  const { t } = useTranslation();
  const { language, setLanguage } = useLanguageStore();
  const { userName, userRegion, logout } = useAuthStore();

  const [seasonalAlerts, setSeasonalAlerts]   = useState(true);
  const [weeklyTips, setWeeklyTips]           = useState(true);
  const [highRisk, setHighRisk]               = useState(true);
  const [selectedCrops, setSelectedCrops]     = useState<string[]>(['wheat', 'tomato']);
  const [farmerName, setFarmerName]           = useState(userName ?? '');

  const toggleCrop = (crop: string) => {
    setSelectedCrops((prev) =>
      prev.includes(crop) ? prev.filter((c) => c !== crop) : [...prev, crop],
    );
  };

  const handleLogout = () => {
    Alert.alert('Logout', 'Are you sure you want to logout?', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Logout', style: 'destructive', onPress: logout },
    ]);
  };

  const SectionTitle = ({ label }: { label: string }) => (
    <Text style={[styles.sectionTitle, { color: C.TEXT_TERTIARY }]}>{label}</Text>
  );

  const RowSwitch = ({
    label, value, onValueChange,
  }: { label: string; value: boolean; onValueChange: (v: boolean) => void }) => (
    <View style={[styles.row, { borderBottomColor: C.BORDER }]}>
      <Text style={[styles.rowLabel, { color: C.TEXT_PRIMARY }]}>{label}</Text>
      <Switch
        value={value}
        onValueChange={onValueChange}
        trackColor={{ false: C.BORDER, true: C.PRIMARY_GREEN }}
        thumbColor={C.WHITE}
      />
    </View>
  );

  return (
    <ScrollView
      style={[styles.flex, { backgroundColor: C.GRAY_BG }]}
      contentContainerStyle={styles.scroll}
      showsVerticalScrollIndicator={false}
    >
      <Text style={[styles.pageTitle, { color: C.TEXT_PRIMARY }]}>Settings</Text>

      {/* ── Language ── */}
      <SectionTitle label={t('settings.language').toUpperCase()} />
      <View style={[styles.card, { backgroundColor: C.CARD_BG, borderColor: C.BORDER }]}>
        <Text style={[styles.rowLabel, { color: C.TEXT_SECONDARY, marginBottom: Spacing.sm }]}>
          {t('settings.languageLabel')}
        </Text>
        <View style={styles.langRow}>
          {LANGUAGES.map((lang) => (
            <TouchableOpacity
              key={lang.code}
              onPress={() => setLanguage(lang.code as SupportedLanguage)}
              style={[
                styles.langPill,
                {
                  backgroundColor: language === lang.code ? C.PRIMARY_GREEN : C.GRAY_BG,
                  borderColor: language === lang.code ? C.PRIMARY_GREEN : C.BORDER,
                },
              ]}
            >
              <Text style={[styles.langText, { color: language === lang.code ? C.WHITE : C.TEXT_SECONDARY }]}>
                {lang.nativeLabel}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* ── Notifications ── */}
      <SectionTitle label={t('settings.notifications').toUpperCase()} />
      <View style={[styles.card, { backgroundColor: C.CARD_BG, borderColor: C.BORDER }]}>
        <RowSwitch label={t('settings.seasonalAlerts')} value={seasonalAlerts} onValueChange={setSeasonalAlerts} />
        <RowSwitch label={t('settings.weeklyTips')}     value={weeklyTips}     onValueChange={setWeeklyTips} />
        <RowSwitch label={t('settings.highRiskWarnings')} value={highRisk}     onValueChange={setHighRisk} />
      </View>

      {/* ── Account ── */}
      <SectionTitle label={t('settings.account').toUpperCase()} />
      <View style={[styles.card, { backgroundColor: C.CARD_BG, borderColor: C.BORDER }]}>
        <View style={styles.inputRow}>
          <Text style={[styles.fieldLabel, { color: C.TEXT_SECONDARY }]}>
            {t('settings.farmerName')}
          </Text>
          <TextInput
            style={[styles.input, { backgroundColor: C.GRAY_BG, color: C.TEXT_PRIMARY, borderColor: C.BORDER }]}
            value={farmerName}
            onChangeText={setFarmerName}
            placeholder="Your name"
            placeholderTextColor={C.TEXT_TERTIARY}
          />
        </View>

        {userRegion && (
          <View style={[styles.row, { borderBottomColor: C.BORDER }]}>
            <Text style={[styles.rowLabel, { color: C.TEXT_PRIMARY }]}>{t('settings.region')}</Text>
            <Text style={[styles.rowValue, { color: C.PRIMARY_GREEN }]}>{userRegion}</Text>
          </View>
        )}

        <Text style={[styles.fieldLabel, { color: C.TEXT_SECONDARY, marginTop: Spacing.md }]}>
          {t('settings.primaryCrops')}
        </Text>
        <View style={styles.cropsWrap}>
          {CROPS.map((crop) => (
            <TouchableOpacity
              key={crop}
              onPress={() => toggleCrop(crop)}
              style={[
                styles.cropChip,
                {
                  backgroundColor: selectedCrops.includes(crop) ? C.LIGHT_GREEN : C.GRAY_BG,
                  borderColor: selectedCrops.includes(crop) ? C.PRIMARY_GREEN : C.BORDER,
                },
              ]}
            >
              <Text style={[styles.cropText, { color: selectedCrops.includes(crop) ? C.DARK_GREEN : C.TEXT_SECONDARY }]}>
                {t(`settings.crops.${crop}`)}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* ── About ── */}
      <SectionTitle label={t('settings.about').toUpperCase()} />
      <View style={[styles.card, { backgroundColor: C.CARD_BG, borderColor: C.BORDER }]}>
        <View style={[styles.row, { borderBottomColor: C.BORDER }]}>
          <Text style={[styles.rowLabel, { color: C.TEXT_PRIMARY }]}>{t('settings.version')}</Text>
          <Text style={[styles.rowValue, { color: C.TEXT_SECONDARY }]}>1.0.0</Text>
        </View>
        <View style={[styles.row, { borderBottomColor: 'transparent' }]}>
          <Text style={[styles.rowLabel, { color: C.TEXT_PRIMARY }]}>Model</Text>
          <Text style={[styles.rowValue, { color: C.TEXT_SECONDARY }]}>EfficientNet-B4 · 14MB</Text>
        </View>
      </View>

      {/* Logout */}
      <TouchableOpacity
        style={[styles.logoutBtn, { borderColor: C.RED }]}
        onPress={handleLogout}
        activeOpacity={0.8}
      >
        <Text style={[styles.logoutText, { color: C.RED }]}>Logout</Text>
      </TouchableOpacity>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  flex: { flex: 1 },
  scroll: { padding: Spacing.xl, paddingBottom: 48 },
  pageTitle: { ...Fonts.heading, fontSize: 22, marginBottom: Spacing.xl },
  sectionTitle: { ...Fonts.caption, letterSpacing: 0.8, fontWeight: '600', marginTop: Spacing.lg, marginBottom: Spacing.sm },
  card: { borderRadius: BorderRadius.md, borderWidth: 0.5, paddingHorizontal: Spacing.lg, marginBottom: Spacing.sm },
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 14, borderBottomWidth: 0.5 },
  rowLabel: { ...Fonts.body, flex: 1 },
  rowValue: { ...Fonts.body },
  langRow: { flexDirection: 'row', gap: 8, paddingBottom: Spacing.md },
  langPill: { paddingHorizontal: Spacing.md, paddingVertical: 8, borderRadius: BorderRadius.pill, borderWidth: 1.5 },
  langText: { ...Fonts.label },
  inputRow: { paddingVertical: Spacing.md },
  fieldLabel: { ...Fonts.caption, fontWeight: '500', marginBottom: 6 },
  input: { borderRadius: BorderRadius.sm, borderWidth: 0.5, paddingHorizontal: Spacing.md, paddingVertical: 10, ...Fonts.body },
  cropsWrap: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, paddingVertical: Spacing.md },
  cropChip: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: BorderRadius.pill, borderWidth: 1 },
  cropText: { ...Fonts.caption, fontWeight: '500' },
  logoutBtn: { borderRadius: BorderRadius.sm, borderWidth: 1.5, paddingVertical: 14, alignItems: 'center', marginTop: Spacing.xl },
  logoutText: { ...Fonts.subheading, fontWeight: '600' },
});

export default SettingsScreen;
