import { NextRequest, NextResponse } from "next/server";
import { judgePost } from "@/lib/agentcore";

// Web検索ファクトチェックで判定が長引くため上限を延長
export const maxDuration = 300;

// コスト増幅攻撃対策の簡易レート制限（インスタンス内メモリのIP別スライディングウィンドウ。
// Vercelのインスタンスを跨いでは共有されない前提の軽量版）
const RATE_WINDOW_MS = 10 * 60 * 1000;
const RATE_MAX_PER_WINDOW = 5;
const rateHits = new Map<string, number[]>();

function isRateLimited(ip: string): boolean {
  const now = Date.now();
  if (rateHits.size > 1000) {
    for (const [k, v] of rateHits) {
      if (v.every((t) => now - t >= RATE_WINDOW_MS)) rateHits.delete(k);
    }
  }
  const recent = (rateHits.get(ip) ?? []).filter((t) => now - t < RATE_WINDOW_MS);
  if (recent.length >= RATE_MAX_PER_WINDOW) {
    rateHits.set(ip, recent);
    return true;
  }
  recent.push(now);
  rateHits.set(ip, recent);
  return false;
}

const RATE_LIMIT_MESSAGE = {
  ja: "リクエストが多すぎます。しばらく待ってから再試行してください",
  en: "Too many requests. Please wait a while and try again.",
} as const;

export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => null);
  const text = typeof body?.text === "string" ? body.text.trim() : "";
  const lang = body?.lang === "en" ? "en" : "ja";
  const ip =
    req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ||
    req.headers.get("x-real-ip") ||
    "unknown";
  if (isRateLimited(ip)) {
    return NextResponse.json({ status: "ERROR", error: RATE_LIMIT_MESSAGE[lang] }, { status: 429 });
  }
  if (!text) {
    return NextResponse.json({ status: "ERROR", error: "text is required" }, { status: 400 });
  }
  if (text.length > 5000) {
    return NextResponse.json({ status: "ERROR", error: "text too long (max 5000)" }, { status: 400 });
  }
  const result = await judgePost(text, lang);
  if (result.status === "ERROR") {
    return NextResponse.json(result, { status: 502 });
  }
  return NextResponse.json(result);
}
