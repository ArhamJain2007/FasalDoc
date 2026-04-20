// TFLite disabled — using backend API for inference instead
export const runInference = async (imageUri: string) => {
  throw new Error('Offline inference not available. Please connect to internet.');
};