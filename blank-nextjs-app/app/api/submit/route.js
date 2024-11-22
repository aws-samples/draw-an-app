import { NextResponse } from 'next/server';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';

// Initialize database
async function openDb() {
  return open({
    filename: './database.sqlite',
    driver: sqlite3.Database
  });
}

// Create table if it doesn't exist
async function initializeDb() {
  const db = await openDb();
  await db.exec(`
    CREATE TABLE IF NOT EXISTS submissions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      division TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);
  await db.close();
}

// Initialize database when server starts
initializeDb().catch(console.error);

export async function POST(request) {
  try {
    const { name, division } = await request.json();

    if (!name || !division) {
      return NextResponse.json(
        { success: false, message: 'Name and division are required' },
        { status: 400 }
      );
    }

    const db = await openDb();
    await db.run(
      'INSERT INTO submissions (name, division) VALUES (?, ?)',
      [name, division]
    );
    await db.close();

    return NextResponse.json(
      { success: true, message: 'Data stored successfully' },
      { status: 200 }
    );
  } catch (error) {
    console.error('Error:', error);
    return NextResponse.json(
      { success: false, message: 'Internal server error' },
      { status: 500 }
    );
  }
}