import * as SQLite from 'expo-sqlite';
import { ScanRecord } from '../store/useHistoryStore';

const db = SQLite.openDatabaseSync('fasaldoc.db');

// ✅ Initialize DB using new expo-sqlite v55 API
export const initDB = (): void => {
  db.execSync(`
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
  console.log('✅ Database initialized');
};

// ✅ Insert a full ScanRecord
export const insertScan = (record: ScanRecord): void => {
  db.runSync(
    `INSERT OR REPLACE INTO scans
      (id, diseaseName, cropName, confidence, stage, imageUri, scanDate, status, treatmentId, synced, description, severity)
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
};

// ✅ Get all records — returns array directly (no callback)
export const getAllScans = (): ScanRecord[] => {
  const rows = db.getAllSync<ScanRecord>(
    'SELECT * FROM scans ORDER BY scanDate DESC;',
  );
  return rows;
};

// ✅ Update scan status
export const updateScanStatus = (id: string, status: string): void => {
  db.runSync('UPDATE scans SET status = ? WHERE id = ?;', [status, id]);
};

// ✅ Delete one record
export const deleteScan = (id: string): void => {
  db.runSync('DELETE FROM scans WHERE id = ?;', [id]);
};

// ✅ Clear all data
export const clearAllScans = (): void => {
  db.execSync('DELETE FROM scans;');
};

// ✅ Get unsynced records
export const getUnsyncedScans = (): ScanRecord[] => {
  return db.getAllSync<ScanRecord>(
    'SELECT * FROM scans WHERE synced = 0 ORDER BY scanDate DESC;',
  );
};

// ✅ Mark a record as synced
export const markSynced = (id: string): void => {
  db.runSync('UPDATE scans SET synced = 1 WHERE id = ?;', [id]);
};
