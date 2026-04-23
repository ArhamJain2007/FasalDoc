import React, { useState, useCallback, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Image,
  TouchableOpacity,
  useColorScheme,
  ActivityIndicator,
  Alert,
  SafeAreaView,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useTranslation } from 'react-i18next';
import * as ImagePicker from 'expo-image-picker';
import * as Network from 'expo-network';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withRepeat,
  withTiming,
  withSequence,
} from 'react-native-reanimated';
import * as Crypto from 'expo-crypto';

import { RootStackParamList } from '../navigation/AppNavigator';
import { getColors } from '../constants/colors';
import { BorderRadius, Fonts, Spacing } from '../constants/fonts';
import LanguageSwitcher from '../components/LanguageSwitcher';
import OfflineBanner from '../components/OfflineBanner';
import ScanButton from '../components/ScanButton';
import DiseaseCard from '../components/DiseaseCard';
import { detectDisease } from '../services/api';
// import { runInference } from '../services/tflite';
const runInference = async () => { throw new Error('Use online mode'); };
import { useHistoryStore, ScanRecord } from '../store/useHistoryStore';

type NavProp = NativeStackNavigationProp<RootStackParamList, 'MainTabs'>;

const ScanScreen: React.FC = () => {
  const scheme = useColorScheme();
  const C = getColors(scheme);
  const { t } = useTranslation();
  const navigation = useNavigation<NavProp>();
  const { addScan } = useHistoryStore();

  const [imageUri, setImageUri] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isOffline, setIsOffline] = useState(false);
  const [result, setResult] = useState<ScanRecord | null>(null);

  const spinnerOpacity = useSharedValue(1);
  const spinnerScale = useSharedValue(1);

  useEffect(() => {
    let isMounted = true;
    const checkNetwork = async () => {
      const state = await Network.getNetworkStateAsync();
      if (isMounted) setIsOffline(!state.isConnected);
    };
    checkNetwork();
    const sub = require('react-native').AppState.addEventListener('change', (next: string) => {
      if (next === 'active') checkNetwork();
    });
    return () => { isMounted = false; sub.remove(); };
  }, []);

  useEffect(() => {
    if (isAnalyzing) {
      spinnerOpacity.value = withRepeat(
        withSequence(withTiming(0.3, { duration: 600 }), withTiming(1, { duration: 600 })),
        -1,
        false,
      );
      spinnerScale.value = withRepeat(
        withSequence(withTiming(1.1, { duration: 600 }), withTiming(1, { duration: 600 })),
        -1,
        false,
      );
    } else {
      spinnerOpacity.value = withTiming(1);
      spinnerScale.value = withTiming(1);
    }
  }, [isAnalyzing]);

  const pulseStyle = useAnimatedStyle(() => ({
    opacity: spinnerOpacity.value,
    transform: [{ scale: spinnerScale.value }],
  }));

  const handleCamera = useCallback(async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') return;
    const response = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.85,
    });
    if (!response.canceled && response.assets?.[0]?.uri) {
      setImageUri(response.assets[0].uri);
      setResult(null);
    }
  }, []);

  const handleGallery = useCallback(async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') return;
    const response = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.85,
    });
    if (!response.canceled && response.assets?.[0]?.uri) {
      setImageUri(response.assets[0].uri);
      setResult(null);
    }
  }, []);

  const handleAnalyze = useCallback(async () => {
    if (!imageUri) return;
    setIsAnalyzing(true);
    setResult(null);

    try {
      let detected;
      if (isOffline) {
        const inference = await runInference(imageUri);
        detected = {
          diseaseName: inference.diseaseName,
          confidence: inference.confidence,
          cropName: inference.cropName,
          stage: inference.stage,
          treatmentId: inference.treatmentId,
          description: '',
          severity: inference.severity,
        };
      } else {
        detected = await detectDisease(imageUri);
      }

      const record: ScanRecord = {
        id: Crypto.randomUUID(),
        diseaseName: detected.diseaseName,
        cropName: detected.cropName,
        confidence: detected.confidence,
        stage: detected.stage,
        imageUri,
        scanDate: new Date().toISOString(),
        status: 'active',
        treatmentId: detected.treatmentId,
        synced: isOffline ? 0 : 1,
        description: detected.description,
        severity: detected.severity as 'low' | 'medium' | 'high',
      };

      await addScan(record);
      setResult(record);
    } catch (err) {
      Alert.alert(t('common.error'), t('common.retry'));
    } finally {
      setIsAnalyzing(false);
    }
  }, [imageUri, isOffline, addScan, t]);

  const handleSeeReport = useCallback(() => {
    if (!result) return;
    navigation.navigate('Result', {
      diseaseName: result.diseaseName,
      confidence: result.confidence,
      cropName: result.cropName,
      stage: result.stage,
      imageUri: result.imageUri,
      scanDate: result.scanDate,
      treatmentId: result.treatmentId,
      description: result.description,
      severity: result.severity,
      scanId: result.id,
    });
  }, [result, navigation]);

  return (
    <SafeAreaView style={[styles.safeArea, { backgroundColor: C.GRAY_BG }]}>
      <OfflineBanner isOffline={isOffline} />

      <ScrollView
        style={{ flex: 1 }}
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={[styles.appName, { color: C.TEXT_PRIMARY }]}>
            {t('app.name')}
          </Text>
          <LanguageSwitcher />
        </View>

        {/* Scan Area */}
        <View
          style={[
            styles.scanZone,
            {
              borderColor: C.PRIMARY_GREEN,
              backgroundColor: imageUri ? C.CARD_BG : C.LIGHT_GREEN,
            },
          ]}
        >
          {imageUri ? (
            <Image
              source={{ uri: imageUri }}
              style={styles.previewImage}
              resizeMode="cover"
            />
          ) : (
            <>
              <Text style={styles.scanIcon}>🌿</Text>
              <Text style={[styles.scanPlaceholder, { color: C.DARK_GREEN }]}>
                {t('scan.placeholder')}
              </Text>
            </>
          )}
        </View>

        {/* Buttons row */}
        <View style={styles.buttonRow}>
          <ScanButton
            label={t('scan.cameraBtn')}
            icon="📷"
            variant="primary"
            onPress={handleCamera}
            style={{ flex: 1 }}
          />
          <ScanButton
            label={t('scan.galleryBtn')}
            icon="🖼"
            variant="secondary"
            onPress={handleGallery}
            style={{ flex: 1 }}
          />
        </View>

        {/* Analyze button */}
        {imageUri && !result && (
          <TouchableOpacity
            style={[
              styles.analyzeBtn,
              {
                backgroundColor: isAnalyzing ? C.LIGHT_GREEN : C.PRIMARY_GREEN,
                opacity: isAnalyzing ? 0.8 : 1,
              },
            ]}
            onPress={handleAnalyze}
            disabled={isAnalyzing}
            activeOpacity={0.8}
          >
            {isAnalyzing ? (
              <Animated.View style={[styles.loadingRow, pulseStyle]}>
                <ActivityIndicator color={C.PRIMARY_GREEN} size="small" />
                <Text style={[styles.analyzeBtnText, { color: C.DARK_GREEN }]}>
                  {t('scan.analyzing')}
                </Text>
              </Animated.View>
            ) : (
              <Text style={[styles.analyzeBtnText, { color: C.WHITE }]}>
                {t('scan.analyzeBtn')}
              </Text>
            )}
          </TouchableOpacity>
        )}

        {/* Quick result strip */}
        {result && (
          <View style={styles.resultStrip}>
            <Text style={[styles.resultReady, { color: C.TEXT_SECONDARY }]}>
              ✓ {t('scan.resultReady')}
            </Text>
            <DiseaseCard
              diseaseName={result.diseaseName}
              cropName={result.cropName}
              confidence={result.confidence}
              status={result.status}
              imageUri={result.imageUri}
              onPress={handleSeeReport}
            />
            <TouchableOpacity
              style={[styles.reportBtn, { backgroundColor: C.PRIMARY_GREEN }]}
              onPress={handleSeeReport}
              activeOpacity={0.85}
            >
              <Text style={[styles.reportBtnText, { color: C.WHITE }]}>
                {t('scan.seeReport')}
              </Text>
            </TouchableOpacity>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
  },
  content: {
    padding: Spacing.lg,
    gap: Spacing.lg,
    paddingBottom: Spacing.xxxl,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  appName: {
    ...Fonts.heading,
  },
  scanZone: {
    borderWidth: 1.5,
    borderStyle: 'dashed',
    borderRadius: 16,
    minHeight: 200,
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
    gap: Spacing.md,
    padding: Spacing.xl,
  },
  scanIcon: {
    fontSize: 64,
  },
  scanPlaceholder: {
    ...Fonts.body,
    textAlign: 'center',
    fontWeight: '500',
  },
  previewImage: {
    width: '100%',
    height: 220,
    borderRadius: 12,
  },
  buttonRow: {
    flexDirection: 'row',
    gap: Spacing.sm,
  },
  analyzeBtn: {
    borderRadius: BorderRadius.sm,
    paddingVertical: 14,
    alignItems: 'center',
    justifyContent: 'center',
  },
  analyzeBtnText: {
    ...Fonts.subheading,
  },
  loadingRow: {
    flexDirection: 'row',
    gap: Spacing.sm,
    alignItems: 'center',
  },
  resultStrip: {
    gap: Spacing.md,
  },
  resultReady: {
    ...Fonts.caption,
    fontWeight: '500',
    textAlign: 'center',
  },
  reportBtn: {
    borderRadius: BorderRadius.sm,
    paddingVertical: 12,
    alignItems: 'center',
  },
  reportBtnText: {
    ...Fonts.subheading,
  },
});

export default ScanScreen;
