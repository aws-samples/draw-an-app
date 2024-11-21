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
    }
    return db;
}

export async function GET(req, {params}) {
    const db = await getDb();
    const order = await db.get("SELECT * FROM orders WHERE id = ?", params.id);
    return NextResponse.json(order);
}

export async function POST(req, {params}) {
    const path = req.url;
    if(path.endsWith("/print")) {
        // Print logic here
        return NextResponse.json({success: true});
    }
    if(path.endsWith("/cancel")) {
        const db = await getDb();
        await db.run("DELETE FROM orders WHERE id = ?", params.id);
        return NextResponse.json({success: true}); 
    }
    return NextResponse.error();
}
