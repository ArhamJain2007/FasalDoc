// TFLite offline inference — disabled, using backend API instead.
// Return type matches DetectResult shape so ScanScreen destructuring works.
export interface TFLiteResult {
  diseaseName: string;
  confidence: number;
  cropName: string;
  stage: string;
  treatmentId: string;
  severity: 'low' | 'medium' | 'high';
}

export const loadModel = async (): Promise<void> => {
  // No-op: model loading disabled; API is used instead
  console.log('[TFLite] Offline model disabled — using API inference');
};

export const runInference = async (_imageUri: string): Promise<TFLiteResult> => {
  throw new Error('Offline inference not available. Please connect to the internet.');
};
