import React, { useEffect, useState } from 'react';
import {
  View, Text, StyleSheet, ScrollView, Share,
  TouchableOpacity, useColorScheme, ActivityIndicator,
} from 'react-native';
import { useTranslation } from 'react-i18next';
import { useRoute, RouteProp } from '@react-navigation/native';
import { getTreatment } from '../services/api';
import { useLanguageStore } from '../store/useLanguageStore';
import type { RootStackParamList } from '../navigation/AppNavigator';
import { getColors } from '../constants/colors';
import { BorderRadius, Fonts, Spacing } from '../constants/fonts';
import TreatmentTag from '../components/TreatmentTag';
import type { TreatmentData } from '../services/api';

type RouteProps = RouteProp<RootStackParamList, 'Treatment'>;

const TreatmentScreen: React.FC = () => {
  const scheme = useColorScheme();
  const C = getColors(scheme);
  const { t } = useTranslation();
  const route = useRoute<RouteProps>();
  const { language } = useLanguageStore();

  const { treatmentId, diseaseName, cropName, stage } = route.params;
  const [treatment, setTreatment] = useState<TreatmentData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetch = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await getTreatment(treatmentId, language);
        setTreatment(data);
      } catch (err: any) {
        setError(err?.response?.data?.message ?? 'Failed to load treatment');
      } finally {
        setIsLoading(false);
      }
    };
    fetch();
  }, [treatmentId, language]);

  const handleShare = async () => {
    if (!treatment) return;
    const msg = `FasalDoc Treatment Plan\n\n${diseaseName} (${cropName})\n\nOrganic: ${treatment.organic.join(', ')}\nChemical: ${treatment.chemical.join(', ')}\nDosage: ${treatment.dosage}`;
    await Share.share({ message: msg });
  };

  if (isLoading) {
    return (
      <View style={[styles.center, { backgroundColor: C.GRAY_BG }]}>
        <ActivityIndicator size="large" color={C.PRIMARY_GREEN} />
      </View>
    );
  }

  if (error || !treatment) {
    return (
      <View style={[styles.center, { backgroundColor: C.GRAY_BG }]}>
        <Text style={{ fontSize: 40, marginBottom: 12 }}>😔</Text>
        <Text style={[styles.errorText, { color: C.TEXT_SECONDARY }]}>
          {error ?? t('treatment.noTreatment')}
        </Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={[styles.flex, { backgroundColor: C.GRAY_BG }]}
      contentContainerStyle={styles.scroll}
      showsVerticalScrollIndicator={false}
    >
      {/* Disease header */}
      <View style={[styles.diseaseHeader, { backgroundColor: C.LIGHT_GREEN }]}>
        <Text style={[styles.diseaseName, { color: C.DARK_GREEN }]}>{diseaseName}</Text>
        <View style={styles.metaRow}>
          <View style={[styles.metaPill, { backgroundColor: C.PRIMARY_GREEN }]}>
            <Text style={styles.metaPillText}>{cropName}</Text>
          </View>
          <View style={[styles.metaPill, { backgroundColor: C.CARD_BG }]}>
            <Text style={[styles.metaPillText, { color: C.TEXT_SECONDARY }]}>{stage}</Text>
          </View>
        </View>
      </View>

      {/* Organic section */}
      <View style={[styles.section, { backgroundColor: C.CARD_BG, borderColor: C.BORDER }]}>
        <Text style={[styles.sectionLabel, { color: C.TEXT_TERTIARY }]}>
          🌱 {t('treatment.organic').toUpperCase()}
        </Text>
        <View style={styles.tagRow}>
          {treatment.organic.map((item, i) => (
            <TreatmentTag key={i} label={item} type="organic" />
          ))}
        </View>
      </View>

      {/* Chemical section */}
      <View style={[styles.section, { backgroundColor: C.CARD_BG, borderColor: C.BORDER }]}>
        <Text style={[styles.sectionLabel, { color: C.TEXT_TERTIARY }]}>
          🧪 {t('treatment.chemical').toUpperCase()}
        </Text>
        <View style={styles.tagRow}>
          {treatment.chemical.map((item, i) => (
            <TreatmentTag key={i} label={item} type="chemical" />
          ))}
        </View>
      </View>

      {/* Dosage section */}
      <View style={[styles.section, { backgroundColor: C.CARD_BG, borderColor: C.BORDER }]}>
        <Text style={[styles.sectionLabel, { color: C.TEXT_TERTIARY }]}>
          📋 {t('treatment.dosage').toUpperCase()}
        </Text>
        <Text style={[styles.dosageText, { color: C.TEXT_PRIMARY }]}>
          {treatment.dosage}
        </Text>
      </View>

      {/* Action buttons */}
      <View style={styles.actionRow}>
        <TouchableOpacity
          style={[styles.actionBtn, { backgroundColor: C.LIGHT_BLUE, flex: 1 }]}
          activeOpacity={0.8}
        >
          <Text style={[styles.actionBtnText, { color: C.BLUE }]}>
            🏪 {t('treatment.findStore')}
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.actionBtn, { backgroundColor: C.LIGHT_PURPLE, flex: 1 }]}
          onPress={handleShare}
          activeOpacity={0.8}
        >
          <Text style={[styles.actionBtnText, { color: C.PURPLE }]}>
            📤 {t('treatment.shareHindi')}
          </Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  flex: { flex: 1 },
  scroll: { padding: Spacing.xl, gap: Spacing.md, paddingBottom: 40 },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: Spacing.xl },
  errorText: { ...Fonts.body, textAlign: 'center' },
  diseaseHeader: { borderRadius: BorderRadius.md, padding: Spacing.lg },
  diseaseName: { fontSize: 20, fontWeight: '600', marginBottom: Spacing.sm },
  metaRow: { flexDirection: 'row', gap: 8 },
  metaPill: { paddingHorizontal: 12, paddingVertical: 4, borderRadius: BorderRadius.pill },
  metaPillText: { ...Fonts.caption, color: '#fff', fontWeight: '500' },
  section: { borderRadius: BorderRadius.md, borderWidth: 0.5, padding: Spacing.lg },
  sectionLabel: { ...Fonts.caption, letterSpacing: 0.6, fontWeight: '500', marginBottom: Spacing.md },
  tagRow: { flexDirection: 'row', flexWrap: 'wrap', marginHorizontal: -4 },
  dosageText: { ...Fonts.body, lineHeight: 24 },
  actionRow: { flexDirection: 'row', gap: Spacing.md },
  actionBtn: { borderRadius: BorderRadius.sm, paddingVertical: 12, alignItems: 'center' },
  actionBtnText: { ...Fonts.label, fontWeight: '600' },
});

export default TreatmentScreen;
