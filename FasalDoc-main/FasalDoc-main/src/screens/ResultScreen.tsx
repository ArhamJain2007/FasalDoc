import React, { useCallback, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Image,
  TouchableOpacity,
  useColorScheme,
  Alert,
  FlatList,
  SafeAreaView,
} from 'react-native';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useTranslation } from 'react-i18next';

import { RootStackParamList } from '../navigation/AppNavigator';
import { getColors } from '../constants/colors';
import { BorderRadius, Fonts, Spacing } from '../constants/fonts';
import ConfidenceBar from '../components/ConfidenceBar';
import DiseaseCard from '../components/DiseaseCard';
import { useHistoryStore } from '../store/useHistoryStore';
import { DISEASE_CLASSES, getDiseaseName } from '../constants/diseases';

type RouteParams = RouteProp<RootStackParamList, 'Result'>;
type NavProp = NativeStackNavigationProp<RootStackParamList>;

const STAGE_COLORS = (C: ReturnType<typeof getColors>) => ({
  'Stage 1': { bg: C.LIGHT_GREEN, text: C.DARK_GREEN },
  'Stage 2': { bg: C.LIGHT_AMBER, text: C.AMBER },
  'Stage 3': { bg: C.LIGHT_RED, text: C.RED },
});

const ResultScreen: React.FC = () => {
  const scheme = useColorScheme();
  const C = getColors(scheme);
  const { t } = useTranslation();
  const navigation = useNavigation<NavProp>();
  const route = useRoute<RouteParams>();
  const { updateStatus } = useHistoryStore();

  const {
    diseaseName,
    confidence,
    cropName,
    stage,
    imageUri,
    scanDate,
    treatmentId,
    description,
    severity,
    scanId,
  } = route.params;

  const [saved, setSaved] = useState(false);

  const stageColors = STAGE_COLORS(C);
  const stageColor = stageColors[stage as keyof typeof stageColors] ?? stageColors['Stage 1'];

  const severityColor =
    severity === 'high'
      ? C.RED
      : severity === 'medium'
      ? C.AMBER
      : C.PRIMARY_GREEN;

  const formattedDate = new Date(scanDate).toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });

  const relatedDiseases = DISEASE_CLASSES.filter(
    (d) => d.cropName === cropName && getDiseaseName(d.label) !== diseaseName,
  ).slice(0, 3);

  const handleViewTreatment = useCallback(() => {
    navigation.navigate('TreatmentDetail', {
      treatmentId,
      diseaseName,
      cropName,
      stage,
    });
  }, [navigation, treatmentId, diseaseName, cropName, stage]);

  const handleSaveHistory = useCallback(async () => {
    if (saved) return;
    try {
      await updateStatus(scanId, 'active');
      setSaved(true);
      Alert.alert('✓', t('result.saved'));
    } catch {
      Alert.alert(t('common.error'), t('common.retry'));
    }
  }, [saved, scanId, updateStatus, t]);

  return (
    <SafeAreaView style={[styles.safeArea, { backgroundColor: C.GRAY_BG }]}>
      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Leaf image */}
        <Image
          source={{ uri: imageUri }}
          style={styles.heroImage}
          resizeMode="cover"
        />

        {/* Back button */}
        <TouchableOpacity
          style={[styles.backBtn, { backgroundColor: C.CARD_BG }]}
          onPress={() => navigation.goBack()}
          activeOpacity={0.8}
        >
          <Text style={{ fontSize: 16 }}>←</Text>
        </TouchableOpacity>

        {/* Floating card */}
        <View style={[styles.floatingCard, { backgroundColor: C.CARD_BG }]}>
          {/* Disease name */}
          <Text style={[styles.diseaseName, { color: C.TEXT_PRIMARY }]}>
            {diseaseName}
          </Text>

          {/* Pill row */}
          <View style={styles.pillRow}>
            <View style={[styles.pill, { backgroundColor: C.LIGHT_GREEN }]}>
              <Text style={[styles.pillText, { color: C.DARK_GREEN }]}>{cropName}</Text>
            </View>
            <View style={[styles.pill, { backgroundColor: stageColor.bg }]}>
              <Text style={[styles.pillText, { color: stageColor.text }]}>
                {t('result.stage')} {stage.split(' ')[1]}
              </Text>
            </View>
            <View style={[styles.pill, { backgroundColor: C.GRAY_BG }]}>
              <Text style={[styles.pillText, { color: C.TEXT_SECONDARY }]}>
                {formattedDate}
              </Text>
            </View>
          </View>

          {/* Confidence */}
          <ConfidenceBar value={confidence} />

          {/* Description */}
          {description ? (
            <View style={styles.section}>
              <Text style={[styles.sectionLabel, { color: C.TEXT_SECONDARY }]}>
                {t('result.description')}
              </Text>
              <Text style={[styles.description, { color: C.TEXT_PRIMARY }]}>
                {description}
              </Text>
            </View>
          ) : null}

          {/* Severity */}
          <View style={styles.severityRow}>
            <Text style={[styles.sectionLabel, { color: C.TEXT_SECONDARY }]}>
              {t('result.severity')}
            </Text>
            <View style={styles.severityIndicator}>
              <View style={[styles.severityDot, { backgroundColor: severityColor }]} />
              <Text style={[styles.severityText, { color: severityColor }]}>
                {t(`result.${severity ?? 'medium'}`)}
              </Text>
            </View>
          </View>

          {/* CTA buttons */}
          <TouchableOpacity
            style={[styles.primaryBtn, { backgroundColor: C.PRIMARY_GREEN }]}
            onPress={handleViewTreatment}
            activeOpacity={0.85}
          >
            <Text style={[styles.primaryBtnText, { color: C.WHITE }]}>
              {t('result.viewTreatment')}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.outlineBtn,
              { borderColor: saved ? C.TEXT_TERTIARY : C.PRIMARY_GREEN },
            ]}
            onPress={handleSaveHistory}
            activeOpacity={0.85}
            disabled={saved}
          >
            <Text
              style={[
                styles.outlineBtnText,
                { color: saved ? C.TEXT_TERTIARY : C.PRIMARY_GREEN },
              ]}
            >
              {saved ? `✓ ${t('result.saved')}` : t('result.saveHistory')}
            </Text>
          </TouchableOpacity>

          {/* Related diseases */}
          {relatedDiseases.length > 0 && (
            <View style={styles.relatedSection}>
              <Text style={[styles.sectionLabel, { color: C.TEXT_SECONDARY }]}>
                {t('result.relatedDiseases')}
              </Text>
              <FlatList
                data={relatedDiseases}
                horizontal
                showsHorizontalScrollIndicator={false}
                keyExtractor={(item) => String(item.id)}
                renderItem={({ item }) => (
                  <DiseaseCard
                    diseaseName={getDiseaseName(item.label)}
                    cropName={item.cropName}
                    confidence={Math.floor(Math.random() * 30) + 55}
                  />
                )}
                style={{ marginTop: Spacing.sm }}
              />
            </View>
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: { flex: 1 },
  heroImage: {
    width: '100%',
    height: 220,
  },
  backBtn: {
    position: 'absolute',
    top: Spacing.lg,
    left: Spacing.lg,
    width: 36,
    height: 36,
    borderRadius: 18,
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 10,
    elevation: 4,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.12,
    shadowRadius: 4,
  },
  floatingCard: {
    marginTop: -24,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: Spacing.xl,
    minHeight: 500,
    gap: Spacing.md,
  },
  diseaseName: {
    fontSize: 20,
    fontWeight: '500',
    lineHeight: 28,
  },
  pillRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.xs,
  },
  pill: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: BorderRadius.pill,
  },
  pillText: {
    fontSize: 12,
    fontWeight: '500',
  },
  section: {
    gap: 4,
  },
  sectionLabel: {
    ...Fonts.caption,
    fontWeight: '500',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 2,
  },
  description: {
    ...Fonts.body,
  },
  severityRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  severityIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  severityDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  severityText: {
    ...Fonts.label,
  },
  primaryBtn: {
    borderRadius: BorderRadius.sm,
    paddingVertical: 14,
    alignItems: 'center',
    marginTop: Spacing.sm,
  },
  primaryBtnText: {
    ...Fonts.subheading,
  },
  outlineBtn: {
    borderRadius: BorderRadius.sm,
    paddingVertical: 13,
    alignItems: 'center',
    borderWidth: 1.5,
  },
  outlineBtnText: {
    ...Fonts.subheading,
  },
  relatedSection: {
    marginTop: Spacing.md,
  },
});

export default ResultScreen;
