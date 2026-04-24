import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { ScanRecord } from '../store/useHistoryStore';
import { Alert } from '../store/useAlertStore';

const TOKEN_KEY = '@fasaldoc_token';

// ─── Types ────────────────────────────────────────────────────────────────────

export interface DetectResult {
  scan_id: string;
  diseaseName: string;
  cropName: string;
  confidence: number;
  stage: string;
  treatmentId: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
  image_url: string;
  scan_date: string;
}

export interface TreatmentData {
  id: string;
  diseaseName: string;
  cropName: string;
  organic: string[];
  chemical: string[];
  dosage: string;
  description: string;
}

export interface SyncResponse {
  synced: string[];
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user_id: string;
  name: string;
  region: string;
  language: string;
}

export interface RegisterPayload {
  phone: string;
  password: string;
  name: string;
  region: string;
  language: string;
  primary_crops: string[];
}

export interface LoginPayload {
  phone: string;
  password: string;
}

// ─── Client factory ───────────────────────────────────────────────────────────

const API_BASE =
  (process.env.EXPO_PUBLIC_API_URL ?? 'http://10.0.2.2:8000') + '/api/v1';

const createAPIClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: API_BASE,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
  });

  // Attach JWT on every request
  client.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
    const token = await AsyncStorage.getItem(TOKEN_KEY);
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  client.interceptors.response.use(
    (response) => response,
    (error) => {
      const msg = error?.response?.data?.message ?? error.message;
      console.error('[API Error]', msg);
      return Promise.reject(error);
    },
  );

  return client;
};

export const apiClient = createAPIClient();

// ─── Auth helpers ─────────────────────────────────────────────────────────────

export const saveToken = async (token: string): Promise<void> => {
  await AsyncStorage.setItem(TOKEN_KEY, token);
};

export const getToken = async (): Promise<string | null> => {
  return AsyncStorage.getItem(TOKEN_KEY);
};

export const clearToken = async (): Promise<void> => {
  await AsyncStorage.removeItem(TOKEN_KEY);
};

// ─── Auth endpoints ───────────────────────────────────────────────────────────

export const register = async (payload: RegisterPayload): Promise<TokenResponse> => {
  const response = await apiClient.post<TokenResponse>('/auth/register', payload);
  await saveToken(response.data.access_token);
  return response.data;
};

export const login = async (payload: LoginPayload): Promise<TokenResponse> => {
  const response = await apiClient.post<TokenResponse>('/auth/login', payload);
  await saveToken(response.data.access_token);
  return response.data;
};

// ─── Detection endpoint ───────────────────────────────────────────────────────

export const detectDisease = async (
  imageUri: string,
  language: string = 'en',
): Promise<DetectResult> => {
  const formData = new FormData();
  formData.append('file', {
    uri: imageUri,
    type: 'image/jpeg',
    name: 'leaf.jpg',
  } as unknown as Blob);

  const response = await apiClient.post<{
    scan_id: string;
    disease_name: string;
    crop_name: string;
    confidence: number;
    stage: string;
    treatment_id: string;
    description: string;
    severity: 'low' | 'medium' | 'high';
    image_url: string;
    scan_date: string;
  }>(`/detect?language=${language}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

  // Map snake_case backend response → camelCase frontend
  const d = response.data;
  return {
    scan_id: d.scan_id,
    diseaseName: d.disease_name,
    cropName: d.crop_name,
    confidence: d.confidence,
    stage: d.stage,
    treatmentId: d.treatment_id,
    description: d.description,
    severity: d.severity,
    image_url: d.image_url,
    scan_date: d.scan_date,
  };
};

// ─── Alerts endpoint ──────────────────────────────────────────────────────────

export const getAlerts = async (
  region: string,
  language: string = 'en',
): Promise<Alert[]> => {
  const response = await apiClient.get<{ alerts: Alert[]; region: string }>(
    `/alerts?region=${encodeURIComponent(region)}&language=${language}`,
  );
  // Backend returns { alerts: [...], region: "..." }
  return response.data.alerts ?? [];
};

// ─── Treatment endpoint ───────────────────────────────────────────────────────

export const getTreatment = async (
  treatmentId: string,
  language: string = 'en',
): Promise<TreatmentData> => {
  const response = await apiClient.get<{
    id: string;
    disease_name: string;
    crop_name: string;
    organic: string[];
    chemical: string[];
    dosage: string;
    description: string;
  }>(`/treatment/${treatmentId}?language=${language}`);

  const d = response.data;
  return {
    id: d.id,
    diseaseName: d.disease_name,
    cropName: d.crop_name,
    organic: d.organic,
    chemical: d.chemical,
    dosage: d.dosage,
    description: d.description,
  };
};

// ─── Sync endpoint ────────────────────────────────────────────────────────────

export const syncHistory = async (records: ScanRecord[]): Promise<SyncResponse> => {
  const response = await apiClient.post<SyncResponse>('/sync', { records });
  return response.data;
};

// ─── FCM token ────────────────────────────────────────────────────────────────

export const registerFCMToken = async (token: string): Promise<void> => {
  await apiClient.post('/register-token', { token });
};

export default apiClient;
