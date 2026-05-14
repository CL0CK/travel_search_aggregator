import type { TripRead } from '../types/trip';

interface ResultsProps {
  t: (key: any, params?: any) => string;
  trips: TripRead[];
  loading: boolean;
}

function formatPrice(value: number | null | undefined): string {
  if (value === null || value === undefined) return '—';
  return `€${value.toFixed(2)}`;
}

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '';
  const d = new Date(iso + 'T00:00:00');
  return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
}

export default function Results({ t, trips, loading }: ResultsProps) {
  if (loading) {
    return (
      <div className="mt-6 flex items-center justify-center py-12 text-gray-400">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
      </div>
    );
  }

  if (trips.length === 0) {
    return (
      <div className="mt-6 rounded-xl border border-gray-200 bg-white p-8 text-center text-gray-500">
        {t('search.noResults')}
      </div>
    );
  }

  return (
    <div className="mt-6">
      <p className="mb-3 text-sm text-gray-500">{t('search.resultsCount', { count: trips.length })}</p>
      <div className="space-y-3">
        {trips.map((trip) => (
          <div
            key={trip.id}
            className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md"
          >
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="min-w-0 flex-1">
                <h3 className="text-lg font-semibold text-gray-900">
                  {trip.destination}
                </h3>
                <p className="text-sm text-gray-500">
                  {t('results.from')} {trip.origin ?? '—'}
                </p>
                {(trip.from_airport || trip.to_airport) && (
                  <p className="mt-0.5 text-xs font-medium text-gray-400">
                    {trip.from_airport ?? '?'} → {trip.to_airport ?? '?'}
                  </p>
                )}
                {(trip.check_in || trip.check_out) && (
                  <p className="mt-0.5 text-xs text-gray-400">
                    {formatDate(trip.check_in)} — {formatDate(trip.check_out)}
                  </p>
                )}
              </div>
              <div className="text-right">
                <p className="text-xl font-bold text-blue-600">{formatPrice(trip.price)}</p>
                <p className="text-xs text-gray-400">
                  ✈ {formatPrice(trip.flight_price)} + 🏨 {formatPrice(trip.hotel_price)}
                </p>
              </div>
            </div>

            <div className="mt-3 flex flex-wrap items-center gap-4 text-sm text-gray-600">
              <span>
                {t('results.provider')}: <span className="font-medium">{trip.provider}</span>
              </span>
              <span>
                {t('results.rating')}: <span className="font-medium">{trip.rating.toFixed(1)}</span>
              </span>
              {trip.hotel_stars != null && trip.hotel_stars > 0 && (
                <span>
                  {t('results.hotelStars')}: <span className="font-medium">{'★'.repeat(trip.hotel_stars)}</span>
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
