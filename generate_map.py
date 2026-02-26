import openpyxl, json, re, random

wb = openpyxl.load_workbook('florida_gated_communities_no55plus.xlsx')
ws = wb.active

coords = {
    'Altamonte Springs': [28.6611, -81.3656],
    'Ave Maria': [26.4045, -81.5237],
    'Bonita Springs': [26.3398, -81.7787],
    'Citrus Hills': [28.8697, -82.4732],
    'Clermont': [28.5494, -81.7729],
    'Coconut Grove': [25.7274, -80.2386],
    'Coral Gables': [25.7215, -80.2684],
    'Dade City': [28.3653, -82.1943],
    'DeBary': [28.8836, -81.3317],
    'Destin': [30.3935, -86.4958],
    'Dr. Phillips': [28.4472, -81.5006],
    'Englewood': [26.9628, -82.3526],
    'Estero': [26.4384, -81.8073],
    'Fort Lauderdale': [26.1224, -80.1373],
    'Fort Myers': [26.6406, -81.8723],
    'Golden Beach': [25.9740, -80.1220],
    'Jacksonville': [30.3322, -81.6557],
    'Jupiter': [26.9342, -80.0942],
    'Key Biscayne': [25.6906, -80.1621],
    'Key Largo': [25.0865, -80.4473],
    'Lake Mary': [28.7581, -81.3176],
    'Lake Mary area': [28.7681, -81.3076],
    'Lakewood Ranch': [27.4082, -82.3896],
    'Lakewood Ranch/Bradenton': [27.3952, -82.4200],
    'Largo': [27.9095, -82.7873],
    'Longwood': [28.7028, -81.3395],
    'Lutz': [28.1536, -82.4593],
    'Miami': [25.7617, -80.1918],
    'Miami Beach': [25.7907, -80.1300],
    'Naples': [26.1420, -81.7948],
    'Naples (North)': [26.2285, -81.7948],
    'Near Fort Lauderdale': [26.1524, -80.1573],
    'New Tampa': [28.1553, -82.3480],
    'Orlando': [28.5383, -81.3792],
    'Ormond Beach': [29.2858, -81.0559],
    'Oviedo': [28.6700, -81.2081],
    'Palm Beach Gardens': [26.8237, -80.1217],
    'Palm City': [27.1670, -80.2678],
    'Palm Coast': [29.5855, -81.2079],
    'Palmetto Bay': [25.6179, -80.3331],
    'Panama City Beach': [30.1766, -85.8055],
    'Ponte Vedra': [30.2391, -81.3870],
    'Port St. Lucie': [27.2730, -80.3582],
    'Sandestin': [30.3835, -86.3127],
    'Sanford': [28.8014, -81.2731],
    'Santa Rosa Beach': [30.3863, -86.2225],
    'Sarasota': [27.3364, -82.5307],
    'Seminole': [27.8450, -82.7779],
    'South Tampa': [27.9106, -82.4641],
    'St. Augustine': [29.8943, -81.3145],
    'St. Johns': [30.0960, -81.6020],
    'Stuart': [27.1975, -80.2520],
    'Tampa': [27.9506, -82.4572],
    'West Palm Beach': [26.7153, -80.0534],
    'Windermere': [28.4994, -81.5206],
    'Winter Garden': [28.5653, -81.5862],
    'Winter Springs': [28.6989, -81.2700],
}

# Map community city → county (for tax/crime lookups in popup)
city_to_county = {
    'Naples': 'Collier', 'Naples (North)': 'Collier', 'Ave Maria': 'Collier',
    'Bonita Springs': 'Lee', 'Estero': 'Lee', 'Fort Myers': 'Lee',
    'Cape Coral': 'Lee',
    'Sarasota': 'Sarasota', 'Englewood': 'Sarasota',
    'Lakewood Ranch': 'Manatee', 'Lakewood Ranch/Bradenton': 'Manatee',
    'Bradenton': 'Manatee',
    'Tampa': 'Hillsborough', 'South Tampa': 'Hillsborough',
    'New Tampa': 'Hillsborough',
    'Lutz': 'Pasco', 'Dade City': 'Pasco',
    'St. Johns': 'St. Johns', 'St. Augustine': 'St. Johns',
    'Ponte Vedra': 'St. Johns',
    'Jacksonville': 'Duval',
    'Orlando': 'Orange', 'Dr. Phillips': 'Orange', 'Windermere': 'Orange',
    'Winter Garden': 'Orange',
    'Altamonte Springs': 'Seminole', 'Winter Springs': 'Seminole',
    'Longwood': 'Seminole', 'Lake Mary': 'Seminole', 'Lake Mary area': 'Seminole',
    'Oviedo': 'Seminole', 'Sanford': 'Seminole',
    'Clermont': 'Lake',
    'Palm Beach Gardens': 'Palm Beach', 'West Palm Beach': 'Palm Beach',
    'Jupiter': 'Palm Beach',
    'Fort Lauderdale': 'Broward', 'Near Fort Lauderdale': 'Broward',
    'Miami': 'Miami-Dade', 'Miami Beach': 'Miami-Dade',
    'Coconut Grove': 'Miami-Dade', 'Coral Gables': 'Miami-Dade',
    'Key Biscayne': 'Miami-Dade', 'Palmetto Bay': 'Miami-Dade',
    'Golden Beach': 'Miami-Dade',
    'Key Largo': 'Monroe',
    'Port St. Lucie': 'St. Lucie', 'Palm City': 'Martin', 'Stuart': 'Martin',
    'Destin': 'Okaloosa', 'Sandestin': 'Walton',
    'Santa Rosa Beach': 'Walton', 'Panama City Beach': 'Bay',
    'Largo': 'Pinellas', 'Seminole': 'Pinellas',
    'Citrus Hills': 'Citrus',
    'Ormond Beach': 'Volusia',
    'Palm Coast': 'Flagler',
    'DeBary': 'Volusia',
}

def parse_price(price_str):
    if not price_str:
        return None, None
    s = str(price_str).replace('$','').strip()
    parts = re.split(r'[^\w\.+KkMm]+', s)
    parts = [p.strip() for p in parts if p.strip()]
    def to_k(val):
        val = val.replace('+','').strip()
        if 'M' in val.upper():
            return float(val.upper().replace('M','')) * 1000
        elif 'K' in val.upper():
            return float(val.upper().replace('K',''))
        else:
            return float(val) / 1000
    try:
        if len(parts) >= 2:
            return to_k(parts[0]), to_k(parts[-1])
        elif len(parts) == 1:
            v = to_k(parts[0])
            return v, v
    except:
        pass
    return None, None

communities = []
for row in ws.iter_rows(min_row=5, values_only=True):
    name, city, typ, amenities, price, security = row
    if not name or str(name).startswith('===') or not city:
        continue
    coord = coords.get(city)
    if not coord:
        continue
    min_p, max_p = parse_price(price)
    random.seed(hash(str(name)))
    lat = coord[0] + random.uniform(-0.009, 0.009)
    lng = coord[1] + random.uniform(-0.012, 0.012)
    communities.append({
        'name': str(name),
        'city': str(city),
        'county': city_to_county.get(str(city), ''),
        'type': str(typ) if typ else 'Gated',
        'amenities': str(amenities) if amenities else '',
        'price': str(price) if price else 'N/A',
        'security': str(security) if security else '',
        'lat': round(lat, 5),
        'lng': round(lng, 5),
        'minPrice': min_p,
        'maxPrice': max_p,
    })

