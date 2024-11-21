import { NextResponse } from "next/server";
import { db } from "@/lib/db";

export async function POST(req) {
    try {
        const body = await req.json();
        const order = {
            ...body,
            value: Math.floor(Math.random() * 1000),
            count: Math.floor(Math.random() * 20),
            delivery: Math.floor(Math.random() * 24)
        };
        
        const result = await db.run(
            `INSERT INTO orders (name, email, value, count, delivery) VALUES (?, ?, ?, ?, ?)`,
            [order.name, order.email, order.value, order.count, order.delivery]
        );

        return NextResponse.json({ ...order, id: result.lastID });
    } catch (error) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
