import { useState, useEffect, useCallback } from 'react';
import translations, { type Language, type TranslationKey } from './translations';

function detectLanguage(): Language {
  const lang = navigator.language;
  if (lang.startsWith('de')) return 'de';
  return 'en';
}

export function useTranslation() {
  const [lang, setLangState] = useState<Language>(() => detectLanguage());

  useEffect(() => {
    const detected = detectLanguage();
    setLangState(detected);
  }, []);

  const setLang = useCallback((l: Language) => {
    setLangState(l);
  }, []);

  const t = useCallback(
    (key: TranslationKey, params?: Record<string, string | number>): string => {
      let text = translations[lang][key];
      if (params) {
        for (const [k, v] of Object.entries(params)) {
          text = text.replace(`{${k}}`, String(v));
        }
      }
      return text;
    },
    [lang],
  );

  return { t, lang, setLang };
}
