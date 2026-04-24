import React, { useState, useCallback } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  Image, ActivityIndicator, Alert, useColorScheme,
} from 'react-native';
import { useTranslation } from 'react-i18next';
import * as ImagePicker from 'expo-image-picker';
import * as Network from 'expo-network';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import * as Crypto from 'expo-crypto';

import { detectDisease } from '../services/api';
import { useHistoryStore } from '../store/useHistoryStore';
import { useLanguageStore } from '../store/useLanguageStore';
import { getColors } from '../constants/colors';
import { BorderRadius, Fonts, Spacing } from '../constants/fonts';
import LanguageSwitcher from '../components/LanguageSwitcher';
import OfflineBanner from '../components/OfflineBanner';
import ScanButton from '../components/ScanButton';
import ConfidenceBar from '../components/ConfidenceBar';
import type { RootStackParamList } from '../navigation/AppNavigator';

type NavProp = NativeStackNavigationProp<RootStackParamList, 'MainTabs'>;

const ScanScreen: React.FC = () => {
  const scheme = useColorScheme();
  const C = getColors(scheme);
  const { t } = useTranslation();
  const navigation = useNavigation<NavProp>();
  const { addScan } = useHistoryStore();
  const { language } = useLanguageStore();

  const [imageUri, setImageUri] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isOffline, setIsOffline] = useState(false);
  const [result, setResult] = useState<any>(null);

  // ─── Check connectivity ───────────────────────────────────────────────────
  const checkNetwork = useCallback(async () => {
    try {
      const net = await Network.getNetworkStateAsync();
      setIsOffline(!net.isConnected || !net.isInternetReachable);
    } catch {
      setIsOffline(false);
    }
  }, []);

  // ─── Open camera ──────────────────────────────────────────────────────────
  const handleCamera = useCallback(async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission needed', 'Camera access is required to scan leaves.');
      return;
    }
    const res = await ImagePicker.launchCameraAsync({
      mediaTypes: ['images'],
      quality: 0.85,
      allowsEditing: true,
      aspect: [1, 1],
    });
    if (!res.canceled && res.assets[0]) {
      setImageUri(res.assets[0].uri);
      setResult(null);
    }
  }, []);

  // ─── Open gallery ─────────────────────────────────────────────────────────
  const handleGallery = useCallback(async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission needed', 'Gallery access is required.');
      return;
    }
    const res = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      quality: 0.85,
      allowsEditing: true,
      aspect: [1, 1],
    });
    if (!res.canceled && res.assets[0]) {
      setImageUri(res.assets[0].uri);
      setResult(null);
    }
  }, []);

  // ─── Analyze image ────────────────────────────────────────────────────────
  const handleAnalyze = useCallback(async () => {
    if (!imageUri) return;
    await checkNetwork();
    setIsAnalyzing(true);
    setResult(null);

    try {
      const data = await detectDisease(imageUri, language);
      setResult(data);

      // Save to local DB
      const scanId = await Crypto.randomUUIDAsync();
      const record = {
        id: scanId,
        diseaseName: data.diseaseName,
        cropName: data.cropName,
        confidence: data.confidence,
        stage: data.stage,
        imageUri,
        scanDate: new Date().toISOString(),
        status: 'active' as const,
        treatmentId: data.treatmentId,
        synced: 0 as const,
        description: data.description,
        severity: data.severity,
      };
      await addScan(record);
    } catch (err: any) {
      const msg =
        err?.response?.data?.message ??
        'Could not analyze the image. Please check your connection and try again.';
      Alert.alert('Analysis failed', msg);
    } finally {
      setIsAnalyzing(false);
    }
  }, [imageUri, language, checkNetwork, addScan]);

  // ─── Navigate to result ───────────────────────────────────────────────────
  const handleSeeReport = () => {
    if (!result) return;
    navigation.navigate('Result', { result, imageUri: imageUri! });
  };

  return (
    <View style={[styles.flex, { backgroundColor: C.GRAY_BG }]}>
      <OfflineBanner isOffline={isOffline} />

      <ScrollView
        contentContainerStyle={styles.scroll}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
      >
        {/* Header */}
        <View style={styles.headerRow}>
          <Text style={[styles.appName, { color: C.TEXT_PRIMARY }]}>
            🌿 {t('app.name')}
          </Text>
          <LanguageSwitcher />
        </View>

        {/* Scan area */}
        <View
          style={[
            styles.scanArea,
            {
              borderColor: imageUri ? C.PRIMARY_GREEN : '#9FE1CB',
              backgroundColor: C.CARD_BG,
            },
          ]}
        >
          {imageUri ? (
            <Image source={{ uri: imageUri }} style={styles.previewImage} resizeMode="cover" />
          ) : (
            <View style={styles.placeholder}>
              <Text style={styles.leafEmoji}>🌿</Text>
              <Text style={[styles.placeholderText, { color: C.TEXT_SECONDARY }]}>
                {t('scan.placeholder')}
              </Text>
            </View>
          )}
        </View>

        {/* Camera / Gallery buttons */}
        <View style={styles.btnRow}>
          <ScanButton
            label={t('scan.cameraBtn')}
            icon="📷"
            variant="primary"
            onPress={handleCamera}
            style={styles.halfBtn}
          />
          <ScanButton
            label={t('scan.galleryBtn')}
            icon="🖼️"
            variant="secondary"
            onPress={handleGallery}
            style={styles.halfBtn}
          />
        </View>

        {/* Offline badge */}
        {isOffline && (
          <View style={[styles.offlinePill, { backgroundColor: C.LIGHT_AMBER }]}>
            <Text style={[styles.offlinePillText, { color: C.AMBER }]}>
              Offline ready
            </Text>
          </View>
        )}

        {/* Analyze button */}
        {imageUri && !result && (
          <TouchableOpacity
            style={[
              styles.analyzeBtn,
              { backgroundColor: C.PRIMARY_GREEN, opacity: isAnalyzing ? 0.7 : 1 },
            ]}
            onPress={handleAnalyze}
            disabled={isAnalyzing}
            activeOpacity={0.85}
          >
            {isAnalyzing ? (
              <View style={styles.analyzeLoading}>
                <ActivityIndicator color="#fff" size="small" />
                <Text style={styles.analyzeBtnText}>{t('scan.analyzing')}</Text>
              </View>
            ) : (
              <Text style={styles.analyzeBtnText}>{t('scan.analyzeBtn')}</Text>
            )}
          </TouchableOpacity>
        )}

        {/* Quick result strip */}
        {result && (
          <View
            style={[
              styles.resultStrip,
              { backgroundColor: C.LIGHT_GREEN, borderColor: C.PRIMARY_GREEN },
            ]}
          >
            <View style={styles.resultHeader}>
              <Text style={[styles.resultDisease, { color: C.DARK_GREEN }]}>
                {result.diseaseName}
              </Text>
              <View style={[styles.stagePill, { backgroundColor: C.PRIMARY_GREEN }]}>
                <Text style={styles.stageText}>{result.stage}</Text>
              </View>
            </View>
            <Text style={[styles.resultCrop, { color: C.TEXT_SECONDARY }]}>
              {result.cropName}
            </Text>
            <ConfidenceBar value={result.confidence} />

            <TouchableOpacity
              style={[styles.reportBtn, { backgroundColor: C.PRIMARY_GREEN }]}
              onPress={handleSeeReport}
              activeOpacity={0.85}
            >
              <Text style={styles.reportBtnText}>{t('scan.seeReport')}</Text>
            </TouchableOpacity>
          </View>
        )}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  flex: { flex: 1 },
  scroll: { padding: Spacing.xl, paddingTop: Spacing.lg },
  headerRow: {
    flexDirection: 'row', justifyContent: 'space-between',
    alignItems: 'center', marginBottom: Spacing.xl,
  },
  appName: { ...Fonts.heading, fontSize: 20, fontWeight: '600' },
  scanArea: {
    borderWidth: 1.5, borderStyle: 'dashed', borderRadius: 16,
    overflow: 'hidden', marginBottom: Spacing.lg, minHeight: 220,
    alignItems: 'center', justifyContent: 'center',
  },
  placeholder: { alignItems: 'center', padding: Spacing.xxxl },
  leafEmoji: { fontSize: 56, marginBottom: Spacing.md },
  placeholderText: { ...Fonts.body, textAlign: 'center' },
  previewImage: { width: '100%', height: 260 },
  btnRow: { flexDirection: 'row', gap: Spacing.md, marginBottom: Spacing.md },
  halfBtn: { flex: 1 },
  offlinePill: {
    alignSelf: 'center', paddingHorizontal: 12, paddingVertical: 4,
    borderRadius: BorderRadius.pill, marginBottom: Spacing.md,
  },
  offlinePillText: { ...Fonts.caption, fontWeight: '500' },
  analyzeBtn: {
    borderRadius: BorderRadius.sm, paddingVertical: 14,
    alignItems: 'center', marginBottom: Spacing.lg,
  },
  analyzeLoading: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  analyzeBtnText: { ...Fonts.subheading, color: '#fff', fontWeight: '600' },
  resultStrip: {
    borderRadius: BorderRadius.md, borderWidth: 1,
    padding: Spacing.lg, marginBottom: Spacing.lg,
  },
  resultHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 },
  resultDisease: { ...Fonts.subheading, flex: 1 },
  stagePill: { paddingHorizontal: 10, paddingVertical: 3, borderRadius: BorderRadius.pill },
  stageText: { ...Fonts.caption, color: '#fff', fontWeight: '600' },
  resultCrop: { ...Fonts.caption, marginBottom: Spacing.sm },
  reportBtn: { borderRadius: BorderRadius.sm, paddingVertical: 12, alignItems: 'center', marginTop: Spacing.md },
  reportBtnText: { ...Fonts.label, color: '#fff', fontWeight: '600' },
});

export default ScanScreen;
