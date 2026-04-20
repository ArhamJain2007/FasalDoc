import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  useColorScheme,
  Share,
  SafeAreaView,
  ActivityIndicator,
  Linking,
} from 'react-native';
import { useRoute, RouteProp } from '@react-navigation/native';
import { useTranslation } from 'react-i18next';

import { RootStackParamList } from '../navigation/AppNavigator';
import { getColors } from '../constants/colors';
import { BorderRadius, Fonts, Spacing } from '../constants/fonts';
import TreatmentTag from '../components/TreatmentTag';
import { getTreatment, TreatmentData } from '../services/api';
import { useHistoryStore } from '../store/useHistoryStore';
import { useLanguageStore } from '../store/useLanguageStore';

type RouteParams = RouteProp<RootStackParamList, 'TreatmentDetail'>;

const FALLBACK_TREATMENT: TreatmentData = {
  id: 'T000',
  diseaseName: 'General',
  cropName: 'General',
  organic: ['Neem oil spray', 'Copper fungicide', 'Trichoderma viride'],
  chemical: ['Mancozeb 75% WP', 'Chlorothalonil 75%', 'Dithane M-45'],
  dosage:
    'Apply every 7 days · 2.5g/L water · Avoid direct sunlight · Repeat 3× cycle · Wear PPE during application',
  description: 'Follow integrated pest management practices for best results.',
};

