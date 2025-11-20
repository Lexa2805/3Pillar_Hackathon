import { NextResponse } from "next/server";
import clientPromise from "@/lib/mongodb";

export async function GET() {
  try {
    const client = await clientPromise;
    const db = client.db(process.env.DB_NAME);

    const collections = await db.listCollections().toArray();

    return NextResponse.json({ 
      status: "success", 
      message: "Connected to MongoDB!",
      collections: collections.map(c => c.name) 
    });
  } catch (e) {
    console.error(e);
    return NextResponse.json({ status: "error", error: e }, { status: 500 });
  }
}