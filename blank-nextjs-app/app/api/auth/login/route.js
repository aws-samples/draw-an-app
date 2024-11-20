import { NextResponse } from 'next/server';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';

export async function POST(request) {
    try {
        const { name, password } = await request.json();

        const db = await open({
            filename: './database.sqlite',
            driver: sqlite3.Database
        });

        await db.exec(`
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                password TEXT
            )
        `);

        const user = await db.get('SELECT * FROM users WHERE name = ?', [name]);
        console.log('user ', user)

        if (!user) {
            await db.run('INSERT INTO users (name, password) VALUES (?, ?)', [name, password]);
        }

        return NextResponse.json({ success: true });
    } catch (error) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}