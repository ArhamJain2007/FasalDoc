import * as SQLite from 'expo-sqlite';

const db = SQLite.openDatabaseSync('fasaldoc.db');

// Types (adjust based on your app)
export type ScanRecord = {
  id?: number;
  data: string;
};

// ✅ Initialize DB
export const initDB = () => {
  db.transaction((tx) => {
    tx.executeSql(
      `CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT
      );`,
      [],
      () => {
        console.log('✅ Database initialized');
      },
      (_, error) => {
        console.log('❌ DB Init Error:', error);
        return false;
      }
    );
  });
};

// ✅ Insert record
export const insertScan = (data: string) => {
  db.transaction((tx) => {
    tx.executeSql(
      'INSERT INTO scans (data) VALUES (?);',
      [data],
      () => {
        console.log('✅ Scan inserted');
      },
      (_, error) => {
        console.log('❌ Insert Error:', error);
        return false;
      }
    );
  });
};

// ✅ Get all records
export const getAllScans = (
  callback: (records: ScanRecord[]) => void
) => {
  db.transaction((tx) => {
    tx.executeSql(
      'SELECT * FROM scans ORDER BY id DESC;',
      [],
      (_, result) => {
        callback(result.rows._array);
      },
      (_, error) => {
        console.log('❌ Fetch Error:', error);
        return false;
      }
    );
  });
};

// ✅ Delete one record
export const deleteScan = (id: number) => {
  db.transaction((tx) => {
    tx.executeSql(
      'DELETE FROM scans WHERE id = ?;',
      [id],
      () => {
        console.log('🗑️ Scan deleted');
      },
      (_, error) => {
        console.log('❌ Delete Error:', error);
        return false;
      }
    );
  });
};

// ✅ Clear all data
export const clearAllScans = () => {
  db.transaction((tx) => {
    tx.executeSql(
      'DELETE FROM scans;',
      [],
      () => {
        console.log('🧹 All scans cleared');
      },
      (_, error) => {
        console.log('❌ Clear Error:', error);
        return false;
      }
    );
  });
};