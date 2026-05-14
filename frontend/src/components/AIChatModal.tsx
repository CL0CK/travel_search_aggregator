import { useState, useRef, useEffect } from 'react';
import { extractParams, searchTrips } from '../api/client';
import type { ExtractionParams, TripRead } from '../types/trip';

interface Message {
  role: 'user' | 'assistant';
  text: string;
}

interface AIChatModalProps {
  t: (key: any, params?: any) => string;
  open: boolean;
  onClose: () => void;
  onResults: (results: TripRead[]) => void;
}

const EMPTY_PARAMS: ExtractionParams = {
  destination: null,
  origin: null,
  check_in: null,
  check_out: null,
  budget: null,
};

function mergeParams(old: ExtractionParams, fresh: ExtractionParams): ExtractionParams {
  return {
    destination: old.destination ?? fresh.destination,
    origin: old.origin ?? fresh.origin,
    check_in: old.check_in ?? fresh.check_in,
    check_out: old.check_out ?? fresh.check_out,
    budget: old.budget ?? fresh.budget,
  };
}

function describeMissing(p: ExtractionParams, t: (key: any) => string): string | null {
  if (!p.destination) return t('ai.missingDestination');
  if (!p.origin) return t('ai.missingOrigin');
  if (!p.check_in || !p.check_out) return t('ai.missingDates');
  return null;
}

function formatExtracted(p: ExtractionParams, t: (key: any) => string): string {
  const parts = [t('ai.extracted')];
  if (p.destination) parts.push(`destination = ${p.destination}`);
  if (p.origin) parts.push(`origin = ${p.origin}`);
  if (p.check_in) parts.push(`check-in = ${p.check_in}`);
  if (p.check_out) parts.push(`check-out = ${p.check_out}`);
  if (p.budget) parts.push(`budget = €${p.budget}`);
  return parts.join(', ') + '.';
}

export default function AIChatModal({ t, open, onClose, onResults }: AIChatModalProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [accumulated, setAccumulated] = useState<ExtractionParams>(EMPTY_PARAMS);
  const [searched, setSearched] = useState(false);
  const searchOptimisticRef = useRef(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (open) {
      setMessages([]);
      setInput('');
      setAccumulated(EMPTY_PARAMS);
      setSearched(false);
    }
  }, [open]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    const query = input.trim();
    if (!query || loading) return;

    setInput('');
    setMessages((prev) => [...prev, { role: 'user', text: query }]);
    setLoading(true);

    try {
      const fresh = await extractParams(query);
      const merged = mergeParams(accumulated, fresh);
      setAccumulated(merged);

      const extractedMsg = formatExtracted(merged, t);
      const missing = describeMissing(merged, t);

      if (missing) {
        setMessages((prev) => [...prev, { role: 'assistant', text: `${extractedMsg}\n\n${missing}` }]);
      } else if (!searched) {
        setSearched(true);
        searchOptimisticRef.current = true;

        setMessages((prev) => [...prev, { role: 'assistant', text: `${extractedMsg}\n\n${t('ai.allSet')}` }]);

        const trips = await searchTrips({
          destination: merged.destination!,
          origin: merged.origin!,
          check_in: merged.check_in!,
          check_out: merged.check_out!,
        });

        setMessages((prev) => [
          ...prev.slice(0, -1),
          { role: 'assistant', text: t('ai.foundResults', { count: trips.length }) },
        ]);

        if (trips.length > 0) {
          onResults(trips);
        }
      }
    } catch (err: any) {
      const message = err?.detail || err?.message || t('ai.error');
      if (searchOptimisticRef.current) {
        searchOptimisticRef.current = false;
        setMessages((prev) => [...prev.slice(0, -1), { role: 'assistant', text: message }]);
      } else {
        setMessages((prev) => [...prev, { role: 'assistant', text: message }]);
      }
    } finally {
      setLoading(false);
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="flex h-[500px] w-full max-w-lg flex-col rounded-2xl bg-white shadow-xl">
        <div className="flex items-center justify-between border-b border-gray-200 px-5 py-3">
          <h2 className="text-base font-semibold text-gray-900">{t('ai.modalTitle')}</h2>
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-5 py-3">
          {messages.length === 0 && (
            <p className="mt-8 text-center text-sm text-gray-400">{t('ai.placeholder')}</p>
          )}
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`mb-3 max-w-[85%] rounded-xl px-4 py-2.5 text-sm leading-relaxed ${
                msg.role === 'user'
                  ? 'ml-auto bg-blue-600 text-white'
                  : 'mr-auto border border-gray-200 bg-gray-50 text-gray-800'
              }`}
            >
              {msg.text}
            </div>
          ))}
          {loading && (
            <div className="mr-auto mb-3 max-w-[85%] rounded-xl border border-gray-200 bg-gray-50 px-4 py-2.5 text-sm text-gray-500">
              {t('ai.thinking')}
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="flex items-center gap-2 border-t border-gray-200 px-5 py-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder={t('ai.placeholder')}
            className="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {t('ai.sendBtn')}
          </button>
        </div>
      </div>
    </div>
  );
}
