import sqlite3 from "sqlite3";
import { open } from "sqlite";

let db = null;

async function initDB() {
    if (!db) {
        db = await open({
            filename: "./orders.db",
            driver: sqlite3.Database
        });

        await db.exec(`
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                value INTEGER,
                count INTEGER,
                delivery INTEGER
            )
        `);
    }
    return db;
}

export { initDB as db };
