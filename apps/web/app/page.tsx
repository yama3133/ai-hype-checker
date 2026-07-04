"use client";

import { useState } from "react";
import type { JudgeResult } from "@/lib/agentcore";

type ApiResponse = {
  status: "OK" | "ERROR";
  result?: JudgeResult;
  error?: string;
};

const VERDICT_STYLE: Record<string, string> = {
  驚き屋: "bg-red-100 text-red-700 border-red-300",
  やや誇張: "bg-yellow-100 text-yellow-700 border-yellow-300",
  堅実: "bg-green-100 text-green-700 border-green-300",
  判定失敗: "bg-gray-100 text-gray-600 border-gray-300",
};

function scoreColor(score: number | null): string {
  if (score === null) return "#9ca3af";
  if (score >= 70) return "#dc2626";
  if (score >= 40) return "#d97706";
  return "#16a34a";
}

export default function Home() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<JudgeResult | null>(null);

  const handleSubmit = async () => {
    if (!text.trim() || loading) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch("/api/judge", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      const data: ApiResponse = await res.json();
      if (data.status === "ERROR" || !data.result) {
        setError(data.error ?? "判定に失敗しました");
      } else {
        setResult(data.result);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex-1 flex flex-col items-center px-4 py-10 sm:py-16 bg-zinc-50">
      <div className="w-full max-w-xl">
        <h1 className="text-2xl sm:text-3xl font-bold text-center">
          AI驚き屋チェッカー
        </h1>
        <p className="mt-2 text-sm text-center text-gray-500">
          X（旧Twitter）のAI関連投稿を貼り付けると、誇張・扇動表現と技術的根拠を分析して
          「驚き屋度」を判定します。
        </p>

        <div className="mt-8">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="判定したい投稿の本文をここに貼り付けてください"
            rows={6}
            className="w-full rounded-lg border border-gray-300 p-3 text-sm text-black focus:outline-none focus:ring-2 focus:ring-indigo-400"
          />
          <button
            onClick={handleSubmit}
            disabled={loading || !text.trim()}
            className="mt-3 w-full rounded-lg bg-indigo-600 py-2.5 text-sm font-semibold text-white disabled:opacity-40 hover:bg-indigo-700 transition-colors"
          >
            {loading ? "判定中..." : "判定する"}
          </button>
        </div>

        {error && (
          <div className="mt-6 rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {result && (
          <div className="mt-8 rounded-xl border border-gray-200 bg-white p-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-4xl font-bold" style={{ color: scoreColor(result.score) }}>
                  {result.score ?? "-"}
                  <span className="text-base font-normal text-gray-400"> / 100</span>
                </div>
                <div className="text-xs text-gray-400 mt-1">驚き屋度スコア</div>
              </div>
              <span
                className={`rounded-full border px-4 py-1.5 text-sm font-semibold ${
                  VERDICT_STYLE[result.verdict] ?? VERDICT_STYLE["判定失敗"]
                }`}
              >
                {result.verdict}
              </span>
            </div>

            {result.reasons?.length > 0 && (
              <div className="mt-6">
                <div className="text-xs font-semibold text-gray-500 mb-2">判定理由</div>
                <ul className="space-y-1.5 text-sm text-gray-700 list-disc list-inside">
                  {result.reasons.map((reason, i) => (
                    <li key={i}>{reason}</li>
                  ))}
                </ul>
              </div>
            )}

            {result.flagged_phrases?.length > 0 && (
              <div className="mt-6">
                <div className="text-xs font-semibold text-gray-500 mb-2">検出された煽り文句</div>
                <div className="flex flex-wrap gap-2">
                  {result.flagged_phrases.map((phrase, i) => (
                    <span
                      key={i}
                      className="rounded-full bg-red-50 border border-red-200 px-3 py-1 text-xs text-red-600"
                    >
                      {phrase}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
