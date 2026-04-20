import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { ScanRecord } from '../store/useHistoryStore';
import { Alert } from '../store/useAlertStore';

const TOKEN_KEY = '@fasaldoc_token';

export interface DetectResult {
  diseaseName: string;
  confidence: number;
  cropName: string;
  stage: string;
  treatmentId: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
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

const createAPIClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: process.env.REACT_APP_API_URL ?? 'https://api.fasaldoc.in',
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
  });

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
      console.error('API Error:', error?.response?.data ?? error.message);
      return Promise.reject(error);
    },
  );

  return client;
};

const apiClient = createAPIClient();

export const detectDisease = async (imageUri: string): Promise<DetectResult> => {
  const formData = new FormData();
  formData.append('image', {
    uri: imageUri,
    type: 'image/jpeg',
    name: 'leaf.jpg',
  } as unknown as Blob);

  const response = await apiClient.post<DetectResult>('/api/detect', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

  return response.data;
};

export const getAlerts = async (region: string): Promise<Alert[]> => {
  const response = await apiClient.get<Alert[]>('/api/alerts', {
    params: { region },
  });
  return response.data;
};

export const getTreatment = async (treatmentId: string): Promise<TreatmentData> => {
  const response = await apiClient.get<TreatmentData>(`/api/treatment/${treatmentId}`);
  return response.data;
};

export const syncHistory = async (records: ScanRecord[]): Promise<SyncResponse> => {
  const response = await apiClient.post<SyncResponse>('/api/sync', { records });
  return response.data;
};

export const registerFCMToken = async (token: string): Promise<void> => {
  await apiClient.post('/api/register-token', { token });
};

export default apiClient;
