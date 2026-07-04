import { NextRequest, NextResponse } from "next/server";
import { judgePost } from "@/lib/agentcore";

export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => null);
  const text = typeof body?.text === "string" ? body.text.trim() : "";
  if (!text) {
    return NextResponse.json({ status: "ERROR", error: "text is required" }, { status: 400 });
  }
  const result = await judgePost(text);
  if (result.status === "ERROR") {
    return NextResponse.json(result, { status: 502 });
  }
  return NextResponse.json(result);
}
