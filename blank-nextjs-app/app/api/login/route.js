import { NextResponse } from "next/server";

export async function POST(req) {
    const body = await req.json();
    // Validate login - simplified for demo
    if(body.name && body.pwd) {
        return NextResponse.json({success: true});
    }
    return NextResponse.error();
}