# ── Election data (FIPS → percentages) ────────────────────────────────────
election_data = {
    '12001': {'name':'Alachua',       'r24':38.77,'d24':59.74,'r20':35.7,'d20':62.9},
    '12003': {'name':'Baker',         'r24':86.31,'d24':13.23,'r20':84.7,'d20':14.5},
    '12005': {'name':'Bay',           'r24':73.12,'d24':25.77,'r20':71.1,'d20':27.5},
    '12007': {'name':'Bradford',      'r24':78.38,'d24':21.15,'r20':75.8,'d20':23.2},
    '12009': {'name':'Brevard',       'r24':59.91,'d24':39.07,'r20':57.6,'d20':41.2},
    '12011': {'name':'Broward',       'r24':41.05,'d24':58.01,'r20':34.8,'d20':64.6},
    '12013': {'name':'Calhoun',       'r24':83.49,'d24':15.88,'r20':80.8,'d20':18.5},
    '12015': {'name':'Charlotte',     'r24':66.69,'d24':32.71,'r20':63.0,'d20':36.4},
    '12017': {'name':'Citrus',        'r24':72.64,'d24':26.75,'r20':70.1,'d20':29.1},
    '12019': {'name':'Clay',          'r24':69.17,'d24':29.91,'r20':67.9,'d20':30.8},
    '12021': {'name':'Collier',       'r24':66.22,'d24':33.15,'r20':62.0,'d20':37.4},
    '12023': {'name':'Columbia',      'r24':74.74,'d24':24.56,'r20':72.1,'d20':27.0},
    '12025': {'name':'Miami-Dade',    'r24':55.35,'d24':43.90,'r20':46.1,'d20':53.4},
    '12027': {'name':'DeSoto',        'r24':71.17,'d24':28.23,'r20':65.7,'d20':33.6},
    '12029': {'name':'Dixie',         'r24':84.93,'d24':14.52,'r20':82.8,'d20':16.7},
    '12031': {'name':'Duval',         'r24':50.14,'d24':48.67,'r20':47.4,'d20':51.2},
    '12033': {'name':'Escambia',      'r24':59.23,'d24':39.69,'r20':56.7,'d20':41.6},
    '12035': {'name':'Flagler',       'r24':63.80,'d24':35.56,'r20':60.0,'d20':39.3},
    '12037': {'name':'Franklin',      'r24':71.49,'d24':27.67,'r20':68.3,'d20':31.0},
    '12039': {'name':'Gadsden',       'r24':34.27,'d24':64.95,'r20':31.4,'d20':68.0},
    '12041': {'name':'Gilchrist',     'r24':83.58,'d24':15.55,'r20':81.5,'d20':17.6},
    '12043': {'name':'Glades',        'r24':76.42,'d24':23.15,'r20':72.8,'d20':26.7},
    '12045': {'name':'Gulf',          'r24':76.85,'d24':22.65,'r20':74.9,'d20':24.3},
    '12047': {'name':'Hamilton',      'r24':69.14,'d24':30.12,'r20':65.4,'d20':33.7},
    '12049': {'name':'Hardee',        'r24':77.81,'d24':21.50,'r20':72.2,'d20':27.1},
    '12051': {'name':'Hendry',        'r24':68.74,'d24':30.43,'r20':61.1,'d20':38.1},
    '12053': {'name':'Hernando',      'r24':68.16,'d24':31.11,'r20':64.6,'d20':34.4},
    '12055': {'name':'Highlands',     'r24':70.09,'d24':29.34,'r20':66.8,'d20':32.5},
    '12057': {'name':'Hillsborough',  'r24':50.90,'d24':47.84,'r20':46.0,'d20':52.9},
    '12059': {'name':'Holmes',        'r24':89.87,'d24': 9.67,'r20':89.1,'d20':10.2},
    '12061': {'name':'Indian River',  'r24':63.36,'d24':36.01,'r20':60.4,'d20':38.8},
    '12063': {'name':'Jackson',       'r24':72.74,'d24':26.66,'r20':69.1,'d20':30.2},
    '12065': {'name':'Jefferson',     'r24':58.94,'d24':40.33,'r20':53.0,'d20':46.1},
    '12067': {'name':'Lafayette',     'r24':87.75,'d24':11.74,'r20':85.5,'d20':13.9},
    '12069': {'name':'Lake',          'r24':61.95,'d24':37.28,'r20':59.6,'d20':39.5},
    '12071': {'name':'Lee',           'r24':63.86,'d24':35.47,'r20':59.2,'d20':40.0},
    '12073': {'name':'Leon',          'r24':38.52,'d24':60.28,'r20':35.3,'d20':63.5},
    '12075': {'name':'Levy',          'r24':74.85,'d24':24.59,'r20':72.4,'d20':26.8},
    '12077': {'name':'Liberty',       'r24':83.04,'d24':16.22,'r20':79.9,'d20':19.5},
    '12079': {'name':'Madison',       'r24':64.15,'d24':35.29,'r20':59.4,'d20':39.9},
    '12081': {'name':'Manatee',       'r24':61.39,'d24':37.87,'r20':57.6,'d20':41.6},
    '12083': {'name':'Marion',        'r24':65.47,'d24':33.83,'r20':62.5,'d20':36.6},
    '12085': {'name':'Martin',        'r24':65.24,'d24':34.12,'r20':62.0,'d20':37.4},
    '12086': {'name':'Miami-Dade',    'r24':55.35,'d24':43.90,'r20':46.1,'d20':53.4},
    '12087': {'name':'Monroe',        'r24':58.80,'d24':40.46,'r20':53.5,'d20':45.6},
    '12089': {'name':'Nassau',        'r24':73.06,'d24':26.12,'r20':72.4,'d20':26.5},
    '12091': {'name':'Okaloosa',      'r24':70.67,'d24':28.23,'r20':68.6,'d20':29.4},
    '12093': {'name':'Okeechobee',    'r24':76.69,'d24':22.86,'r20':71.9,'d20':27.5},
    '12095': {'name':'Orange',        'r24':42.54,'d24':56.13,'r20':37.9,'d20':61.0},
    '12097': {'name':'Osceola',       'r24':50.19,'d24':48.74,'r20':42.6,'d20':56.4},
    '12099': {'name':'Palm Beach',    'r24':49.19,'d24':49.95,'r20':43.3,'d20':56.1},
    '12101': {'name':'Pasco',         'r24':62.10,'d24':36.88,'r20':59.5,'d20':39.4},
    '12103': {'name':'Pinellas',      'r24':52.12,'d24':46.89,'r20':49.3,'d20':49.6},
    '12105': {'name':'Polk',          'r24':59.91,'d24':39.23,'r20':56.7,'d20':42.3},
    '12107': {'name':'Putnam',        'r24':73.61,'d24':25.79,'r20':70.1,'d20':28.9},
    '12109': {'name':'St. Johns',     'r24':65.21,'d24':33.86,'r20':62.8,'d20':36.2},
    '12111': {'name':'St. Lucie',     'r24':54.17,'d24':45.11,'r20':50.4,'d20':48.9},
    '12113': {'name':'Santa Rosa',    'r24':74.99,'d24':24.05,'r20':72.4,'d20':25.8},
    '12115': {'name':'Sarasota',      'r24':58.74,'d24':40.55,'r20':54.8,'d20':44.4},
    '12117': {'name':'Seminole',      'r24':51.13,'d24':47.58,'r20':48.0,'d20':50.8},
    '12119': {'name':'Sumter',        'r24':68.56,'d24':30.94,'r20':67.9,'d20':31.7},
    '12121': {'name':'Suwannee',      'r24':80.22,'d24':19.26,'r20':77.9,'d20':21.3},
    '12123': {'name':'Taylor',        'r24':79.56,'d24':19.92,'r20':76.5,'d20':22.7},
    '12125': {'name':'Union',         'r24':83.84,'d24':15.58,'r20':82.2,'d20':16.9},
    '12127': {'name':'Volusia',       'r24':60.45,'d24':38.69,'r20':56.5,'d20':42.5},
    '12129': {'name':'Wakulla',       'r24':71.75,'d24':27.40,'r20':70.0,'d20':29.1},
    '12131': {'name':'Walton',        'r24':78.57,'d24':20.74,'r20':75.4,'d20':23.7},
    '12133': {'name':'Washington',    'r24':82.41,'d24':17.01,'r20':80.1,'d20':19.0},
}

