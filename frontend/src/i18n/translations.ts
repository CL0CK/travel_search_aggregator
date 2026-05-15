export type Language = 'en' | 'de';

export type TranslationKey =
  | 'app.title'
  | 'app.subtitle'
  | 'search.destination'
  | 'search.origin'
  | 'search.checkIn'
  | 'search.checkOut'
  | 'search.maxPrice'
  | 'search.hotelStars'
  | 'search.any'
  | 'search.searchBtn'
  | 'search.searching'
  | 'search.noResults'
  | 'search.resultsCount'
  | 'results.provider'
  | 'results.price'
  | 'results.rating'
  | 'results.origin'
  | 'results.hotelStars'
  | 'results.flightPrice'
  | 'results.hotelPrice'
  | 'results.from'
  | 'results.stars'
  | 'results.bookBtn'
  | 'ai.openBtn'
  | 'ai.modalTitle'
  | 'ai.placeholder'
  | 'ai.sendBtn'
  | 'ai.thinking'
  | 'ai.error'
  | 'ai.extracted'
  | 'ai.foundResults'
  | 'ai.missingDestination'
  | 'ai.missingOrigin'
  | 'ai.missingDates'
  | 'ai.allSet'
  | 'ai.searching'
  | 'lang.en'
  | 'lang.de'
  | 'pagination.loadMore';

const translations: Record<Language, Record<TranslationKey, string>> = {
  en: {
    'app.title': 'Travel Search',
    'app.subtitle': 'Find the best trips with AI assistance',
    'search.destination': 'Destination',
    'search.origin': 'Origin',
    'search.checkIn': 'Check-in',
    'search.checkOut': 'Check-out',
    'search.maxPrice': 'Max Price (€)',
    'search.hotelStars': 'Hotel Stars',
    'search.any': 'Any',
    'search.searchBtn': 'Search',
    'search.searching': 'Searching...',
    'search.noResults': 'No trips found. Try changing your filters.',
    'search.resultsCount': '{count} trip(s) found',
    'results.provider': 'Provider',
    'results.price': 'Price',
    'results.rating': 'Rating',
    'results.origin': 'Origin',
    'results.hotelStars': 'Stars',
    'results.flightPrice': 'Flight',
    'results.hotelPrice': 'Hotel',
    'results.from': 'From',
    'results.stars': '★',
    'results.bookBtn': 'Book',
    'ai.openBtn': 'AI Search',
    'ai.modalTitle': 'AI Travel Agent',
    'ai.placeholder': 'Describe your trip... (e.g. "I want to go to Paris from London next week")',
    'ai.sendBtn': 'Send',
    'ai.thinking': 'Thinking...',
    'ai.error': 'Sorry, something went wrong. Please try again.',
    'ai.extracted': 'I understood:',
    'ai.foundResults': 'Found {count} trip(s)! Results shown below.',
    'ai.missingDestination': 'Where would you like to go? Please specify a destination city.',
    'ai.missingOrigin': 'Where are you departing from? Please specify your city.',
    'ai.missingDates': 'What dates are you traveling? Please provide check-in and check-out dates.',
    'ai.allSet': 'I have all the information! Searching for trips now...',
    'ai.searching': 'Searching for the best trips...',
    'lang.en': 'EN',
    'lang.de': 'DE',
    'pagination.loadMore': 'Load more',
  },
  de: {
    'app.title': 'Reisesuche',
    'app.subtitle': 'Finde die besten Reisen mit KI-Unterstützung',
    'search.destination': 'Zielort',
    'search.origin': 'Abfahrtsort',
    'search.checkIn': 'Check-in',
    'search.checkOut': 'Check-out',
    'search.maxPrice': 'Max. Preis (€)',
    'search.hotelStars': 'Hotelsterne',
    'search.any': 'Beliebig',
    'search.searchBtn': 'Suchen',
    'search.searching': 'Suche...',
    'search.noResults': 'Keine Reisen gefunden. Versuche andere Filter.',
    'search.resultsCount': '{count} Reise(n) gefunden',
    'results.provider': 'Anbieter',
    'results.price': 'Preis',
    'results.rating': 'Bewertung',
    'results.origin': 'Abfahrt',
    'results.hotelStars': 'Sterne',
    'results.flightPrice': 'Flug',
    'results.hotelPrice': 'Hotel',
    'results.from': 'Ab',
    'results.stars': '★',
    'results.bookBtn': 'Book',
    'ai.openBtn': 'KI-Suche',
    'ai.modalTitle': 'KI Reiseagent',
    'ai.placeholder': 'Beschreibe deine Reise... (z.B. "Ich möchte nächste Woche nach Paris von London reisen")',
    'ai.sendBtn': 'Senden',
    'ai.thinking': 'Denke...',
    'ai.error': 'Entschuldigung, etwas ist schiefgelaufen. Bitte versuche es erneut.',
    'ai.extracted': 'Ich habe verstanden:',
    'ai.foundResults': '{count} Reise(n) gefunden! Ergebnisse unten angezeigt.',
    'ai.missingDestination': 'Wohin möchtest du reisen? Bitte gib ein Ziel an.',
    'ai.missingOrigin': 'Von wo reist du ab? Bitte gib deine Stadt an.',
    'ai.missingDates': 'An welchen Daten reist du? Bitte gib Check-in und Check-out an.',
    'ai.allSet': 'Ich habe alle Informationen! Suche jetzt nach Reisen...',
    'ai.searching': 'Suche nach den besten Reisen...',
    'lang.en': 'EN',
    'lang.de': 'DE',
    'pagination.loadMore': 'Mehr laden',
  },
};

export default translations;
