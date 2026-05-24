"use client";

import React, { createContext, useContext, useState, useCallback } from "react";
import { Language } from "@/types";
import en from "@/locales/en.json";
import hi from "@/locales/hi.json";
import bn from "@/locales/bn.json";

const locales = { en, hi, bn };

type LocaleData = typeof en;

interface LanguageContextType {
  lang: Language;
  t: LocaleData;
  setLang: (lang: Language) => void;
  cycleLang: () => void;
  langLabel: string;
}

const LanguageContext = createContext<LanguageContextType | null>(null);

const langOrder: Language[] = ["en", "hi", "bn"];
const langLabels: Record<Language, string> = { en: "EN", hi: "हिं", bn: "বাং" };

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLang] = useState<Language>("en");

  const cycleLang = useCallback(() => {
    setLang((prev) => {
      const idx = langOrder.indexOf(prev);
      return langOrder[(idx + 1) % langOrder.length];
    });
  }, []);

  const value: LanguageContextType = {
    lang,
    t: locales[lang] as LocaleData,
    setLang,
    cycleLang,
    langLabel: langLabels[lang],
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error("useLanguage must be used within LanguageProvider");
  return ctx;
}
