import { useEffect, useState } from 'react';
import type { SearchParams } from '../types/trip';

interface SearchFormProps {
  t: (key: any, params?: any) => string;
  onSearch: (params: SearchParams) => void;
  loading: boolean;
  aiValues: SearchParams | null;
}

export default function SearchForm({ t, onSearch, loading, aiValues }: SearchFormProps) {
  const [destination, setDestination] = useState('');
  const [origin, setOrigin] = useState('');
  const [checkIn, setCheckIn] = useState('');
  const [checkOut, setCheckOut] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [hotelStars, setHotelStars] = useState('');

  useEffect(() => {
    if (aiValues) {
      setDestination(aiValues.destination);
      setOrigin(aiValues.origin);
      setCheckIn(aiValues.check_in);
      setCheckOut(aiValues.check_out);
    }
  }, [aiValues]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!destination || !origin || !checkIn || !checkOut) return;
    onSearch({
      destination: destination.trim(),
      origin: origin.trim(),
      check_in: checkIn,
      check_out: checkOut,
      max_price: maxPrice ? Number(maxPrice) : undefined,
      hotel_stars: hotelStars ? Number(hotelStars) : undefined,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">{t('search.destination')}</label>
          <input
            type="text"
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            required
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            placeholder="Paris"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">{t('search.origin')}</label>
          <input
            type="text"
            value={origin}
            onChange={(e) => setOrigin(e.target.value)}
            required
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            placeholder="London"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">{t('search.checkIn')}</label>
          <input
            type="date"
            value={checkIn}
            onChange={(e) => setCheckIn(e.target.value)}
            required
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">{t('search.checkOut')}</label>
          <input
            type="date"
            value={checkOut}
            onChange={(e) => setCheckOut(e.target.value)}
            required
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">{t('search.maxPrice')}</label>
          <input
            type="number"
            min={0}
            step={10}
            value={maxPrice}
            onChange={(e) => setMaxPrice(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            placeholder="500"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">{t('search.hotelStars')}</label>
          <select
            value={hotelStars}
            onChange={(e) => setHotelStars(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">{t('search.any')}</option>
            {[1, 2, 3, 4, 5].map((n) => (
              <option key={n} value={n}>
                {n} {t('results.stars')}
              </option>
            ))}
          </select>
        </div>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="mt-5 w-full rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? t('search.searching') : t('search.searchBtn')}
      </button>
    </form>
  );
}
