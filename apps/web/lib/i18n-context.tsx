"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { DEFAULT_LOCALE, DICTIONARIES, Locale } from "@/lib/i18n";

const STORAGE_KEY = "ai-hype-checker-locale";

interface Ctx {
  locale: Locale;
  setLocale: (l: Locale) => void;
  t: (typeof DICTIONARIES)[Locale];
}

const I18nContext = createContext<Ctx | null>(null);

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(DEFAULT_LOCALE);

  useEffect(() => {
    try {
      const stored = window.localStorage.getItem(STORAGE_KEY) as Locale | null;
      if (stored && stored in DICTIONARIES) {
        setLocaleState(stored);
      } else {
        const nav = (typeof navigator !== "undefined" ? navigator.language : "")
          .slice(0, 2)
          .toLowerCase();
        if (nav && nav in DICTIONARIES) {
          setLocaleState(nav as Locale);
        }
      }
    } catch {
      /* ignore */
    }
  }, []);

  useEffect(() => {
    if (typeof document !== "undefined") {
      document.documentElement.lang = locale;
    }
  }, [locale]);

  const setLocale = (l: Locale) => {
    setLocaleState(l);
    try {
      window.localStorage.setItem(STORAGE_KEY, l);
    } catch {
      /* ignore */
    }
  };

  const value: Ctx = {
    locale,
    setLocale,
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
