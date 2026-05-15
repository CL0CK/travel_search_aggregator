import asyncio
import logging

import httpx

from app.core.config import settings
from app.schemas.trip import TripDTO

logger = logging.getLogger(__name__)

BOOKING_HEADERS = {
    "X-RapidAPI-Key": settings.rapidapi_key,
    "X-RapidAPI-Host": "booking-com.p.rapidapi.com",
}

FLIGHT_CODES = {
    "paris": "CDG.AIRPORT",
    "париж": "CDG.AIRPORT",
    "london": "LHR.AIRPORT",
    "лондон": "LHR.AIRPORT",
    "berlin": "BER.AIRPORT",
    "берлин": "BER.AIRPORT",
    "rome": "FCO.AIRPORT",
    "рим": "FCO.AIRPORT",
    "barcelona": "BCN.AIRPORT",
    "барселона": "BCN.AIRPORT",
    "amsterdam": "AMS.AIRPORT",
    "амстердам": "AMS.AIRPORT",
    "madrid": "MAD.AIRPORT",
    "мадрид": "MAD.AIRPORT",
    "istanbul": "IST.AIRPORT",
    "стамбул": "IST.AIRPORT",
    "dubai": "DXB.AIRPORT",
    "дубай": "DXB.AIRPORT",
    "tokyo": "NRT.AIRPORT",
    "токио": "NRT.AIRPORT",
    "bangkok": "BKK.AIRPORT",
    "бангкок": "BKK.AIRPORT",
    "new york": "JFK.AIRPORT",
    "нью-йорк": "JFK.AIRPORT",
    "los angeles": "LAX.AIRPORT",
    "лос-анджелес": "LAX.AIRPORT",
    "miami": "MIA.AIRPORT",
    "майами": "MIA.AIRPORT",
    "chicago": "ORD.AIRPORT",
    "чикаго": "ORD.AIRPORT",
    "singapore": "SIN.AIRPORT",
    "сингапур": "SIN.AIRPORT",
    "seoul": "ICN.AIRPORT",
    "сеул": "ICN.AIRPORT",
    "beijing": "PEK.AIRPORT",
    "пекин": "PEK.AIRPORT",
    "cairo": "CAI.AIRPORT",
    "каир": "CAI.AIRPORT",
    "sydney": "SYD.AIRPORT",
    "сидней": "SYD.AIRPORT",
    "dublin": "DUB.AIRPORT",
    "даблин": "DUB.AIRPORT",
    "lisbon": "LIS.AIRPORT",
    "лисабон": "LIS.AIRPORT",
    "prague": "PRG.AIRPORT",
    "прага": "PRG.AIRPORT",
    "vienna": "VIE.AIRPORT",
    "вена": "VIE.AIRPORT",
    "budapest": "BUD.AIRPORT",
    "будапешт": "BUD.AIRPORT",
    "athens": "ATH.AIRPORT",
    "афины": "ATH.AIRPORT",
    "zurich": "ZRH.AIRPORT",
    "цюрих": "ZRH.AIRPORT",
    "bali": "DPS.AIRPORT",
    "бали": "DPS.AIRPORT",
    "maldives": "MLE.AIRPORT",
    "мальдивы": "MLE.AIRPORT",
    "kyiv": "KBP.AIRPORT",
    "киев": "KBP.AIRPORT",
    "warsaw": "WAW.AIRPORT",
    "варшава": "WAW.AIRPORT",
    "helsinki": "HEL.AIRPORT",
    "хельсинки": "HEL.AIRPORT",
    "stockholm": "ARN.AIRPORT",
    "стокгольм": "ARN.AIRPORT",
    "copenhagen": "CPH.AIRPORT",
    "копенгаген": "CPH.AIRPORT",
    "oslo": "OSL.AIRPORT",
    "осло": "OSL.AIRPORT",
    "tallinn": "TLL.AIRPORT",
    "таллин": "TLL.AIRPORT",
    "tartu": "TAY.AIRPORT",
    "тарту": "TAY.AIRPORT",
    "estonia": "TLL.AIRPORT",
    "эстония": "TLL.AIRPORT",
    "france": "CDG.AIRPORT",
    "франция": "CDG.AIRPORT",
    "spain": "BCN.AIRPORT",
    "испания": "BCN.AIRPORT",
    "italy": "FCO.AIRPORT",
    "италия": "FCO.AIRPORT",
    "germany": "BER.AIRPORT",
    "германия": "BER.AIRPORT",
    "japan": "NRT.AIRPORT",
    "япония": "NRT.AIRPORT",
    "thailand": "BKK.AIRPORT",
    "таиланд": "BKK.AIRPORT",
    "turkey": "IST.AIRPORT",
    "турция": "TUR.AIRPORT",
    "uae": "DXB.AIRPORT",
    "оаэ": "DXB.AIRPORT",
    "ukraine": "KBP.AIRPORT",
    "украина": "KBP.AIRPORT",
    "china": "PEK.AIRPORT",
    "китай": "PEK.AIRPORT",
    "india": "BOM.AIRPORT",
    "индия": "BOM.AIRPORT",
    "australia": "SYD.AIRPORT",
    "австралия": "SYD.AIRPORT",
    "england": "LHR.AIRPORT",
    "англия": "LHR.AIRPORT",
    "mumbai": "BOM.AIRPORT",
    "мумбаи": "BOM.AIRPORT",
    "delhi": "DEL.AIRPORT",
    "дельхи": "DEL.AIRPORT",
    "hong kong": "HKG.AIRPORT",
    "гонконг": "HKG.AIRPORT",
    "shanghai": "PVG.AIRPORT",
    "шанхай": "PVG.AIRPORT",
    "san francisco": "SFO.AIRPORT",
    "сан-франциско": "SFO.AIRPORT",
    "las vegas": "LAS.AIRPORT",
    "лас-вегас": "LAS.AIRPORT",
    "toronto": "YYZ.AIRPORT",
    "торонто": "YYZ.AIRPORT",
    "vancouver": "YVR.AIRPORT",
    "ванкувер": "YVR.AIRPORT",
    "brussels": "BRU.AIRPORT",
    "брюссель": "BRU.AIRPORT",
    "geneva": "GVA.AIRPORT",
    "женева": "GVA.AIRPORT",
    "malta": "MLA.AIRPORT",
    "мальта": "MLA.AIRPORT",
    "cyprus": "LCA.AIRPORT",
    "кипр": "LCA.AIRPORT",
    "iceland": "KEF.AIRPORT",
    "исландия": "KEF.AIRPORT",
    "norway": "OSL.AIRPORT",
    "норвегия": "OSL.AIRPORT",
    "sweden": "ARN.AIRPORT",
    "швеция": "ARN.AIRPORT",
    "hawaii": "HNL.AIRPORT",
    "гавайи": "HNL.AIRPORT",
    "santorini": "JTR.AIRPORT",
    "санторини": "JTR.AIRPORT",
    "melbourne": "MEL.AIRPORT",
    "мельбурн": "MEL.AIRPORT",
    "cape town": "CPT.AIRPORT",
    "кептаун": "CPT.AIRPORT",
    "rio de janeiro": "GIG.AIRPORT",
    "рио-де-жанейро": "GIG.AIRPORT",
    "buenos aires": "EZE.AIRPORT",
    "буэнос-айрес": "EZE.AIRPORT",
    "sao paulo": "GRU.AIRPORT",
    "сао-пауло": "GRU.AIRPORT",
}

