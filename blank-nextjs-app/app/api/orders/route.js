import { NextResponse } from 'next/server';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';

export async function POST(request) {
    try {
        const orderData = await request.json();
        
        const db = await open({
            filename: './database.sqlite',
            driver: sqlite3.Database
        });

        await db.exec(`
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                value INTEGER,
                count INTEGER,
                delivery TEXT
            )
        `);

        const result = await db.run(
            'INSERT INTO orders (value, count, delivery) VALUES (?, ?, ?)',
            [orderData.value, orderData.count, orderData.delivery]
        );

        return NextResponse.json({ id: result.lastID });
    } catch (error) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}