const TreatmentScreen: React.FC = () => {
  const scheme = useColorScheme();
  const C = getColors(scheme);
  const { t } = useTranslation();
  const route = useRoute<RouteParams>();
  const { scans } = useHistoryStore();
  const { language } = useLanguageStore();

  const params = route.params;
  const lastScan = scans[0];

  const treatmentId = params?.treatmentId ?? lastScan?.treatmentId ?? 'T000';
  const diseaseName = params?.diseaseName ?? lastScan?.diseaseName ?? '';
  const cropName = params?.cropName ?? lastScan?.cropName ?? '';
  const stage = params?.stage ?? lastScan?.stage ?? 'Stage 1';

  const [treatment, setTreatment] = useState<TreatmentData | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchTreatment();
  }, [treatmentId]);

  const fetchTreatment = async () => {
    setIsLoading(true);
    try {
      const data = await getTreatment(treatmentId);
      setTreatment(data);
    } catch {
      setTreatment(FALLBACK_TREATMENT);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFindStore = useCallback(() => {
    const query = encodeURIComponent('agricultural pesticide store near me');
    Linking.openURL(`https://maps.google.com/?q=${query}`);
  }, []);

  const handleShare = useCallback(async () => {
    if (!treatment) return;

    const text = [
      `🌿 FasalDoc — ${t('treatment.title')}`,
      `🦠 ${diseaseName} (${cropName})`,
      '',
      `✅ ${t('treatment.organic')}:`,
      ...(treatment.organic.map((o) => `• ${o}`)),
      '',
      `⚗️ ${t('treatment.chemical')}:`,
      ...(treatment.chemical.map((c) => `• ${c}`)),
      '',
      `📋 ${t('treatment.dosage')}:`,
      treatment.dosage,
    ].join('\n');

    await Share.share({ message: text, title: `FasalDoc — ${diseaseName}` });
  }, [treatment, diseaseName, cropName, language, t]);

  const stageColor =
    stage === 'Stage 1'
      ? { bg: C.LIGHT_GREEN, text: C.DARK_GREEN }
      : stage === 'Stage 2'
      ? { bg: C.LIGHT_AMBER, text: C.AMBER }
      : { bg: C.LIGHT_RED, text: C.RED };

  if (isLoading) {
    return (
      <SafeAreaView style={[styles.safeArea, { backgroundColor: C.GRAY_BG }]}>
        <View style={styles.loadingState}>
          <ActivityIndicator size="large" color={C.PRIMARY_GREEN} />
          <Text style={[styles.loadingText, { color: C.TEXT_SECONDARY }]}>
            {t('common.loading')}
          </Text>
        </View>
      </SafeAreaView>
    );
  }

  const data = treatment ?? FALLBACK_TREATMENT;

  return (
    <SafeAreaView style={[styles.safeArea, { backgroundColor: C.GRAY_BG }]}>
      <ScrollView
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.headerSection}>
          <Text style={[styles.title, { color: C.TEXT_PRIMARY }]}>
            {t('treatment.title')}
          </Text>
          {diseaseName ? (
            <View style={styles.metaRow}>
              <Text style={[styles.diseaseLabel, { color: C.TEXT_SECONDARY }]}>
                {diseaseName} · {cropName}
              </Text>
              <View style={[styles.stagePill, { backgroundColor: stageColor.bg }]}>
                <Text style={[styles.stageText, { color: stageColor.text }]}>{stage}</Text>
              </View>
            </View>
          ) : null}
        </View>

        {/* Organic options */}
        <View style={[styles.section, { backgroundColor: C.CARD_BG, borderColor: C.BORDER }]}>
          <Text style={[styles.sectionTitle, { color: C.DARK_GREEN }]}>
            🌱 {t('treatment.organic')}
          </Text>
          <View style={styles.tagsWrap}>
            {data.organic.map((tag) => (
              <TreatmentTag key={tag} label={tag} type="organic" />
            ))}
          </View>
        </View>

        {/* Chemical pesticides */}
        <View style={[styles.section, { backgroundColor: C.CARD_BG, borderColor: C.BORDER }]}>
          <Text style={[styles.sectionTitle, { color: C.AMBER }]}>
            ⚗️ {t('treatment.chemical')}
          </Text>
          <View style={styles.tagsWrap}>
            {data.chemical.map((tag) => (
              <TreatmentTag key={tag} label={tag} type="chemical" />
            ))}
          </View>
        </View>

        {/* Dosage */}
        <View style={[styles.section, { backgroundColor: C.CARD_BG, borderColor: C.BORDER }]}>
          <Text style={[styles.sectionTitle, { color: C.TEXT_PRIMARY }]}>
            📋 {t('treatment.dosage')}
          </Text>
          <Text style={[styles.dosageText, { color: C.TEXT_SECONDARY }]}>{data.dosage}</Text>
        </View>

        {/* Warning */}
        <View style={[styles.warning, { backgroundColor: C.LIGHT_AMBER, borderColor: C.AMBER }]}>
          <Text style={[styles.warningText, { color: C.AMBER }]}>
            ⚠️ Always wear PPE. Follow label directions. Consult local extension officer before first use.
          </Text>
        </View>

        {/* Action buttons */}
        <View style={styles.actionRow}>
          <TouchableOpacity
            style={[styles.actionBtn, { backgroundColor: C.LIGHT_BLUE }]}
            onPress={handleFindStore}
            activeOpacity={0.8}
          >
            <Text style={[styles.actionBtnText, { color: C.BLUE }]}>
              🏪 {t('treatment.findStore')}
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.actionBtn, { backgroundColor: C.LIGHT_PURPLE }]}
            onPress={handleShare}
            activeOpacity={0.8}
          >
            <Text style={[styles.actionBtnText, { color: C.PURPLE }]}>
              📤 {t('treatment.shareHindi')}
            </Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: { flex: 1 },
  content: {
    padding: Spacing.lg,
    gap: Spacing.md,
    paddingBottom: Spacing.xxxl,
  },
  loadingState: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    gap: Spacing.md,
  },
  loadingText: {
    ...Fonts.body,
  },
  headerSection: {
    gap: Spacing.xs,
  },
  title: {
    ...Fonts.heading,
  },
  metaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  diseaseLabel: {
    ...Fonts.caption,
    flex: 1,
  },
  stagePill: {
    paddingHorizontal: 10,
    paddingVertical: 3,
    borderRadius: BorderRadius.pill,
  },
  stageText: {
    fontSize: 11,
    fontWeight: '500',
  },
  section: {
    borderRadius: BorderRadius.md,
    borderWidth: 0.5,
    padding: Spacing.md,
    gap: Spacing.sm,
  },
  sectionTitle: {
    ...Fonts.subheading,
  },
  tagsWrap: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    margin: -4,
  },
  dosageText: {
    fontSize: 13,
    lineHeight: 22,
  },
  warning: {
    borderRadius: BorderRadius.sm,
    borderWidth: 0.5,
    padding: Spacing.md,
  },
  warningText: {
    ...Fonts.caption,
    lineHeight: 18,
  },
  actionRow: {
    flexDirection: 'row',
    gap: Spacing.sm,
    marginTop: Spacing.sm,
  },
  actionBtn: {
    flex: 1,
    borderRadius: BorderRadius.pill,
    paddingVertical: 12,
    alignItems: 'center',
  },
  actionBtnText: {
    ...Fonts.label,
  },
});

export default TreatmentScreen;
