import React, { useCallback } from 'react';
import {
  View, Text, StyleSheet, ScrollView, Image,
  TouchableOpacity, useColorScheme, Alert,
} from 'react-native';
import { useTranslation } from 'react-i18next';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import type { RootStackParamList } from '../navigation/AppNavigator';
import { getColors } from '../constants/colors';
import { BorderRadius, Fonts, Spacing } from '../constants/fonts';
import ConfidenceBar from '../components/ConfidenceBar';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';

type RouteProps = RouteProp<RootStackParamList, 'Result'>;
type NavProp = NativeStackNavigationProp<RootStackParamList, 'Result'>;

const ResultScreen: React.FC = () => {
  const scheme = useColorScheme();
  const C = getColors(scheme);
  const { t } = useTranslation();
  const route = useRoute<RouteProps>();
  const navigation = useNavigation<NavProp>();

  const { result, imageUri } = route.params;

  const severityColor =
    result.severity === 'high'
      ? C.RED
      : result.severity === 'medium'
      ? C.AMBER
      : C.PRIMARY_GREEN;

  const stageColor =
    result.stage === 'Stage 3'
      ? C.LIGHT_RED
      : result.stage === 'Stage 2'
      ? C.LIGHT_AMBER
      : C.LIGHT_GREEN;

  const handleViewTreatment = useCallback(() => {
    navigation.navigate('Treatment', {
      treatmentId: result.treatmentId,
      diseaseName: result.diseaseName,
      cropName: result.cropName,
      stage: result.stage,
    });
  }, [navigation, result]);

  const handleSaveHistory = useCallback(() => {
    Alert.alert('Saved', t('result.saved'));
  }, [t]);

  return (
    <ScrollView
      style={[styles.flex, { backgroundColor: C.GRAY_BG }]}
      showsVerticalScrollIndicator={false}
    >
      {/* Leaf image */}
      {imageUri ? (
        <Image source={{ uri: imageUri }} style={styles.heroImage} resizeMode="cover" />
      ) : (
        <View style={[styles.heroImage, { backgroundColor: C.LIGHT_GREEN, alignItems: 'center', justifyContent: 'center' }]}>
          <Text style={{ fontSize: 64 }}>🌿</Text>
        </View>
      )}

      {/* Floating card */}
      <View style={[styles.card, { backgroundColor: C.CARD_BG }]}>

        {/* Disease name + stage */}
        <Text style={[styles.diseaseName, { color: C.TEXT_PRIMARY }]}>
          {result.diseaseName}
        </Text>
        <View style={styles.pillRow}>
          <View style={[styles.pill, { backgroundColor: C.LIGHT_GREEN }]}>
            <Text style={[styles.pillText, { color: C.DARK_GREEN }]}>{result.cropName}</Text>
          </View>
          <View style={[styles.pill, { backgroundColor: stageColor }]}>
            <Text style={[styles.pillText, { color: C.TEXT_PRIMARY }]}>{result.stage}</Text>
          </View>
          <View style={[styles.pill, { backgroundColor: C.GRAY_BG }]}>
            <Text style={[styles.pillText, { color: C.TEXT_SECONDARY }]}>
              {new Date(result.scan_date ?? Date.now()).toLocaleDateString('en-IN')}
            </Text>
          </View>
        </View>

        {/* Confidence */}
        <ConfidenceBar value={result.confidence} />

        {/* Severity */}
        <View style={[styles.severityRow, { backgroundColor: C.GRAY_BG, borderRadius: BorderRadius.sm }]}>
          <Text style={[styles.severityLabel, { color: C.TEXT_SECONDARY }]}>
            {t('result.severity')}
          </Text>
          <View style={styles.severityRight}>
            <View style={[styles.severityDot, { backgroundColor: severityColor }]} />
            <Text style={[styles.severityValue, { color: severityColor }]}>
              {t(`result.${result.severity}`)}
            </Text>
          </View>
        </View>

        {/* Description */}
        {result.description ? (
          <View style={styles.section}>
            <Text style={[styles.sectionLabel, { color: C.TEXT_TERTIARY }]}>
              {t('result.description').toUpperCase()}
            </Text>
            <Text style={[styles.description, { color: C.TEXT_PRIMARY }]}>
              {result.description}
            </Text>
          </View>
        ) : null}

        {/* CTAs */}
        <TouchableOpacity
          style={[styles.primaryBtn, { backgroundColor: C.PRIMARY_GREEN }]}
          onPress={handleViewTreatment}
          activeOpacity={0.85}
        >
          <Text style={styles.primaryBtnText}>{t('result.viewTreatment')}</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.secondaryBtn, { borderColor: C.PRIMARY_GREEN }]}
          onPress={handleSaveHistory}
          activeOpacity={0.85}
        >
          <Text style={[styles.secondaryBtnText, { color: C.PRIMARY_GREEN }]}>
            {t('result.saveHistory')}
          </Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  flex: { flex: 1 },
  heroImage: { width: '100%', height: 240 },
  card: {
    borderTopLeftRadius: 20, borderTopRightRadius: 20,
    marginTop: -20, padding: Spacing.xl, paddingBottom: 40,
  },
  diseaseName: { fontSize: 22, fontWeight: '600', marginBottom: Spacing.md },
  pillRow: { flexDirection: 'row', gap: 8, flexWrap: 'wrap', marginBottom: Spacing.md },
  pill: { paddingHorizontal: 12, paddingVertical: 4, borderRadius: BorderRadius.pill },
  pillText: { ...Fonts.caption, fontWeight: '500' },
  severityRow: {
    flexDirection: 'row', justifyContent: 'space-between',
    alignItems: 'center', padding: Spacing.md, marginVertical: Spacing.md,
  },
  severityLabel: { ...Fonts.body },
  severityRight: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  severityDot: { width: 8, height: 8, borderRadius: 4 },
  severityValue: { ...Fonts.body, fontWeight: '500' },
  section: { marginBottom: Spacing.lg },
  sectionLabel: { ...Fonts.caption, letterSpacing: 0.6, marginBottom: 6 },
  description: { ...Fonts.body, lineHeight: 22 },
  primaryBtn: {
    borderRadius: BorderRadius.sm, paddingVertical: 14,
    alignItems: 'center', marginBottom: Spacing.md,
  },
  primaryBtnText: { ...Fonts.subheading, color: '#fff', fontWeight: '600' },
  secondaryBtn: {
    borderRadius: BorderRadius.sm, paddingVertical: 13,
    alignItems: 'center', borderWidth: 1.5,
  },
  secondaryBtnText: { ...Fonts.subheading, fontWeight: '600' },
});

export default ResultScreen;
