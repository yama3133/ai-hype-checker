"use client";

import { useState } from "react";
import type { JudgeResult, Verdict } from "@/lib/agentcore";
import { useI18n } from "@/lib/i18n-context";
import LanguageSwitcher from "@/components/LanguageSwitcher";

type ApiResponse = {
  status: "OK" | "ERROR";
  result?: JudgeResult;
  error?: string;
};

const VERDICT_STYLE: Record<Verdict, string> = {
  hype: "bg-red-100 text-red-700 border-red-300",
  exaggerated: "bg-yellow-100 text-yellow-700 border-yellow-300",
  grounded: "bg-green-100 text-green-700 border-green-300",
  failed: "bg-gray-100 text-gray-600 border-gray-300",
};

function scoreColor(score: number | null): string {
  if (score === null) return "#9ca3af";
  if (score >= 70) return "#dc2626";
  if (score >= 40) return "#d97706";
  return "#16a34a";
}

export default function Home() {
  const { locale, t } = useI18n();
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<JudgeResult | null>(null);

  const verdictLabel: Record<Verdict, string> = {
    hype: t.verdictHype,
    exaggerated: t.verdictExaggerated,
    grounded: t.verdictGrounded,
    failed: t.verdictFailed,
  };

  const handleSubmit = async () => {
    if (!text.trim() || loading) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch("/api/judge", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, lang: locale }),
      });
      const data: ApiResponse = await res.json();
      if (data.status === "ERROR" || !data.result) {
        setError(data.error ?? t.errorGeneric);
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
        <div className="flex justify-end mb-2">
          <LanguageSwitcher />
        </div>

        <h1 className="text-2xl sm:text-3xl font-bold text-center">{t.appTitle}</h1>
        <p className="mt-2 text-sm text-center text-gray-500">{t.appDescription}</p>

        <div className="mt-8">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={t.placeholder}
            rows={6}
            className="w-full rounded-lg border border-gray-300 p-3 text-sm text-black focus:outline-none focus:ring-2 focus:ring-indigo-400"
          />
          <button
            onClick={handleSubmit}
            disabled={loading || !text.trim()}
            className="mt-3 w-full rounded-lg bg-indigo-600 py-2.5 text-sm font-semibold text-white disabled:opacity-40 hover:bg-indigo-700 transition-colors"
          >
            {loading ? t.submitting : t.submit}
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
                <div className="text-xs text-gray-400 mt-1">{t.scoreLabel}</div>
              </div>
              <span
                className={`rounded-full border px-4 py-1.5 text-sm font-semibold ${
                  VERDICT_STYLE[result.verdict] ?? VERDICT_STYLE.failed
                }`}
              >
                {verdictLabel[result.verdict] ?? result.verdict}
              </span>
            </div>

            {result.reasons?.length > 0 && (
              <div className="mt-6">
                <div className="text-xs font-semibold text-gray-500 mb-2">{t.reasonsLabel}</div>
                <ul className="space-y-1.5 text-sm text-gray-700 list-disc list-inside">
                  {result.reasons.map((reason, i) => (
                    <li key={i}>{reason}</li>
                  ))}
                </ul>
              </div>
            )}

            {result.flagged_phrases?.length > 0 && (
              <div className="mt-6">
                <div className="text-xs font-semibold text-gray-500 mb-2">
                  {t.flaggedPhrasesLabel}
                </div>
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
