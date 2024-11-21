import { NextResponse } from "next/server";
import sqlite3 from "sqlite3";
import { open } from "sqlite";

let db;

async function getDb() {
    if(!db) {
        db = await open({
            filename: "database.sqlite",
            driver: sqlite3.Database
        });
        await db.exec(`CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            value INTEGER,
            count INTEGER, 
            delivery TEXT
        )`);
    }
    return db;
}

export async function POST(req) {
    const body = await req.json();
    const db = await getDb();
    
    const result = await db.run(
        "INSERT INTO orders (value, count, delivery) VALUES (?, ?, ?)",
        [body.value, body.count, body.delivery]
    );

    return NextResponse.json({id: result.lastID, ...body});
}
