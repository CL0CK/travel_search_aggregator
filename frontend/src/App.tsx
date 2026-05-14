import { useState } from 'react';
import { useTranslation } from './i18n/useTranslation';
import { searchTrips } from './api/client';
import type { TripRead, SearchParams } from './types/trip';
import Header from './components/Header';
import SearchForm from './components/SearchForm';
import Results from './components/Results';
import AIChatModal from './components/AIChatModal';

export default function App() {
  const { t, lang, setLang } = useTranslation();
  const [trips, setTrips] = useState<TripRead[]>([]);
  const [loading, setLoading] = useState(false);
  const [aiOpen, setAiOpen] = useState(false);

  const handleSearch = async (params: SearchParams) => {
    setLoading(true);
    setTrips([]);
    try {
      const data = await searchTrips(params);
      setTrips(data);
    } catch (err) {
      console.error('Search failed', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAIResults = (results: TripRead[]) => {
    setTrips(results);
    setAiOpen(false);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header t={t} lang={lang} setLang={setLang} onOpenAI={() => setAiOpen(true)} />

      <main className="mx-auto max-w-5xl px-4 py-6">
        <SearchForm t={t} onSearch={handleSearch} loading={loading} />
        <Results t={t} trips={trips} loading={loading} />
      </main>

      <AIChatModal
        t={t}
        open={aiOpen}
        onClose={() => setAiOpen(false)}
        onResults={handleAIResults}
      />
    </div>
  );
}
