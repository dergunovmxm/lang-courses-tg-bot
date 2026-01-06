import { Pool, PoolConfig } from 'pg';
import dotenv from 'dotenv';

dotenv.config();

// Конфигурация подключения к PostgreSQL
const dbConfig: PoolConfig = {
  host: process.env.POSTGRESQL_HOST,
  port: parseInt(process.env.POSTGRESQL_PORT || '5432'),
  database: process.env.POSTGRESQL_DBNAME,
  user: process.env.POSTGRESQL_USER,
  password: process.env.POSTGRESQL_PASSWORD,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
};

class Database {
  private static instance: Database;
  private pool: Pool;

  private constructor() {
    this.pool = new Pool(dbConfig);
    
    // Обработка ошибок подключения
    this.pool.on('error', (err) => {
      console.error('Unexpected error on idle client', err);
    });

    // Тестовое подключение
    this.testConnection();
  }

  public static getInstance(): Database {
    if (!Database.instance) {
      Database.instance = new Database();
    }
    return Database.instance;
  }

  private async testConnection() {
    try {
      const client = await this.pool.connect();
      console.log('✅ PostgreSQL connected successfully');
      client.release();
    } catch (error) {
      console.log('dbConfig', dbConfig)
      console.error('❌ Error connecting to PostgreSQL:', error);
      throw error;
    }
  }

  public async query(text: string, params?: any[]) {
    const start = Date.now();
    try {
      const res = await this.pool.query(text, params);
      const duration = Date.now() - start;
      console.log('Executed query', { text, duration, rows: res.rowCount });
      return res;
    } catch (error) {
      console.error('Error executing query', { text, error });
      throw error;
    }
  }

  public async connect() {
    return this.testConnection();
  }

  public async close() {
    await this.pool.end();
    console.log('PostgreSQL connection pool closed');
  }

  // Метод для проверки здоровья БД
  public async healthCheck() {
    try {
      await this.query('SELECT 1');
      return true;
    } catch (error) {
      return false;
    }
  }
}

export const db = Database.getInstance();
export type { PoolConfig };