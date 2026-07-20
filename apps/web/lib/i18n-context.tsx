"use client";

import React, { createContext, useContext, useEffect, useSyncExternalStore } from "react";
import { DEFAULT_LOCALE, DICTIONARIES, Locale } from "@/lib/i18n";

const STORAGE_KEY = "ai-hype-checker-locale";

// localStorage+navigatorを外部ストアとして扱う（SSR初回はDEFAULT_LOCALE、
// ハイドレーション後にクライアント側の値へ切り替わる）
let memoryLocale: Locale | null = null;
let listeners: Array<() => void> = [];

function subscribe(listener: () => void): () => void {
  listeners.push(listener);
  return () => {
    listeners = listeners.filter((l) => l !== listener);
  };
}

function getLocaleSnapshot(): Locale {
  if (memoryLocale) return memoryLocale;
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored && stored in DICTIONARIES) return stored as Locale;
  } catch {
    /* ignore */
  }
  const nav = (typeof navigator !== "undefined" ? navigator.language : "")
    .slice(0, 2)
    .toLowerCase();
  if (nav && nav in DICTIONARIES) return nav as Locale;
  return DEFAULT_LOCALE;
}

function setStoredLocale(l: Locale): void {
  memoryLocale = l;
  try {
    window.localStorage.setItem(STORAGE_KEY, l);
  } catch {
    /* ignore */
  }
  listeners.forEach((fn) => fn());
}

interface Ctx {
  locale: Locale;
  setLocale: (l: Locale) => void;
  t: (typeof DICTIONARIES)[Locale];
}

const I18nContext = createContext<Ctx | null>(null);

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const locale = useSyncExternalStore(subscribe, getLocaleSnapshot, () => DEFAULT_LOCALE);

  useEffect(() => {
    document.documentElement.lang = locale;
  }, [locale]);

  const value: Ctx = {
    locale,
    setLocale: setStoredLocale,
    t: DICTIONARIES[locale],
  };
  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): Ctx {
  const c = useContext(I18nContext);
  if (!c) {
    return {
      locale: DEFAULT_LOCALE,
      setLocale: () => undefined,
      t: DICTIONARIES[DEFAULT_LOCALE],
    };
  }
  return c;
}
