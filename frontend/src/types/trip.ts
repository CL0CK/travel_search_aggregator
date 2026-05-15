export interface TripRead {
  id: string;
  destination: string;
  price: number;
  rating: number;
  provider: string;
  created_at: string;
  origin: string | null;
  hotel_stars: number | null;
  flight_price: number | null;
  hotel_price: number | null;
  check_in: string | null;
  check_out: string | null;
  from_airport: string | null;
  to_airport: string | null;
  booking_url: string | null;
}

export interface SearchAIResponse {
  destination: string;
  origin: string | null;
  budget: number | null;
  results: TripRead[];
}

export interface SearchParams {
  destination: string;
  origin: string;
  check_in: string;
  check_out: string;
  max_price?: number;
  hotel_stars?: number;
}

export interface ExtractionParams {
  destination: string | null;
  origin: string | null;
  check_in: string | null;
  check_out: string | null;
  budget: number | null;
}
