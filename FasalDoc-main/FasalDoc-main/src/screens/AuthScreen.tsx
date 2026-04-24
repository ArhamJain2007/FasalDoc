import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  ScrollView, KeyboardAvoidingView, Platform, Alert,
  useColorScheme, ActivityIndicator,
} from 'react-native';
import { useTranslation } from 'react-i18next';
import { login, register } from '../services/api';
import { useAuthStore } from '../store/useAuthStore';
import { useLanguageStore } from '../store/useLanguageStore';
import { getColors } from '../constants/colors';
import { BorderRadius, Fonts, Spacing } from '../constants/fonts';
import LanguageSwitcher from '../components/LanguageSwitcher';

const REGIONS = [
  'Punjab', 'Haryana', 'Uttar Pradesh', 'Delhi NCR',
  'Rajasthan', 'Madhya Pradesh', 'Maharashtra', 'Bihar',
  'West Bengal', 'Karnataka',
];

const AuthScreen: React.FC = () => {
  const scheme = useColorScheme();
  const C = getColors(scheme);
  const { t } = useTranslation();
  const { setAuth } = useAuthStore();
  const { language } = useLanguageStore();

  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);

  // Form fields
  const [phone, setPhone]       = useState('');
  const [password, setPassword] = useState('');
  const [name, setName]         = useState('');
  const [region, setRegion]     = useState('Punjab');

  const handleSubmit = async () => {
    if (!phone.trim() || !password.trim()) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }
    if (!isLogin && !name.trim()) {
      Alert.alert('Error', 'Please enter your name');
      return;
    }

    setLoading(true);
    try {
      if (isLogin) {
        const res = await login({ phone: phone.trim(), password });
        setAuth(res.user_id, res.name, res.region);
      } else {
        const res = await register({
          phone: phone.trim(),
          password,
          name: name.trim(),
          region,
          language,
          primary_crops: [],
        });
        setAuth(res.user_id, res.name, res.region);
      }
    } catch (err: any) {
      const msg =
        err?.response?.data?.message ??
        (isLogin ? 'Invalid phone or password' : 'Registration failed');
      Alert.alert('Error', msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={[styles.flex, { backgroundColor: C.GRAY_BG }]}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView
        contentContainerStyle={styles.scroll}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={[styles.appName, { color: C.PRIMARY_GREEN }]}>🌿 FasalDoc</Text>
          <LanguageSwitcher />
        </View>

        {/* Card */}
        <View style={[styles.card, { backgroundColor: C.CARD_BG, borderColor: C.BORDER }]}>
          <Text style={[styles.title, { color: C.TEXT_PRIMARY }]}>
            {isLogin ? t('auth.loginTitle') : t('auth.registerTitle')}
          </Text>

          {/* Name (register only) */}
          {!isLogin && (
            <View style={styles.field}>
              <Text style={[styles.fieldLabel, { color: C.TEXT_SECONDARY }]}>
                {t('auth.name')}
              </Text>
              <TextInput
                style={[styles.input, { backgroundColor: C.GRAY_BG, color: C.TEXT_PRIMARY, borderColor: C.BORDER }]}
                placeholder={t('auth.namePlaceholder')}
                placeholderTextColor={C.TEXT_TERTIARY}
                value={name}
                onChangeText={setName}
                autoCapitalize="words"
              />
            </View>
          )}

          {/* Phone */}
          <View style={styles.field}>
            <Text style={[styles.fieldLabel, { color: C.TEXT_SECONDARY }]}>
              {t('auth.phone')}
            </Text>
            <TextInput
              style={[styles.input, { backgroundColor: C.GRAY_BG, color: C.TEXT_PRIMARY, borderColor: C.BORDER }]}
              placeholder={t('auth.phonePlaceholder')}
              placeholderTextColor={C.TEXT_TERTIARY}
              value={phone}
              onChangeText={setPhone}
              keyboardType="phone-pad"
              maxLength={10}
            />
          </View>

          {/* Password */}
          <View style={styles.field}>
            <Text style={[styles.fieldLabel, { color: C.TEXT_SECONDARY }]}>
              {t('auth.password')}
            </Text>
            <TextInput
              style={[styles.input, { backgroundColor: C.GRAY_BG, color: C.TEXT_PRIMARY, borderColor: C.BORDER }]}
              placeholder={t('auth.passwordPlaceholder')}
              placeholderTextColor={C.TEXT_TERTIARY}
              value={password}
              onChangeText={setPassword}
              secureTextEntry
            />
          </View>

          {/* Region (register only) */}
          {!isLogin && (
            <View style={styles.field}>
              <Text style={[styles.fieldLabel, { color: C.TEXT_SECONDARY }]}>
                {t('settings.region')}
              </Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                <View style={styles.regionRow}>
                  {REGIONS.map((r) => (
                    <TouchableOpacity
                      key={r}
                      onPress={() => setRegion(r)}
                      style={[
                        styles.regionPill,
                        {
                          backgroundColor: region === r ? C.PRIMARY_GREEN : C.GRAY_BG,
                          borderColor: region === r ? C.PRIMARY_GREEN : C.BORDER,
                        },
                      ]}
                    >
                      <Text
                        style={[
                          styles.regionText,
                          { color: region === r ? C.WHITE : C.TEXT_SECONDARY },
                        ]}
                      >
                        {r}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </ScrollView>
            </View>
          )}

          {/* Submit button */}
          <TouchableOpacity
            style={[styles.submitBtn, { backgroundColor: C.PRIMARY_GREEN, opacity: loading ? 0.7 : 1 }]}
            onPress={handleSubmit}
            disabled={loading}
            activeOpacity={0.85}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.submitText}>
                {isLogin ? t('auth.login') : t('auth.register')}
              </Text>
            )}
          </TouchableOpacity>

          {/* Toggle */}
          <TouchableOpacity onPress={() => setIsLogin(!isLogin)} style={styles.toggle}>
            <Text style={[styles.toggleText, { color: C.PRIMARY_GREEN }]}>
              {isLogin ? t('auth.switchToRegister') : t('auth.switchToLogin')}
            </Text>
          </TouchableOpacity>
        </View>

        <Text style={[styles.tagline, { color: C.TEXT_TERTIARY }]}>
          AI-powered plant disease detection for Indian farmers
        </Text>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  flex: { flex: 1 },
  scroll: { flexGrow: 1, padding: Spacing.xl, justifyContent: 'center' },
  header: {
    flexDirection: 'row', justifyContent: 'space-between',
    alignItems: 'center', marginBottom: Spacing.xxl,
  },
  appName: { fontSize: 24, fontWeight: '600' },
  card: {
    borderRadius: BorderRadius.frame, borderWidth: 0.5,
    padding: Spacing.xl, marginBottom: Spacing.xl,
  },
  title: { ...Fonts.heading, marginBottom: Spacing.xl },
  field: { marginBottom: Spacing.lg },
  fieldLabel: { ...Fonts.caption, fontWeight: '500', marginBottom: 6, textTransform: 'uppercase', letterSpacing: 0.5 },
  input: {
    borderRadius: BorderRadius.sm, borderWidth: 0.5,
    paddingHorizontal: Spacing.md, paddingVertical: 12,
    ...Fonts.body,
  },
  regionRow: { flexDirection: 'row', gap: 8, paddingVertical: 4 },
  regionPill: {
    paddingHorizontal: Spacing.md, paddingVertical: 6,
    borderRadius: BorderRadius.pill, borderWidth: 1,
  },
  regionText: { ...Fonts.caption, fontWeight: '500' },
  submitBtn: {
    borderRadius: BorderRadius.sm, paddingVertical: 14,
    alignItems: 'center', marginTop: Spacing.sm,
  },
  submitText: { ...Fonts.subheading, color: '#fff', fontWeight: '600' },
  toggle: { alignItems: 'center', marginTop: Spacing.lg },
  toggleText: { ...Fonts.body },
  tagline: { ...Fonts.caption, textAlign: 'center' },
});

export default AuthScreen;
