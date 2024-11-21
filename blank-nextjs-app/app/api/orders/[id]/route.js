import { NextResponse } from "next/server";
import { db } from "@/lib/db";

export async function GET(req, { params }) {
    try {
        const order = await db.get("SELECT * FROM orders WHERE id = ?", [params.id]);
        if (!order) {
            return NextResponse.json({ error: "Order not found" }, { status: 404 });
        }
        return NextResponse.json(order);
    } catch (error) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}

export async function PUT(req, { params }) {
    try {
        const body = await req.json();
        await db.run(
            `UPDATE orders SET name = ?, email = ?, value = ?, count = ?, delivery = ? WHERE id = ?`,
            [body.name, body.email, body.value, body.count, body.delivery, params.id]
        );
        const order = await db.get("SELECT * FROM orders WHERE id = ?", [params.id]);
        return NextResponse.json(order);
    } catch (error) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}

export async function DELETE(req, { params }) {
    try {
        await db.run("DELETE FROM orders WHERE id = ?", [params.id]);
        return NextResponse.json({ message: "Order deleted successfully" });
    } catch (error) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