_dest_id_cache = {}


def _get_flight_code(city: str) -> str | None:
    return FLIGHT_CODES.get(city.lower().strip())


async def _get_booking_dest_id(city: str) -> tuple:
    if city in _dest_id_cache:
        return _dest_id_cache[city]

    url = "https://booking-com.p.rapidapi.com/v1/hotels/locations"
    params = {"name": city, "locale": "en-gb"}

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params, headers=BOOKING_HEADERS)

    if resp.status_code != 200:
        logger.warning(f"Booking.com locations error: {resp.status_code}")
        _dest_id_cache[city] = (None, None)
        return None, None

    locations = resp.json()
    if not locations:
        logger.warning(f"Booking.com: no location found for '{city}'")
        _dest_id_cache[city] = (None, None)
        return None, None

    loc = locations[0]
    dest_id = loc.get("dest_id")
    dest_type = loc.get("dest_type", "city")
    _dest_id_cache[city] = (dest_id, dest_type)
    return dest_id, dest_type


async def _search_flights(
    origin_city: str,
    dest_city: str,
    check_in: str,
    check_out: str,
) -> list[dict]:
    from_code = _get_flight_code(origin_city)
    to_code = _get_flight_code(dest_city)

    if not from_code or not to_code:
        logger.warning(f"Booking.com: flight codes not found: origin={origin_city}, dest={dest_city}")
        return []

    url = "https://booking-com.p.rapidapi.com/v1/flights/search"
    params = {
        "from_code": from_code,
        "to_code": to_code,
        "depart_date": check_in,
        "return_date": check_out,
        "adults": 1,
        "cabin_class": "ECONOMY",
        "currency": "EUR",
        "locale": "en-gb",
        "order_by": "BEST",
        "flight_type": "ONEWAY",
        "page_number": 0,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url, params=params, headers=BOOKING_HEADERS)

    if resp.status_code != 200:
        logger.warning(f"Booking.com flight error: {resp.status_code} {resp.text[:200]}")
        return []

    data = resp.json()
    if "detail" in data:
        logger.warning(f"Booking.com flight: {data['detail']}")
        return []

    flight_items = data.get("flightOffers", [])
    flights = []

    for item in flight_items[:10]:
        pb = item.get("priceBreakdown", {})
        total = pb.get("total", {})
        units = total.get("units", 0)
        nanos = total.get("nanos", 0)
        price = units + (nanos / 1_000_000_000)

        segments = item.get("segments", [])
        airline = "Unknown"
        if segments:
            legs = segments[0].get("legs", [])
            if legs:
                carriers = legs[0].get("carriers", [])
                if carriers:
                    airline = carriers[0]

        flights.append({
            "price": float(price) if price else 0,
            "airline": airline,
            "origin": origin_city,
            "destination": dest_city,
        })

    logger.info(f"Booking.com flights: found {len(flights)} offers")
    return flights


