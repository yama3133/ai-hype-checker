"use client";

import { LOCALES, Locale } from "@/lib/i18n";
import { useI18n } from "@/lib/i18n-context";

export default function LanguageSwitcher() {
  const { locale, setLocale, t } = useI18n();
  return (
    <label className="inline-flex items-center gap-2 text-xs text-gray-500">
      <span className="sr-only">{t.language}</span>
      <select
        value={locale}
        onChange={(e) => setLocale(e.target.value as Locale)}
        className="rounded border border-gray-300 bg-white px-2 py-1 text-xs text-black"
      >
        {LOCALES.map((l) => (
          <option key={l.code} value={l.code}>
            {l.label}
          </option>
        ))}
      </select>
    </label>
  );
}
