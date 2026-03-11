"""국가명 → {lat, lng, continent, region} 매핑 (주요 뉴스 등장국 60+)"""

COUNTRY_GEO = {
    # Asia
    "China": {"lat": 35.86, "lng": 104.20, "continent": "Asia", "region": "East Asia"},
    "Japan": {"lat": 36.20, "lng": 138.25, "continent": "Asia", "region": "East Asia"},
    "South Korea": {"lat": 35.91, "lng": 127.77, "continent": "Asia", "region": "East Asia"},
    "North Korea": {"lat": 40.34, "lng": 127.51, "continent": "Asia", "region": "East Asia"},
    "India": {"lat": 20.59, "lng": 78.96, "continent": "Asia", "region": "South Asia"},
    "Pakistan": {"lat": 30.38, "lng": 69.35, "continent": "Asia", "region": "South Asia"},
    "Indonesia": {"lat": -0.79, "lng": 113.92, "continent": "Asia", "region": "Southeast Asia"},
    "Philippines": {"lat": 12.88, "lng": 121.77, "continent": "Asia", "region": "Southeast Asia"},
    "Thailand": {"lat": 15.87, "lng": 100.99, "continent": "Asia", "region": "Southeast Asia"},
    "Vietnam": {"lat": 14.06, "lng": 108.28, "continent": "Asia", "region": "Southeast Asia"},
    "Myanmar": {"lat": 21.91, "lng": 95.96, "continent": "Asia", "region": "Southeast Asia"},
    "Taiwan": {"lat": 23.70, "lng": 120.96, "continent": "Asia", "region": "East Asia"},
    "Israel": {"lat": 31.05, "lng": 34.85, "continent": "Asia", "region": "Middle East"},
    "Iran": {"lat": 32.43, "lng": 53.69, "continent": "Asia", "region": "Middle East"},
    "Iraq": {"lat": 33.22, "lng": 43.68, "continent": "Asia", "region": "Middle East"},
    "Syria": {"lat": 34.80, "lng": 38.99, "continent": "Asia", "region": "Middle East"},
    "Saudi Arabia": {"lat": 23.89, "lng": 45.08, "continent": "Asia", "region": "Middle East"},
    "Turkey": {"lat": 38.96, "lng": 35.24, "continent": "Asia", "region": "Middle East"},
    "Afghanistan": {"lat": 33.94, "lng": 67.71, "continent": "Asia", "region": "South Asia"},
    "Yemen": {"lat": 15.55, "lng": 48.52, "continent": "Asia", "region": "Middle East"},
    "Lebanon": {"lat": 33.85, "lng": 35.86, "continent": "Asia", "region": "Middle East"},
    "United Arab Emirates": {"lat": 23.42, "lng": 53.85, "continent": "Asia", "region": "Middle East"},
    # Europe
    "United Kingdom": {"lat": 55.38, "lng": -3.44, "continent": "Europe", "region": "Western Europe"},
    "France": {"lat": 46.23, "lng": 2.21, "continent": "Europe", "region": "Western Europe"},
    "Germany": {"lat": 51.17, "lng": 10.45, "continent": "Europe", "region": "Western Europe"},
    "Italy": {"lat": 41.87, "lng": 12.57, "continent": "Europe", "region": "Western Europe"},
    "Spain": {"lat": 40.46, "lng": -3.75, "continent": "Europe", "region": "Western Europe"},
    "Ukraine": {"lat": 48.38, "lng": 31.17, "continent": "Europe", "region": "Eastern Europe"},
    "Russia": {"lat": 61.52, "lng": 105.32, "continent": "Europe", "region": "Eastern Europe"},
    "Poland": {"lat": 51.92, "lng": 19.15, "continent": "Europe", "region": "Eastern Europe"},
    "Netherlands": {"lat": 52.13, "lng": 5.29, "continent": "Europe", "region": "Western Europe"},
    "Belgium": {"lat": 50.50, "lng": 4.47, "continent": "Europe", "region": "Western Europe"},
    "Switzerland": {"lat": 46.82, "lng": 8.23, "continent": "Europe", "region": "Western Europe"},
    "Sweden": {"lat": 60.13, "lng": 18.64, "continent": "Europe", "region": "Northern Europe"},
    "Norway": {"lat": 60.47, "lng": 8.47, "continent": "Europe", "region": "Northern Europe"},
    "Greece": {"lat": 39.07, "lng": 21.82, "continent": "Europe", "region": "Southern Europe"},
    # North America
    "United States": {"lat": 37.09, "lng": -95.71, "continent": "NorthAmerica", "region": "North America"},
    "Canada": {"lat": 56.13, "lng": -106.35, "continent": "NorthAmerica", "region": "North America"},
    "Mexico": {"lat": 23.63, "lng": -102.55, "continent": "NorthAmerica", "region": "Central America"},
    "Cuba": {"lat": 21.52, "lng": -77.78, "continent": "NorthAmerica", "region": "Caribbean"},
    # South America
    "Brazil": {"lat": -14.24, "lng": -51.93, "continent": "SouthAmerica", "region": "South America"},
    "Argentina": {"lat": -38.42, "lng": -63.62, "continent": "SouthAmerica", "region": "South America"},
    "Colombia": {"lat": 4.57, "lng": -74.30, "continent": "SouthAmerica", "region": "South America"},
    "Venezuela": {"lat": 6.42, "lng": -66.59, "continent": "SouthAmerica", "region": "South America"},
    "Chile": {"lat": -35.68, "lng": -71.54, "continent": "SouthAmerica", "region": "South America"},
    "Peru": {"lat": -9.19, "lng": -75.02, "continent": "SouthAmerica", "region": "South America"},
    # Africa
    "Nigeria": {"lat": 9.08, "lng": 8.68, "continent": "Africa", "region": "West Africa"},
    "South Africa": {"lat": -30.56, "lng": 22.94, "continent": "Africa", "region": "Southern Africa"},
    "Egypt": {"lat": 26.82, "lng": 30.80, "continent": "Africa", "region": "North Africa"},
    "Ethiopia": {"lat": 9.15, "lng": 40.49, "continent": "Africa", "region": "East Africa"},
    "Kenya": {"lat": -0.02, "lng": 37.91, "continent": "Africa", "region": "East Africa"},
    "Sudan": {"lat": 12.86, "lng": 30.22, "continent": "Africa", "region": "East Africa"},
    "Libya": {"lat": 26.34, "lng": 17.23, "continent": "Africa", "region": "North Africa"},
    "Somalia": {"lat": 5.15, "lng": 46.20, "continent": "Africa", "region": "East Africa"},
    "Congo": {"lat": -4.04, "lng": 21.76, "continent": "Africa", "region": "Central Africa"},
    "Morocco": {"lat": 31.79, "lng": -7.09, "continent": "Africa", "region": "North Africa"},
    # Oceania
    "Australia": {"lat": -25.27, "lng": 133.78, "continent": "Oceania", "region": "Oceania"},
    "New Zealand": {"lat": -40.90, "lng": 174.89, "continent": "Oceania", "region": "Oceania"},
}

# GDELT sourcecountry 값 / NewsData country 코드 등 다양한 키로 조회 가능하도록 별칭 추가
_ALIASES = {
    "US": "United States", "USA": "United States", "U.S.": "United States",
    "UK": "United Kingdom", "Britain": "United Kingdom", "England": "United Kingdom",
    "Korea": "South Korea", "Republic of Korea": "South Korea",
    "UAE": "United Arab Emirates",
    "DRC": "Congo", "Democratic Republic of the Congo": "Congo",
    "Russian Federation": "Russia",
}


def lookup_country(name: str) -> dict | None:
    if not name:
        return None
    name = name.strip()
    if name in COUNTRY_GEO:
        return COUNTRY_GEO[name]
    resolved = _ALIASES.get(name)
    if resolved:
        return COUNTRY_GEO.get(resolved)
    for key in COUNTRY_GEO:
        if key.lower() in name.lower() or name.lower() in key.lower():
            return COUNTRY_GEO[key]
    return None
