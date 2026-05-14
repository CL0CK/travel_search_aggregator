import type { Language } from '../i18n/translations';

interface HeaderProps {
  t: (key: any, params?: any) => string;
  lang: Language;
  setLang: (l: Language) => void;
  onOpenAI: () => void;
}

export default function Header({ t, lang, setLang, onOpenAI }: HeaderProps) {
  return (
    <header className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600 text-lg font-bold text-white">
            ✈
          </div>
          <div>
            <h1 className="text-xl font-semibold text-gray-900">{t('app.title')}</h1>
            <p className="text-xs text-gray-500">{t('app.subtitle')}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={onOpenAI}
            className="rounded-lg border border-purple-200 bg-purple-50 px-3 py-1.5 text-sm font-medium text-purple-700 transition-colors hover:bg-purple-100"
          >
            {t('ai.openBtn')}
          </button>

          <div className="flex overflow-hidden rounded-lg border border-gray-200">
            <button
              onClick={() => setLang('en')}
              className={`px-2.5 py-1 text-xs font-medium transition-colors ${
                lang === 'en' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'
              }`}
            >
              {t('lang.en')}
            </button>
            <button
              onClick={() => setLang('de')}
              className={`px-2.5 py-1 text-xs font-medium transition-colors ${
                lang === 'de' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'
              }`}
            >
              {t('lang.de')}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
