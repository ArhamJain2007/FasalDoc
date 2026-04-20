import { create } from 'zustand';
import { getAllScans, insertScan, updateScanStatus } from '../services/offlineDB';

export type ScanStatus = 'active' | 'treated' | 'resolved';

export interface ScanRecord {
  id: string;
  diseaseName: string;
  cropName: string;
  confidence: number;
  stage: string;
  imageUri: string;
  scanDate: string;
  status: ScanStatus;
  treatmentId: string;
  synced: 0 | 1;
  description?: string;
  severity?: 'low' | 'medium' | 'high';
}

interface HistoryState {
  scans: ScanRecord[];
  isLoading: boolean;
  addScan: (record: ScanRecord) => Promise<void>;
  updateStatus: (id: string, status: ScanStatus) => Promise<void>;
  loadFromDB: () => Promise<void>;
}

export const useHistoryStore = create<HistoryState>((set) => ({
  scans: [],
  isLoading: false,

  addScan: async (record: ScanRecord) => {
    await insertScan(record);
    set((state) => ({ scans: [record, ...state.scans] }));
  },

  updateStatus: async (id: string, status: ScanStatus) => {
    await updateScanStatus(id, status);
    set((state) => ({
      scans: state.scans.map((s) => (s.id === id ? { ...s, status } : s)),
    }));
  },

  loadFromDB: async () => {
    set({ isLoading: true });
    try {
      const scans = await getAllScans();
      set({ scans, isLoading: false });
    } catch {
      set({ isLoading: false });
    }
  },
}));