# ── Crime data (FIPS → violent crimes per 100k) ────────────────────────────
# Source: FDLE via FLHealthCHARTS.gov, 2024
crime_data = {
    '12001': {'name':'Alachua',       'violent': 205.1},
    '12003': {'name':'Baker',         'violent': 215.0},
    '12005': {'name':'Bay',           'violent': 265.9},
    '12007': {'name':'Bradford',      'violent': 173.3},
    '12009': {'name':'Brevard',       'violent': 129.3},
    '12011': {'name':'Broward',       'violent': 135.1},
    '12013': {'name':'Calhoun',       'violent': 180.6},
    '12015': {'name':'Charlotte',     'violent':  60.2},
    '12017': {'name':'Citrus',        'violent':  76.2},
    '12019': {'name':'Clay',          'violent':  54.2},
    '12021': {'name':'Collier',       'violent':  51.9},
    '12023': {'name':'Columbia',      'violent': 286.9},
    '12025': {'name':'Miami-Dade',    'violent': 194.2},
    '12027': {'name':'DeSoto',        'violent': 250.8},
    '12029': {'name':'Dixie',         'violent': 206.1},
    '12031': {'name':'Duval',         'violent': 174.9},
    '12033': {'name':'Escambia',      'violent': 218.9},
    '12035': {'name':'Flagler',       'violent':  92.1},
    '12037': {'name':'Franklin',      'violent': 196.8},
    '12039': {'name':'Gadsden',       'violent': 143.6},
    '12041': {'name':'Gilchrist',     'violent': 113.4},
    '12043': {'name':'Glades',        'violent': 180.9},
    '12045': {'name':'Gulf',          'violent': 114.8},
    '12047': {'name':'Hamilton',      'violent': 232.3},
    '12049': {'name':'Hardee',        'violent': 225.9},
    '12051': {'name':'Hendry',        'violent': 237.4},
    '12053': {'name':'Hernando',      'violent': 117.9},
    '12055': {'name':'Highlands',     'violent': 155.6},
    '12057': {'name':'Hillsborough',  'violent': 168.6},
    '12059': {'name':'Holmes',        'violent': 170.2},
    '12061': {'name':'Indian River',  'violent': 135.7},
    '12063': {'name':'Jackson',       'violent': 107.7},
    '12065': {'name':'Jefferson',     'violent': 147.3},
    '12067': {'name':'Lafayette',     'violent':  85.3},
    '12069': {'name':'Lake',          'violent': 104.4},
    '12071': {'name':'Lee',           'violent':  83.7},
    '12073': {'name':'Leon',          'violent': 179.1},
    '12075': {'name':'Levy',          'violent': 139.1},
    '12077': {'name':'Liberty',       'violent':  87.4},
    '12079': {'name':'Madison',       'violent': 234.3},
    '12081': {'name':'Manatee',       'violent': 120.5},
    '12083': {'name':'Marion',        'violent': 161.4},
    '12085': {'name':'Martin',        'violent':  81.4},
    '12086': {'name':'Miami-Dade',    'violent': 194.2},
    '12087': {'name':'Monroe',        'violent': 170.3},
    '12089': {'name':'Nassau',        'violent':  82.3},
    '12091': {'name':'Okaloosa',      'violent': 108.1},
    '12093': {'name':'Okeechobee',    'violent': 216.5},
    '12095': {'name':'Orange',        'violent': 202.8},
    '12097': {'name':'Osceola',       'violent': 147.2},
    '12099': {'name':'Palm Beach',    'violent': 107.3},
    '12101': {'name':'Pasco',         'violent': 107.5},
    '12103': {'name':'Pinellas',      'violent': 137.3},
    '12105': {'name':'Polk',          'violent': 169.0},
    '12107': {'name':'Putnam',        'violent': 231.1},
    '12109': {'name':'St. Johns',     'violent':  55.6},
    '12111': {'name':'St. Lucie',     'violent': 133.4},
    '12113': {'name':'Santa Rosa',    'violent':  90.1},
    '12115': {'name':'Sarasota',      'violent':  78.2},
    '12117': {'name':'Seminole',      'violent':  95.6},
    '12119': {'name':'Sumter',        'violent':  76.1},
    '12121': {'name':'Suwannee',      'violent': 187.1},
    '12123': {'name':'Taylor',        'violent': 219.9},
    '12125': {'name':'Union',         'violent': 109.4},
    '12127': {'name':'Volusia',       'violent': 179.8},
    '12129': {'name':'Wakulla',       'violent':  94.5},
    '12131': {'name':'Walton',        'violent': 117.5},
    '12133': {'name':'Washington',    'violent': 152.0},
}

# ── Property tax data (county name → effective rate %) ─────────────────────
# Source: SmartAsset.com, compiled from county assessor records
tax_data = {
    'Alachua': 0.92, 'Bay': 0.59, 'Brevard': 0.70, 'Broward': 0.94,
    'Charlotte': 0.84, 'Citrus': 0.61, 'Clay': 0.68, 'Collier': 0.57,
    'Columbia': 0.69, 'Duval': 0.77, 'Escambia': 0.57, 'Flagler': 0.77,
    'Hernando': 0.65, 'Highlands': 0.66, 'Hillsborough': 0.82,
    'Indian River': 0.66, 'Lake': 0.79, 'Lee': 0.78, 'Leon': 0.75,
    'Manatee': 0.77, 'Marion': 0.73, 'Martin': 0.70, 'Miami-Dade': 0.76,
    'Monroe': 0.52, 'Nassau': 0.68, 'Okaloosa': 0.58, 'Orange': 0.75,
    'Osceola': 0.78, 'Palm Beach': 0.83, 'Pasco': 0.75, 'Pinellas': 0.67,
    'Polk': 0.74, 'Putnam': 0.84, 'St. Johns': 0.72, 'St. Lucie': 1.00,
    'Santa Rosa': 0.59, 'Sarasota': 0.74, 'Seminole': 0.65, 'Sumter': 0.74,
    'Volusia': 0.76, 'Walton': 0.53,
    # Estimates for remaining counties based on regional averages
    'Baker': 0.67, 'Bradford': 0.76, 'Calhoun': 0.59, 'DeSoto': 0.80,
    'Dixie': 0.65, 'Franklin': 0.55, 'Gadsden': 0.80, 'Gilchrist': 0.65,
    'Glades': 0.65, 'Gulf': 0.58, 'Hamilton': 0.73, 'Hardee': 0.79,
    'Hendry': 0.80, 'Holmes': 0.57, 'Jackson': 0.65, 'Jefferson': 0.72,
    'Lafayette': 0.60, 'Levy': 0.65, 'Liberty': 0.55, 'Madison': 0.70,
    'Okeechobee': 0.80, 'Suwannee': 0.73, 'Taylor': 0.63, 'Union': 0.65,
    'Wakulla': 0.75, 'Washington': 0.60,
}

# FIPS → tax rate lookup
tax_fips = {}
county_name_to_fips = {v['name']: k for k,v in election_data.items() if k not in ('12025',)}
for county, rate in tax_data.items():
    fips = county_name_to_fips.get(county)
    if fips:
        tax_fips[fips] = {'name': county, 'rate': rate}
    # Miami-Dade dual FIPS
    if county == 'Miami-Dade':
        tax_fips['12025'] = {'name': county, 'rate': rate}
        tax_fips['12086'] = {'name': county, 'rate': rate}

data_json      = json.dumps(communities)
election_json  = json.dumps(election_data)
crime_json     = json.dumps(crime_data)
tax_json       = json.dumps(tax_fips)
ctax_json      = json.dumps(tax_data)   # keyed by county name for popups

html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Florida Gated Communities Map</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css"/>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/nouislider@15.7.1/dist/nouislider.min.css"/>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', sans-serif; background: #1a1a2e; color: #eee; height: 100vh; overflow: hidden; display: flex; flex-direction: column; }