async def _search_hotels(
    dest_city: str,
    check_in: str,
    check_out: str,
    min_stars: int | None = None,
) -> list[dict]:
    dest_id, dest_type = await _get_booking_dest_id(dest_city)
    if not dest_id:
        return []

    url = "https://booking-com.p.rapidapi.com/v1/hotels/search"
    params = {
        "locale": "en-gb",
        "dest_id": dest_id,
        "dest_type": dest_type,
        "checkin_date": check_in,
        "checkout_date": check_out,
        "room_number": 1,
        "adults_number": 1,
        "filter_by_currency": "EUR",
        "order_by": "popularity",
        "units": "metric",
        "page_number": 0,
    }

    if min_stars:
        params["categories_filter_ids"] = f"class::{min_stars}"

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url, params=params, headers=BOOKING_HEADERS)

    if resp.status_code != 200:
        logger.warning(f"Booking.com hotel error: {resp.status_code} {resp.text[:200]}")
        return []

    data = resp.json()
    hotels_raw = data.get("result", [])
    hotels = []

    for hotel in hotels_raw[:10]:
        price = hotel.get("min_total_price", 0)
        stars = hotel.get("class", 0) or hotel.get("star_rating", 0)
        review = hotel.get("review_score", 0)

        if min_stars and stars and int(stars) < min_stars:
            continue

        hotels.append({
            "name": hotel.get("hotel_name", "Unknown"),
            "price": float(price) if price else 0,
            "stars": int(stars) if stars else 0,
            "rating": float(review) / 2.0 if review else 0,
            "destination": dest_city,
            "booking_url": hotel.get("url"),
        })

    logger.info(f"Booking.com hotels: found {len(hotels)} offers")
    return hotels


async def provider_rapidapi(
    origin: str,
    destination: str,
    check_in: str,
    check_out: str,
    hotel_stars: int | None = None,
) -> list[TripDTO]:
    if not settings.rapidapi_key:
        logger.error("RapidAPI key not configured")
        return []

    flights, hotels = await asyncio.gather(
        _search_flights(origin, destination, check_in, check_out),
        _search_hotels(destination, check_in, check_out, min_stars=hotel_stars),
    )

    if not flights or not hotels:
        logger.warning(f"No results: {len(flights)} flights, {len(hotels)} hotels")
        return []

    packages = []
    for flight in flights:
        for hotel in hotels:
            total_price = flight["price"] + hotel["price"]
            packages.append({
                "destination": hotel["name"],
                "price": total_price,
                "rating": hotel["rating"],
                "provider": "Booking.com",
                "origin": origin,
                "hotel_stars": hotel["stars"],
                "flight_price": flight["price"],
                "hotel_price": hotel["price"],
                "booking_url": hotel.get("booking_url"),
            })

    logger.info(f"Booking.com packages: {len(packages)} combinations")
    return packages
