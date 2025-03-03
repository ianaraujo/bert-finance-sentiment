import re

MONTHS = {
    '01': ['janeiro', 'jan'],
    '02': ['fevereiro', 'fev'],
    '03': ['março', 'mar'],
    '04': ['abril', 'abr'],
    '05': ['maio', 'mai'],
    '06': ['junho', 'jun'],
    '07': ['julho', 'jul'],
    '08': ['agosto', 'ago'],
    '09': ['setembro', 'set'],
    '10': ['outubro', 'out'],
    '11': ['novembro', 'nov'],
    '12': ['dezembro', 'dez']
}

def match_month(text: str):
    matched_months = []
    
    for numeric_month, month_variations in MONTHS.items():
        for month_name in month_variations:
            if month_name.lower() in text.lower():
                matched_months.append(int(numeric_month))

    if matched_months:
        return f"{max(matched_months):02d}"

    return None

def match_year(text: str):
    year_match = re.search(r'(\d{4})', text)

    if year_match:
        return year_match.group(1)

    return None

def match_trimester(text: str):
    tri_match = re.search(r'(\d)[ºo]?\s*(?:Tri(?:mestre)?)', text, re.IGNORECASE)

    if tri_match:
        tri = tri_match.group(1)
        return {"1": "01", "2": "04", "3": "07", "4": "10"}.get(tri, "01")

    return None

def extract_date(text: str):
    year = match_year(text)
    month = match_month(text)

    if not month:
        month = match_trimester(text)

    if not year or not month:
        return None

    return f"{year}-{month}-01"