/* ── Header ──────────────────────────────────────────────────────────────── */
#header {
  background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
  padding: 10px 18px 8px;
  display: flex; flex-direction: column; gap: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.5); z-index: 1000;
}
#header-row1 { display: flex; align-items: center; gap: 18px; flex-wrap: wrap; }
#header-row2 { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 8px; }

#header h1 { font-size: 1.1rem; font-weight: 700; color: #e94560; white-space: nowrap; flex-shrink: 0; }
#header h1 span { color: #fff; }

.ctrl-group { display: flex; flex-direction: column; gap: 3px; }
.ctrl-label { font-size: 0.65rem; font-weight: 600; color: #718096; text-transform: uppercase; letter-spacing: 0.8px; }

.noUi-connect { background: #e94560; }
.noUi-handle { background: #fff; border: 2px solid #e94560; border-radius: 50%; box-shadow: 0 0 5px rgba(233,69,96,.5); cursor: pointer; }
.noUi-handle::before, .noUi-handle::after { display: none; }
.noUi-target { background: #2d3748; border: none; box-shadow: none; height: 5px; }

/* Filter chips */
.chip-row { display: flex; gap: 4px; flex-wrap: wrap; }
.chip {
  padding: 3px 8px; border-radius: 20px; border: 1.5px solid;
  font-size: 0.65rem; font-weight: 600; cursor: pointer; transition: all .18s; background: transparent;
  white-space: nowrap;
}
.elec-btn { border-color: #4a5568; color: #718096; }
.elec-btn.active { border-color: #e2e8f0; color: #1a1a2e; background: #e2e8f0; }

/* Search */
#search-wrap { display: flex; flex-direction: column; gap: 3px; flex: 1; min-width: 160px; max-width: 240px; }
#search-input {
  background: rgba(45,55,72,0.8); border: 1px solid #4a5568; border-radius: 6px;
  color: #eee; padding: 5px 10px; font-size: 0.78rem; outline: none;
  transition: border-color .2s;
}
#search-input:focus { border-color: #63b3ed; }
#search-input::placeholder { color: #718096; }

/* Count + favorites badges */
#badges { display: flex; gap: 8px; align-items: center; margin-left: auto; }
#count-badge { background: #e94560; color: #fff; border-radius: 20px; padding: 4px 11px; font-size: 0.75rem; font-weight: 700; white-space: nowrap; }
#fav-btn {
  background: rgba(246,173,85,0.15); color: #f6ad55; border: 1.5px solid #f6ad55;
  border-radius: 20px; padding: 4px 11px; font-size: 0.75rem; font-weight: 700;
  cursor: pointer; white-space: nowrap; transition: all .2s;
}
#fav-btn:hover { background: rgba(246,173,85,0.3); }
#fav-btn.has-favs { background: rgba(246,173,85,0.25); }

/* ── Map ──────────────────────────────────────────────────────────────────── */
#map { flex: 1; min-height: 0; position: relative; overflow: hidden; }

/* ── Popups ───────────────────────────────────────────────────────────────── */
.leaflet-popup-content-wrapper {
  background: #16213e; color: #eee; border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0,0,0,.6); border: 1px solid #0f3460; max-width: 290px;
}
.leaflet-popup-tip { background: #16213e; }
.popup-name { font-size: .95rem; font-weight: 700; color: #e94560; margin-bottom: 2px; }
.popup-city { font-size: .73rem; color: #a0aec0; margin-bottom: 6px; }
.popup-type { display: inline-block; padding: 2px 7px; border-radius: 12px; font-size: .65rem; font-weight: 600; margin-bottom: 6px; }
.popup-price { font-size: .9rem; font-weight: 700; color: #68d391; margin-bottom: 5px; }
.popup-amenities { font-size: .71rem; color: #cbd5e0; line-height: 1.4; margin-bottom: 6px; }
.popup-meta { display: flex; gap: 12px; font-size: .68rem; color: #a0aec0; margin-bottom: 8px; }
.popup-meta span b { color: #eee; }
.popup-actions { display: flex; gap: 7px; flex-wrap: wrap; }
.popup-btn {
  padding: 4px 10px; border-radius: 6px; font-size: .68rem; font-weight: 600;
  cursor: pointer; border: 1px solid; transition: all .18s; text-decoration: none;
  display: inline-block;
}
.btn-website { background: rgba(99,179,237,.15); color: #63b3ed; border-color: #63b3ed; }
.btn-website:hover { background: rgba(99,179,237,.3); }
.btn-fav { background: rgba(246,173,85,.12); color: #f6ad55; border-color: #f6ad55; }
.btn-fav:hover { background: rgba(246,173,85,.28); }
.btn-fav.starred { background: rgba(246,173,85,.35); }

/* ── Side panel ───────────────────────────────────────────────────────────── */
#panel-toggle {
  position: absolute; right: 0; top: 50%; transform: translateY(-50%);
  z-index: 1001; background: rgba(15,52,96,0.97); border: 1px solid #4a5568;
  border-right: none; border-radius: 6px 0 0 6px;
  color: #eee; padding: 14px 7px; cursor: pointer; font-size: 1.1rem;
  transition: right .3s ease; line-height: 1;
}
#panel-toggle:hover { background: #0f3460; }
#side-panel {
  position: absolute; right: 0; top: 0; bottom: 0; z-index: 1000;
  width: 234px; background: rgba(13,40,80,0.97); backdrop-filter: blur(8px);
  border-left: 1px solid #2d3748; display: flex; flex-direction: column;
  overflow-y: auto; transform: translateX(100%); transition: transform .3s ease;
}
#side-panel.open { transform: translateX(0); }
.sp-head {
  display: flex; align-items: center; padding: 11px 14px 9px;
  background: #0f3460; border-bottom: 1px solid #2d3748; flex-shrink: 0;
}
.sp-heading { font-size: .82rem; font-weight: 700; color: #e2e8f0; flex: 1; letter-spacing: .3px; }
.sp-close { background: none; border: none; color: #718096; font-size: 1.2rem; cursor: pointer; padding: 0 2px; }
.sp-close:hover { color: #e94560; }
.sp-section { padding: 13px 14px 10px; }
.sp-label { font-size: .62rem; font-weight: 700; color: #718096; text-transform: uppercase; letter-spacing: .8px; margin-bottom: 9px; }
.sp-overlay-btns { display: flex; flex-direction: column; gap: 5px; }
.sp-overlay-btns .chip { text-align: left; padding: 6px 11px; width: 100%; }
.sp-divider { border-top: 1px solid rgba(255,255,255,.07); margin: 2px 10px; }
#price-display { font-size: .82rem; font-weight: 700; color: #63b3ed; margin-bottom: 10px; }
#slider { margin: 2px 3px 6px; }

/* ── Overlay legend (inside side panel) ──────────────────────────────────── */
#overlay-legend { padding: 0 14px 14px; display: none; }
#overlay-legend.visible { display: block; }
#overlay-legend .leg-title { font-size: .62rem; font-weight: 700; color: #718096; text-transform: uppercase; letter-spacing: .7px; margin-bottom: 8px; }
.leg-bar { width: 100%; height: 10px; border-radius: 5px; margin-bottom: 4px; }
.leg-bar.election { background: linear-gradient(to right,#003399,#6688ff,#ccccff,#ffcccc,#ff4444,#990000); }
.leg-labels { display: flex; justify-content: space-between; font-size: .62rem; color: #718096; margin-bottom: 2px; }
.leg-labels span.d { color: #6688ff; font-weight: 700; }
.leg-labels span.r { color: #ff4444; font-weight: 700; }
.crime-swatches, .tax-swatches { display: flex; flex-direction: column; gap: 2px; }
.swatch-row { display: flex; align-items: center; gap: 6px; font-size: .63rem; color: #cbd5e0; }
.swatch { width: 12px; height: 12px; border-radius: 2px; flex-shrink: 0; }

/* ── Compare panel ────────────────────────────────────────────────────────── */
#compare-panel {
  position: fixed; bottom: 0; left: 0; right: 0; z-index: 2000;
  background: #16213e; border-top: 2px solid #e94560;
  transform: translateY(100%); transition: transform .3s ease;
  max-height: 55vh; display: flex; flex-direction: column;
}
#compare-panel.open { transform: translateY(0); }
#compare-header {
  display: flex; align-items: center; padding: 10px 16px; gap: 12px;
  background: #0f3460; flex-shrink: 0;
}
#compare-header h3 { font-size: .9rem; font-weight: 700; color: #fff; flex: 1; }
#clear-favs { padding: 3px 10px; border: 1px solid #718096; border-radius: 12px; font-size: .68rem; color: #718096; background: transparent; cursor: pointer; }
#close-compare { background: none; border: none; color: #a0aec0; font-size: 1.2rem; cursor: pointer; padding: 0 4px; }
#compare-scroll { overflow-y: auto; flex: 1; }
#compare-table { width: 100%; border-collapse: collapse; font-size: .72rem; }
#compare-table th { position: sticky; top: 0; background: #0f3460; color: #a0aec0; font-weight: 600; text-transform: uppercase; font-size: .6rem; letter-spacing: .5px; padding: 7px 10px; text-align: left; border-bottom: 1px solid #2d3748; }
#compare-table td { padding: 8px 10px; border-bottom: 1px solid rgba(255,255,255,.05); vertical-align: top; color: #eee; }
#compare-table tr:hover td { background: rgba(255,255,255,.04); }
.td-name { font-weight: 700; color: #e94560; max-width: 150px; }
.td-remove { cursor: pointer; color: #718096; font-size: 1rem; text-align: center; }
.td-remove:hover { color: #e94560; }
.crime-badge, .tax-badge { display: inline-block; padding: 1px 6px; border-radius: 10px; font-size: .63rem; font-weight: 600; }

/* ── Loading spinner ──────────────────────────────────────────────────────── */
#loading-overlay {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%);
  background: rgba(22,33,62,.92); border-radius: 10px; padding: 14px 22px;
  color: #63b3ed; font-size: .82rem; font-weight: 600; z-index: 2000;
  display: none; align-items: center; gap: 9px;
}
#loading-overlay.visible { display: flex; }
.spinner { width: 18px; height: 18px; border: 3px solid #2d3748; border-top-color: #63b3ed; border-radius: 50%; animation: spin .8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* County tooltip */
.county-tip {
  background: rgba(22,33,62,.95) !important; border: 1px solid #2d3748 !important;
  color: #eee !important; border-radius: 6px !important; font-size: .75rem !important;
  padding: 6px 10px !important; box-shadow: 0 2px 8px rgba(0,0,0,.5) !important;
  line-height: 1.5 !important;
}
.county-tip::before { display: none !important; }
</style>
</head>
<body>

<div id="header">
  <!-- Row 1: title, type, badges -->
  <div id="header-row1">
    <h1>Florida <span>Gated Communities</span></h1>

    <div class="ctrl-group">
      <span class="ctrl-label">Community Type</span>
      <div id="type-filter" class="chip-row"></div>
    </div>

    <div id="badges">
      <div id="count-badge">228 communities</div>
      <button id="fav-btn" onclick="toggleCompare()">Saved (0)</button>
    </div>
  </div>

  <!-- Row 2: search, amenity filters -->
  <div id="header-row2">
    <div id="search-wrap">
      <span class="ctrl-label">Search</span>
      <input id="search-input" type="text" placeholder="Community name or city&hellip;" oninput="applyFilters()"/>
    </div>

    <div class="ctrl-group">
      <span class="ctrl-label">Must-Have Amenities</span>
      <div id="amenity-filter" class="chip-row"></div>
    </div>
  </div>
</div>

<div id="map">
  <div id="loading-overlay"><div class="spinner"></div>Loading county data&hellip;</div>

  <!-- Panel toggle tab (always visible on map edge) -->
  <button id="panel-toggle" onclick="togglePanel()" title="Toggle filters panel">&#9776;</button>

  <!-- Side panel: price range + overlay + legend -->
  <div id="side-panel" class="open">
    <div class="sp-head">
      <span class="sp-heading">Filters &amp; Layers</span>
      <button class="sp-close" onclick="togglePanel()" title="Close panel">&times;</button>
    </div>

    <div class="sp-section">
      <div class="sp-label">Price Range</div>
      <div id="price-display">$140K &ndash; $10M+</div>
      <div id="slider"></div>
    </div>

    <div class="sp-divider"></div>

    <div class="sp-section">
      <div class="sp-label">Map Overlay</div>
      <div id="overlay-btns" class="sp-overlay-btns">
        <button class="chip elec-btn active" data-overlay="off">Off</button>
        <button class="chip elec-btn" data-overlay="2020">2020 Vote</button>
        <button class="chip elec-btn" data-overlay="2024">2024 Vote</button>
        <button class="chip elec-btn" data-overlay="crime">Crime</button>
        <button class="chip elec-btn" data-overlay="tax">Prop Tax</button>
      </div>
    </div>

    <div class="sp-divider"></div>

    <!-- Legend (shown when an overlay is active) -->
    <div id="overlay-legend">
      <div class="leg-title" id="leg-title">Legend</div>
      <div id="leg-election">
        <div class="leg-bar election"></div>
        <div class="leg-labels"><span class="d">Dem</span><span class="r">Rep</span></div>
      </div>
      <div id="leg-crime" style="display:none">
        <div class="crime-swatches">
          <div class="swatch-row"><div class="swatch" style="background:#2d8e3e"></div>Very Low &lt;75</div>
          <div class="swatch-row"><div class="swatch" style="background:#68d391"></div>Low 75&ndash;125</div>
          <div class="swatch-row"><div class="swatch" style="background:#f6e05e"></div>Moderate 125&ndash;175 <em style="color:#718096">(avg 146)</em></div>
          <div class="swatch-row"><div class="swatch" style="background:#f6ad55"></div>Elevated 175&ndash;225</div>
          <div class="swatch-row"><div class="swatch" style="background:#e53e3e"></div>High &gt;225</div>
        </div>
      </div>
      <div id="leg-tax" style="display:none">
        <div class="tax-swatches">
          <div class="swatch-row"><div class="swatch" style="background:#2d8e3e"></div>Low &lt;0.60%</div>
          <div class="swatch-row"><div class="swatch" style="background:#68d391"></div>Below avg 0.60&ndash;0.72%</div>
          <div class="swatch-row"><div class="swatch" style="background:#f6e05e"></div>Average 0.72&ndash;0.82% <em style="color:#718096">(FL ~0.74%)</em></div>
          <div class="swatch-row"><div class="swatch" style="background:#f6ad55"></div>Above avg 0.82&ndash;0.92%</div>
          <div class="swatch-row"><div class="swatch" style="background:#e53e3e"></div>High &gt;0.92%</div>
        </div>
      </div>
    </div><!-- end overlay-legend -->

  </div><!-- end side-panel -->
</div><!-- end map -->

<!-- Compare / favorites panel -->
<div id="compare-panel">
  <div id="compare-header">
    <h3 id="compare-title">Saved Communities</h3>
    <button id="clear-favs" onclick="clearFavs()">Clear all</button>
    <button id="close-compare" onclick="toggleCompare()">&times;</button>
  </div>
  <div id="compare-scroll">
    <table id="compare-table">
      <thead>
        <tr>
          <th>Community</th><th>City</th><th>Type</th><th>Price Range</th>
          <th>Crime (county)</th><th>Prop Tax</th><th>Amenities</th><th></th>
        </tr>
      </thead>
      <tbody id="compare-body"></tbody>
    </table>
  </div>
</div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
<script src="https://cdn.jsdelivr.net/npm/nouislider@15.7.1/dist/nouislider.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/topojson-client@3/dist/topojson-client.min.js"></script>
<script>
const communities  = COMMUNITIES_DATA_PLACEHOLDER;
const electionData = ELECTION_DATA_PLACEHOLDER;
const crimeData    = CRIME_DATA_PLACEHOLDER;
const taxFips      = TAX_FIPS_PLACEHOLDER;
const countyTax    = COUNTY_TAX_PLACEHOLDER;

// Safe CSS attribute value escape (avoids CSS.escape browser compat issues)
function safeAttr(str) { return str.replace(/"/g, '\\\\"'); }

// ── Map setup ──────────────────────────────────────────────────────────────
const map = L.map('map', { center: [27.5, -81.8], zoom: 7 });
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
  attribution: '&copy; OpenStreetMap &copy; CARTO', maxZoom: 19
}).addTo(map);
// Force Leaflet to recalculate dimensions after the flex layout settles
setTimeout(function() { map.invalidateSize(); }, 200);

// ── Side panel ─────────────────────────────────────────────────────────────
var PANEL_W = 234;
var panelEl  = document.getElementById('side-panel');
var toggleEl = document.getElementById('panel-toggle');
// Panel starts open — position toggle to the left of it
toggleEl.style.right = PANEL_W + 'px';
function togglePanel() {
  var isOpen = panelEl.classList.toggle('open');
  toggleEl.style.right = isOpen ? PANEL_W + 'px' : '0';
  // Let Leaflet re-measure after animation
  setTimeout(function() { map.invalidateSize(); }, 320);
}
map.createPane('countyPane');
map.getPane('countyPane').style.zIndex = 350;

// ── Type colors ────────────────────────────────────────────────────────────
const typeColors = {
  'Golf':         { bg: '#68d391', border: '#38a169' },
  'Luxury':       { bg: '#f6ad55', border: '#dd6b20' },
  'Ultra-Luxury': { bg: '#fc8181', border: '#c53030' },
  'Waterfront':   { bg: '#63b3ed', border: '#2b6cb0' },
  'Country Club': { bg: '#b794f4', border: '#6b46c1' },
  'Condo':        { bg: '#76e4f7', border: '#0987a0' },
  'Other':        { bg: '#e94560', border: '#9b2335' },
};
function getTypeCat(t) {
  if (!t) return 'Other';
  const tl = t.toLowerCase();
  if (tl.includes('ultra')) return 'Ultra-Luxury';
  if (tl.includes('golf')) return 'Golf';
  if (tl.includes('luxury')) return 'Luxury';
  if (tl.includes('waterfront')||tl.includes('beach')||tl.includes('marina')||tl.includes('island')) return 'Waterfront';
  if (tl.includes('country club')||(tl.includes('cc')&&tl.length<6)) return 'Country Club';
  if (tl.includes('condo')) return 'Condo';
  return 'Other';
}
function makeIcon(cat) {
  const c = typeColors[cat]||typeColors['Other'];
  return L.divIcon({
    html: '<svg xmlns="http://www.w3.org/2000/svg" width="26" height="34" viewBox="0 0 26 34">'
      +'<path d="M13 0C5.82 0 0 5.82 0 13c0 8.667 13 21 13 21S26 21.667 26 13C26 5.82 20.18 0 13 0z" fill="'+c.border+'"/>'
      +'<path d="M13 2C6.925 2 2 6.925 2 13c0 7.8 11 19 11 19S24 20.8 24 13C24 6.925 19.075 2 13 2z" fill="'+c.bg+'"/>'
      +'<circle cx="13" cy="13" r="5" fill="white" opacity="0.9"/></svg>',
    className:'', iconSize:[26,34], iconAnchor:[13,34], popupAnchor:[0,-34]
  });
}

// ── Cluster group ──────────────────────────────────────────────────────────
const clusterGroup = L.markerClusterGroup({
  maxClusterRadius: 50,
  iconCreateFunction: function(cl) {
    return L.divIcon({
      html:'<div style="background:#e94560;color:#fff;border-radius:50%;width:34px;height:34px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:12px;border:2px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,.4)">'+cl.getChildCount()+'</div>',
      className:'', iconSize:[34,34]
    });
  }
});
map.addLayer(clusterGroup);

// ── Helpers ────────────────────────────────────────────────────────────────
function fmtPrice(k) {
  if (k>=1000){var m=k/1000;return '$'+(m%1===0?m.toFixed(0):m.toFixed(1))+'M';}
  return '$'+k+'K';
}
function crimeTier(rate) {
  if (rate<75)  return {label:'Very Low',  color:'#68d391'};
  if (rate<125) return {label:'Low',        color:'#9ae6b4'};
  if (rate<175) return {label:'Moderate',   color:'#f6e05e'};
  if (rate<225) return {label:'Elevated',   color:'#f6ad55'};
               return {label:'High',        color:'#fc8181'};
}
function taxColor(rate) {
  if (rate < 0.60) return '#2d8e3e';
  if (rate < 0.72) return '#68d391';
  if (rate < 0.82) return '#f6e05e';
  if (rate < 0.92) return '#f6ad55';
               return '#e53e3e';
}

// ── Favorites (localStorage) ───────────────────────────────────────────────
function loadFavs() { try { return JSON.parse(localStorage.getItem('fl_favs')||'[]'); } catch(e){ return []; } }
function saveFavs(arr) { try { localStorage.setItem('fl_favs', JSON.stringify(arr)); } catch(e) {} }
function isFav(name) { return loadFavs().includes(name); }
function toggleFav(name) {
  var favs = loadFavs();
  var idx = favs.indexOf(name);
  if (idx>=0) favs.splice(idx,1); else favs.push(name);
  saveFavs(favs);
  updateFavBtn();
  renderCompareTable();
  // Update all open popups for this community
  document.querySelectorAll('.btn-fav[data-name="'+safeAttr(name)+'"]').forEach(function(el){
    el.textContent = isFav(name) ? 'Saved' : 'Save';
    el.classList.toggle('starred', isFav(name));
  });
}
function updateFavBtn() {
  var n = loadFavs().length;
  var btn = document.getElementById('fav-btn');
  btn.textContent = 'Saved ('+n+')';
  btn.classList.toggle('has-favs', n>0);
}
function clearFavs() { saveFavs([]); updateFavBtn(); renderCompareTable(); }
updateFavBtn();

// ── Popup builder ──────────────────────────────────────────────────────────
function buildPopup(c) {
  var cat = getTypeCat(c.type);
  var tc  = typeColors[cat]||typeColors['Other'];
  var searchUrl = 'https://www.google.com/search?q='+encodeURIComponent(c.name+' '+c.city+' Florida gated community');
  var faved = isFav(c.name);

  // County stats
  var crimeHtml = '', taxHtml = '';
  var cname = c.county;
  // Crime lookup by county name
  var crimeRate = null;
  for (var fips in crimeData) { if (crimeData[fips].name === cname) { crimeRate = crimeData[fips].violent; break; } }
  if (crimeRate !== null) {
    var tier = crimeTier(crimeRate);
    crimeHtml = '<span style="color:'+tier.color+'">'+tier.label+' ('+crimeRate.toFixed(0)+'/100k)</span>';
  }
  var taxRate = countyTax[cname];
  if (taxRate !== undefined) {
    taxHtml = '<span style="color:'+taxColor(taxRate)+'">'+taxRate.toFixed(2)+'%/yr</span>';
  }

  var metaHtml = '';
  if (crimeHtml||taxHtml) {
    metaHtml = '<div class="popup-meta">'
      + (crimeHtml ? '<span>Crime: '+crimeHtml+'</span>' : '')
      + (taxHtml   ? '<span>Tax: '+taxHtml+'</span>' : '')
      + '</div>';
  }

  return '<div class="popup-name">'+c.name+'</div>'
    +'<div class="popup-city">'+c.city+(cname?' &bull; '+cname+' Co.':'')+'</div>'
    +'<span class="popup-type" style="background:'+tc.bg+'22;color:'+tc.bg+';border:1px solid '+tc.bg+'">'+c.type+'</span><br/>'
    +'<div class="popup-price">'+c.price+'</div>'
    +'<div class="popup-amenities">'+c.amenities+'</div>'
    +'<div style="font-size:.68rem;color:#a0aec0;margin-bottom:6px">Security: <span style="color:#63b3ed;font-weight:600">'+c.security+'</span></div>'
    +metaHtml
    +'<div class="popup-actions">'
    +'<a href="'+searchUrl+'" target="_blank" class="popup-btn btn-website">Search Website</a>'
    +'<button class="popup-btn btn-fav'+(faved?' starred':'')+'" data-name="'+c.name.replace(/"/g,'&quot;')+'" onclick="toggleFav(this.dataset.name)">'+(faved?'Saved':'Save')+'</button>'
    +'</div>';
}

// ── Markers ────────────────────────────────────────────────────────────────
const markers = communities.map(function(c) {
  var cat = getTypeCat(c.type);
  var m = L.marker([c.lat,c.lng],{icon:makeIcon(cat)});
  m.bindPopup(function(){ return buildPopup(c); },{maxWidth:290});
  m._community = c;
  m._cat = cat;
  return m;
});

// ── Price slider ───────────────────────────────────────────────────────────
const SLIDER_MIN=140, SLIDER_MAX=10000;
var slider=document.getElementById('slider');
noUiSlider.create(slider,{start:[SLIDER_MIN,SLIDER_MAX],connect:true,range:{min:SLIDER_MIN,max:SLIDER_MAX},step:50,tooltips:false});
var priceDisplay=document.getElementById('price-display');
function updatePriceDisplay(vals){
  var lo=parseFloat(vals[0]),hi=parseFloat(vals[1]);
  priceDisplay.textContent=fmtPrice(lo)+' \u2013 '+(hi>=SLIDER_MAX?fmtPrice(hi)+'+':fmtPrice(hi));
}

// ── Type filter ────────────────────────────────────────────────────────────
var allTypes=['Golf','Luxury','Ultra-Luxury','Waterfront','Country Club','Condo','Other'];
var activeTypes={};
allTypes.forEach(function(t){activeTypes[t]=true;});
var typeFilterEl=document.getElementById('type-filter');
allTypes.forEach(function(t){
  var c=typeColors[t]||typeColors['Other'];
  var btn=document.createElement('button');
  btn.className='chip type-btn';
  btn.textContent=t;
  btn.style.borderColor=c.bg; btn.style.color=c.bg; btn.style.background=c.bg+'22';
  btn.addEventListener('click',function(){
    activeTypes[t]=!activeTypes[t];
    btn.style.background=activeTypes[t]?c.bg+'22':'transparent';
    btn.style.color=activeTypes[t]?c.bg:c.bg+'55';
    btn.style.borderColor=activeTypes[t]?c.bg:c.bg+'33';
    applyFilters();
  });
  typeFilterEl.appendChild(btn);
});

// ── Amenity filter ─────────────────────────────────────────────────────────
var amenityKeywords = [
  {label:'Pool',    kw:'pool'},
  {label:'Golf',    kw:'golf'},
  {label:'Tennis',  kw:'tennis'},
  {label:'Fitness', kw:'fitness'},
  {label:'Water',   kw:['waterfront','marina','lake','bay','gulf','beach']},
  {label:'Pickleball', kw:'pickleball'},
  {label:'Clubhouse',  kw:'clubhouse'},
];
var activeAmenities={};
amenityKeywords.forEach(function(a){activeAmenities[a.label]=false;});
var amenityEl=document.getElementById('amenity-filter');
amenityKeywords.forEach(function(a){
  var btn=document.createElement('button');
  btn.className='chip';
  btn.textContent=a.label;
  btn.style.borderColor='#4a5568'; btn.style.color='#718096';
  btn.addEventListener('click',function(){
    activeAmenities[a.label]=!activeAmenities[a.label];
    btn.style.background=activeAmenities[a.label]?'rgba(99,179,237,.25)':'transparent';
    btn.style.color=activeAmenities[a.label]?'#63b3ed':'#718096';
    btn.style.borderColor=activeAmenities[a.label]?'#63b3ed':'#4a5568';
    applyFilters();
  });
  amenityEl.appendChild(btn);
});
function hasAmenity(c, kw) {
  var text=(c.amenities+' '+c.type).toLowerCase();
  if (Array.isArray(kw)) return kw.some(function(k){return text.includes(k);});
  return text.includes(kw);
}

// ── Filter logic ───────────────────────────────────────────────────────────
var currentMin=SLIDER_MIN, currentMax=SLIDER_MAX;
var countBadge=document.getElementById('count-badge');

function applyFilters(){
  var searchVal=(document.getElementById('search-input').value||'').toLowerCase().trim();
  var anyAmenity=amenityKeywords.some(function(a){return activeAmenities[a.label];});
  clusterGroup.clearLayers();
  var toAdd=[];
  markers.forEach(function(m){
    var c=m._community;
    // Type
    if (!activeTypes[m._cat]) return;
    // Price
    var cMin=c.minPrice!==null?c.minPrice:0;
    var cMax=c.maxPrice!==null?c.maxPrice:99999;
    var atMax=currentMax>=SLIDER_MAX;
    if (!atMax&&cMin>currentMax) return;
    if (cMax<currentMin) return;
    // Search
    if (searchVal&&!(c.name.toLowerCase().includes(searchVal)||c.city.toLowerCase().includes(searchVal))) return;
    // Amenities
    if (anyAmenity) {
      var ok=amenityKeywords.every(function(a){
        if (!activeAmenities[a.label]) return true;
        return hasAmenity(c,a.kw);
      });
      if (!ok) return;
    }
    toAdd.push(m);
  });
  clusterGroup.addLayers(toAdd);
  countBadge.textContent=toAdd.length+' communities';
}

slider.noUiSlider.on('update',function(vals){
  currentMin=parseFloat(vals[0]); currentMax=parseFloat(vals[1]);
  updatePriceDisplay(vals); applyFilters();
});
applyFilters();

// ── Compare panel ──────────────────────────────────────────────────────────
var compareOpen=false;
function toggleCompare(){
  compareOpen=!compareOpen;
  document.getElementById('compare-panel').classList.toggle('open',compareOpen);
  if (compareOpen) renderCompareTable();
}
function renderCompareTable(){
  var favs=loadFavs();
  var tbody=document.getElementById('compare-body');
  tbody.innerHTML='';
  var title=document.getElementById('compare-title');
  title.textContent='Saved Communities ('+favs.length+')';
  if (favs.length===0){
    tbody.innerHTML='<tr><td colspan="8" style="text-align:center;color:#718096;padding:20px">No saved communities yet. Click &ldquo;Save&rdquo; on any community popup.</td></tr>';
    return;
  }
  favs.forEach(function(name){
    var c=communities.find(function(x){return x.name===name;});
    if (!c) return;
    var crimeRate=null;
    for (var fips in crimeData){if(crimeData[fips].name===c.county){crimeRate=crimeData[fips].violent;break;}}
    var crimeTierStr='', crimeBadge='';
    if (crimeRate!==null){
      var t=crimeTier(crimeRate);
      crimeBadge='<span class="crime-badge" style="background:'+t.color+'22;color:'+t.color+';border:1px solid '+t.color+'">'+t.label+'<br/>'+crimeRate.toFixed(0)+'/100k</span>';
    }
    var taxRate=countyTax[c.county];
    var taxBadge=taxRate!==undefined?'<span class="tax-badge" style="background:'+taxColor(taxRate)+'22;color:'+taxColor(taxRate)+';border:1px solid '+taxColor(taxRate)+'">'+taxRate.toFixed(2)+'%</span>':'—';
    var tr=document.createElement('tr');
    tr.innerHTML='<td class="td-name">'+c.name+'</td>'
      +'<td>'+c.city+'</td>'
      +'<td>'+c.type+'</td>'
      +'<td style="white-space:nowrap">'+c.price+'</td>'
      +'<td>'+crimeBadge+'</td>'
      +'<td>'+taxBadge+'</td>'
      +'<td style="max-width:200px;font-size:.67rem;color:#a0aec0">'+c.amenities+'</td>'
      +'<td class="td-remove" data-name="'+c.name.replace(/"/g,'&quot;')+'" onclick="toggleFav(this.dataset.name)" title="Remove">&times;</td>';
    tbody.appendChild(tr);
  });
}

// ── County overlay ─────────────────────────────────────────────────────────
var countyLayer=null, topoCache=null, currentOverlay='off';
var overlayLegend=document.getElementById('overlay-legend');
var legTitle=document.getElementById('leg-title');
var legElection=document.getElementById('leg-election');
var legCrime=document.getElementById('leg-crime');
var legTax=document.getElementById('leg-tax');
var loadingOverlay=document.getElementById('loading-overlay');

function electionColor(r,d){
  var m=r-d;
  if (m>45) return 'rgba(130,0,0,.72)';
  if (m>30) return 'rgba(200,30,30,.68)';
  if (m>15) return 'rgba(240,80,80,.62)';
  if (m>5)  return 'rgba(255,160,160,.55)';
  if (m>-5) return 'rgba(210,210,255,.55)';
  if (m>-15) return 'rgba(130,160,255,.62)';
  if (m>-30) return 'rgba(50,80,220,.68)';
             return 'rgba(0,0,160,.72)';
}
function crimeColor(rate){
  if (rate<75)  return 'rgba(45,142,62,.70)';
  if (rate<125) return 'rgba(104,211,145,.65)';
  if (rate<175) return 'rgba(246,224,94,.65)';
  if (rate<225) return 'rgba(246,173,85,.68)';
               return 'rgba(229,62,62,.72)';
}
function taxColorAlpha(rate){
  if (rate<0.60) return 'rgba(45,142,62,.70)';
  if (rate<0.72) return 'rgba(104,211,145,.65)';
  if (rate<0.82) return 'rgba(246,224,94,.65)';
  if (rate<0.92) return 'rgba(246,173,85,.68)';
               return 'rgba(229,62,62,.72)';
}
function getFillColor(fips, overlay){
  var key=String(fips).padStart(5,'0');
  if (overlay==='crime'){
    var cd=crimeData[key]; return cd?crimeColor(cd.violent):'rgba(100,100,100,.25)';
  }
  if (overlay==='tax'){
    var td=taxFips[key]; return td?taxColorAlpha(td.rate):'rgba(100,100,100,.25)';
  }
  var ed=electionData[key]; if (!ed) return 'rgba(100,100,100,.25)';
  return overlay==='2024'?electionColor(ed.r24,ed.d24):electionColor(ed.r20,ed.d20);
}
function buildCountyTip(fips, overlay){
  var key=String(fips).padStart(5,'0');
  if (overlay==='crime'){
    var cd=crimeData[key]; if (!cd) return null;
    var t=crimeTier(cd.violent);
    return '<b>'+cd.name+' County</b><br/>Violent: <b>'+cd.violent.toFixed(1)+'</b>/100k &mdash; <span style="color:'+t.color+'">'+t.label+'</span><br/><em style="color:#718096">FL avg: 145.7</em>';
  }
  if (overlay==='tax'){
    var td=taxFips[key]; if (!td) return null;
    return '<b>'+td.name+' County</b><br/>Eff. tax rate: <b>'+td.rate.toFixed(2)+'%</b><br/><span style="color:'+taxColor(td.rate)+'">'+( td.rate<0.72?'Below avg':td.rate<0.82?'Average':'Above avg')+'</span><br/><em style="color:#718096">FL avg: ~0.74%</em>';
  }
  var ed=electionData[key]; if (!ed) return null;
  var r=overlay==='2024'?ed.r24:ed.r20;
  var d=overlay==='2024'?ed.d24:ed.d20;
  var dem=overlay==='2024'?'Harris':'Biden';
  var winner=r>d?'Trump':dem;
  var wc=r>d?'#ff8080':'#8080ff';
  return '<b>'+ed.name+' County</b>'
    +'<br/><span style="color:'+wc+';font-weight:700">'+winner+' +'+ Math.abs(r-d).toFixed(1)+'%</span>'
    +'<br/><span style="color:#ff9999">R '+r.toFixed(1)+'%</span>'
    +' &nbsp;<span style="color:#99aaff">D '+d.toFixed(1)+'%</span>';
}

function buildCountyLayer(overlay){
  if (countyLayer){map.removeLayer(countyLayer);countyLayer=null;}
  if (overlay==='off'){overlayLegend.classList.remove('visible');return;}
  legElection.style.display='none'; legCrime.style.display='none'; legTax.style.display='none';
  if (overlay==='crime'){legTitle.textContent='Violent Crime (per 100k)'; legCrime.style.display='block';}
  else if (overlay==='tax'){legTitle.textContent='Property Tax Rate'; legTax.style.display='block';}
  else {legTitle.textContent=overlay+' Presidential Vote'; legElection.style.display='block';}

  var features=topojson.feature(topoCache,topoCache.objects.counties).features
    .filter(function(f){return String(f.id).padStart(5,'0').startsWith('12');});

  countyLayer=L.geoJSON(features,{
    pane:'countyPane',
    style:function(f){return{fillColor:getFillColor(f.id,overlay),fillOpacity:1,color:'rgba(255,255,255,.18)',weight:1};},
    onEachFeature:function(f,layer){
      layer.on('mouseover',function(e){
        layer.setStyle({color:'rgba(255,255,255,.7)',weight:2});
        var tip=buildCountyTip(f.id,overlay);
        if (tip) layer.bindTooltip(tip,{sticky:true,className:'county-tip',opacity:.95}).openTooltip(e.latlng);
      });
      layer.on('mouseout',function(){countyLayer.resetStyle(layer);layer.closeTooltip();});
    }
  }).addTo(map);
  overlayLegend.classList.add('visible');
}

function loadTopoAndRender(overlay){
  if (topoCache){buildCountyLayer(overlay);return;}
  loadingOverlay.classList.add('visible');
  fetch('https://cdn.jsdelivr.net/npm/us-atlas@3/counties-10m.json')
    .then(function(r){return r.json();})
    .then(function(topo){topoCache=topo;loadingOverlay.classList.remove('visible');buildCountyLayer(overlay);})
    .catch(function(){loadingOverlay.classList.remove('visible');alert('Could not load county boundaries. Check internet connection.');});
}

document.querySelectorAll('.elec-btn').forEach(function(btn){
  btn.addEventListener('click',function(){
    var ov=btn.getAttribute('data-overlay');
    if (ov===currentOverlay) return;
    currentOverlay=ov;
    document.querySelectorAll('.elec-btn').forEach(function(b){b.classList.remove('active');});
    btn.classList.add('active');
    if (ov==='off'){
      if (countyLayer){map.removeLayer(countyLayer);countyLayer=null;}
      overlayLegend.classList.remove('visible');
    } else { loadTopoAndRender(ov); }
  });
});
</script>
</body>
</html>"""

html = html.replace('COMMUNITIES_DATA_PLACEHOLDER', data_json)
html = html.replace('ELECTION_DATA_PLACEHOLDER',    election_json)
html = html.replace('CRIME_DATA_PLACEHOLDER',       crime_json)
html = html.replace('TAX_FIPS_PLACEHOLDER',         tax_json)
html = html.replace('COUNTY_TAX_PLACEHOLDER',       ctax_json)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f'Done! {len(communities)} communities, {len(election_data)} election, {len(crime_data)} crime, {len(tax_data)} tax counties.')
