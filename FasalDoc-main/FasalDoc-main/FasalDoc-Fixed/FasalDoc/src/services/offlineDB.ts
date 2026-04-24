import { ScanRecord } from '../store/useHistoryStore';

// Lazy-load SQLite so it doesn't crash on web/Expo Go
let db: any = null;

const getDB = () => {
  if (!db) {
    const SQLite = require('expo-sqlite');
    db = SQLite.openDatabaseSync('fasaldoc.db');
  }
  return db;
};

export const initDB = (): void => {
  try {
    getDB().execSync(`
      CREATE TABLE IF NOT EXISTS scans (
        id TEXT PRIMARY KEY,
        diseaseName TEXT NOT NULL,
        cropName TEXT NOT NULL,
        confidence REAL NOT NULL,
        stage TEXT NOT NULL,
        imageUri TEXT NOT NULL,
        scanDate TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'active',
        treatmentId TEXT NOT NULL,
        synced INTEGER NOT NULL DEFAULT 0,
        description TEXT,
        severity TEXT
      );
    `);
    console.log('[DB] Initialized');
  } catch (err) {
    console.warn('[DB] Init failed:', err);
  }
};

export const insertScan = (record: ScanRecord): void => {
  try {
    getDB().runSync(
      `INSERT OR REPLACE INTO scans
        (id, diseaseName, cropName, confidence, stage, imageUri, scanDate,
         status, treatmentId, synced, description, severity)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);`,
      [
        record.id,
        record.diseaseName,
        record.cropName,
        record.confidence,
        record.stage,
        record.imageUri,
        record.scanDate,
        record.status,
        record.treatmentId,
        record.synced,
        record.description ?? null,
        record.severity ?? null,
      ],
    );
  } catch (err) {
    console.warn('[DB] insertScan failed:', err);
  }
};

export const getAllScans = (): ScanRecord[] => {
  try {
    return getDB().getAllSync<ScanRecord>(
      'SELECT * FROM scans ORDER BY scanDate DESC;',
    );
  } catch (err) {
    console.warn('[DB] getAllScans failed:', err);
    return [];
  }
};

export const updateScanStatus = (id: string, status: string): void => {
  try {
    getDB().runSync('UPDATE scans SET status = ? WHERE id = ?;', [status, id]);
  } catch (err) {
    console.warn('[DB] updateScanStatus failed:', err);
  }
};

export const getUnsyncedScans = (): ScanRecord[] => {
  try {
    return getDB().getAllSync<ScanRecord>(
      'SELECT * FROM scans WHERE synced = 0 ORDER BY scanDate DESC;',
    );
  } catch (err) {
    console.warn('[DB] getUnsyncedScans failed:', err);
    return [];
  }
};

export const markSynced = (id: string): void => {
  try {
    getDB().runSync('UPDATE scans SET synced = 1 WHERE id = ?;', [id]);
  } catch (err) {
    console.warn('[DB] markSynced failed:', err);
  }
};

export const deleteScan = (id: string): void => {
  try {
    getDB().runSync('DELETE FROM scans WHERE id = ?;', [id]);
  } catch (err) {
    console.warn('[DB] deleteScan failed:', err);
  }
};
