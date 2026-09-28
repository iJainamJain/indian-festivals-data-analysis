"""Canonical festival catalog used to resolve RBI holiday descriptions into festivals.

Each entry: canonical name -> (regex matched against the RBI description, primary tradition,
festival type, Wikipedia article title used for attribution/verification of tradition).

primary_tradition is assigned from the Wikipedia infobox "Observed by"/"Type" fields that
02_build_dataset.py scrapes and stores next to it (wiki_observed_by, wiki_type), so every
classification can be audited against its cited source.
"""

# Traditions used in the analysis (the eight groups named in the project brief)
TRADITIONS = ["Hindu", "Muslim", "Christian", "Sikh", "Buddhist", "Jain", "Parsi", "Tribal/Indigenous",
              "Cultural (multi-faith)"]

# name: (regex, tradition, type, wikipedia_title)
CATALOG = {
    # ---------------- Hindu ----------------
    "Diwali (Deepavali)": (r"Diwali|Deepawali|Deepavali|Naraka Chaturdashi|Kali Puja|Govardhan|Bali Pratipada|Balipadyami|Laxmi Puja \(Deepawali\)",
                           "Hindu", "Religious", "Diwali"),
    "Bhai Dooj": (r"Bhai ?Bij|Bhaidooj|Bhratridwitiya|Chitragupt", "Hindu", "Religious", "Bhai Dooj"),
    "Vikram Samvat New Year": (r"Vikram Samvant", "Hindu", "New Year", "Vikram Samvat"),
    "Kojagari Lakshmi Puja": (r"^(?!.*(Diwali|Deepawali)).*(Lakshmi Puja|Laxmi Puja)", "Hindu", "Religious", "Sharad Purnima"),
    "Holi": (r"Holi\b|Holi \(|Dhulandi|Dhuleti|Dol Jatra|Holika Dahan", "Hindu", "Religious/Seasonal", "Holi"),
    "Navratri / Durga Puja / Dussehra": (r"Dussehra|Dusshera|Dasara|Vijaya ?Dash|Vijayadas|Durga Puja|Durga Ashtami|Maha Ashtami|Maha Saptami|Maha ?[Nn]avami|Mahanavami|Ayu[dt]ha ?[Pp]ooja|Ayudhapooja|Navaratri Ends|Navratra Sthapna",
                                         "Hindu", "Religious", "Durga Puja"),
    "Mahalaya": (r"Mahalaya", "Hindu", "Religious", "Mahalaya"),
    "Ganesh Chaturthi": (r"Ganesh|Vinayak|Varasiddhi", "Hindu", "Religious", "Ganesh Chaturthi"),
    "Hartalika Teej": (r"Hartalika", "Hindu", "Religious", "Teej"),
    "Janmashtami": (r"Janmashtami|Krishna Jayanthi", "Hindu", "Religious", "Krishna Janmashtami"),
    "Raksha Bandhan": (r"Raksha Bandhan|Jhulana Purnima", "Hindu", "Religious", "Raksha Bandhan"),
    "Maha Shivaratri": (r"[Ss]hivratri|Sivarathri", "Hindu", "Religious", "Maha Shivaratri"),
    "Ram Navami": (r"Ram Navami", "Hindu", "Religious", "Rama Navami"),
    "Chaitra Navratri (1st day)": (r"1st Navratra", "Hindu", "Religious", "Chaitra Navaratri"),
    "Makar Sankranti": (r"Makar|Uttarayana|Maghe Sankranti", "Hindu", "Harvest", "Makar Sankranti"),
    "Pongal": (r"Pongal(?!a)|Uzhavar|Kanuma|Thiruvalluvar", "Hindu", "Harvest", "Pongal (festival)"),
    "Chhath Puja": (r"Chh?ath|Surya Shashti", "Hindu", "Religious", "Chhath"),
    "Saraswati Puja / Vasant Panchami": (r"Saraswati|Basanta Panchami", "Hindu", "Religious", "Vasant Panchami"),
    "Karva Chauth": (r"Karva Chauth", "Hindu", "Religious", "Karva Chauth"),
    "Rath Yatra": (r"Rath", "Hindu", "Religious", "Ratha Yatra (Puri)"),
    "Kartika Purnima / Rahas Purnima": (r"Kart?hika Purnima|Kartika Purnima|Rahas Purnima", "Hindu", "Religious", "Kartik Purnima"),
    "Kumar Purnima": (r"Kumar Purnima", "Hindu", "Religious", "Kumar Purnima"),
    "Akshaya Tritiya": (r"Akshaya Tritiya", "Hindu", "Religious", "Akshaya Tritiya"),
    "Basava Jayanti": (r"Basava Jayanti", "Hindu", "Commemoration", "Basava Jayanti"),
    "Parshuram Jayanti": (r"Parshuram", "Hindu", "Commemoration", "Parashurama Jayanti"),
    "Valmiki Jayanti": (r"Valmiki", "Hindu", "Commemoration", "Valmiki Jayanti"),
    "Vishwakarma Day": (r"Vishwakarma", "Hindu", "Religious", "Vishwakarma Puja"),
    "Thaipusam": (r"Thai Poosam", "Hindu", "Religious", "Thaipusam"),
    "Attukal Pongala": (r"Attukal", "Hindu", "Religious", "Attukal Pongala"),
    "Nuakhai": (r"Nuakhai", "Hindu", "Harvest", "Nuakhai"),
    "Raja Sankranti": (r"Raja Sankranti", "Hindu", "Seasonal", "Raja Parba"),
    "Harela": (r"Harela", "Hindu", "Seasonal", "Harela"),
    "Igas-Bagwal": (r"Ig?as-Bagwal|Egaas-Bagwaal", "Hindu", "Religious", "Igas Bagwal"),
    "Indra Jatra": (r"Indrajatra", "Hindu", "Religious", "Indra Jatra"),
    "Srimanta Sankardeva Tithi / Janmotsav": (r"Sankardeva", "Hindu", "Commemoration", "Srimanta Sankardeva"),
    "Kanakadasa Jayanti": (r"Kanakadasa", "Hindu", "Commemoration", "Kanaka Dasa"),
    "Sant Ravidas Jayanti": (r"Ravidas|Ravi Das", "Hindu", "Commemoration", "Ravidas Jayanti"),
    "Sant Kabir Jayanti": (r"Kabir", "Hindu", "Commemoration", "Kabir"),
    "Sree Narayana Guru Jayanti / Samadhi": (r"Narayana Guru", "Hindu", "Commemoration", "Narayana Guru"),
    "Maharaja Agrasen Jayanti": (r"Agrasen", "Hindu", "Commemoration", "Agrasen"),
    "Kati Bihu": (r"Kati Bihu", "Hindu", "Harvest", "Kati Bihu"),
    "Gudi Padwa / Ugadi": (r"Gudhi Padwa|Ugadi|Telugu New Year", "Hindu", "New Year", "Ugadi"),
    "Maha Vishuva Sankranti (Odia New Year)": (r"Maha Vishuva", "Hindu", "New Year", "Pana Sankranti"),
    "Tamil New Year (Puthandu)": (r"Tamil New Year", "Hindu", "New Year", "Puthandu"),
    "Vishu": (r"Vishu\b", "Hindu", "New Year", "Vishu"),
    # ---------------- Cultural / multi-faith regional ----------------
    "Onam": (r"Onam|Thiruvonam", "Cultural (multi-faith)", "Harvest", "Onam"),
    "Bohag Bihu": (r"Bohag Bihu", "Cultural (multi-faith)", "New Year", "Rongali Bihu"),
    "Magh Bihu": (r"Magh Bihu", "Cultural (multi-faith)", "Harvest", "Magh Bihu"),
    "Bengali New Year (Pohela Boishakh)": (r"Bengali New Year", "Cultural (multi-faith)", "New Year", "Pohela Boishakh"),
    # ---------------- Muslim ----------------
    "Eid-ul-Fitr": (r"Id-Ul-Fitr|Eid-Ul-Fitr|Ramzan-Id|Khutub-E-Ramzan", "Muslim", "Religious", "Eid al-Fitr"),
    "Eid-ul-Adha (Bakrid)": (r"Bakri|Id-Uz-Zuha|Id-ul-Zuha|Adha", "Muslim", "Religious", "Eid al-Adha"),
    "Milad-un-Nabi": (r"Milad|Baravafat|bara vafat", "Muslim", "Religious", "Mawlid"),
    "Muharram / Ashura": (r"Muharram|Moharam|Ashoora", "Muslim", "Religious", "Ashura"),
    "Jumat-ul-Vida": (r"Jumat-ul-Vida", "Muslim", "Religious", "Jumu'atul-Wida"),
    "Shab-e-Qadr": (r"Shab-I-Qadr", "Muslim", "Religious", "Laylat al-Qadr"),
    "Birthday of Hazrat Ali": (r"Hazr?a?t Ali|Hazarat Ali", "Muslim", "Commemoration", "Ali"),
    # ---------------- Christian ----------------
    "Christmas": (r"Christmas(?! Eve)", "Christian", "Religious", "Christmas"),
    "Christmas Eve": (r"Christmas Eve", "Christian", "Religious", "Christmas Eve"),
    "Good Friday": (r"Good Friday", "Christian", "Religious", "Good Friday"),
    "Maundy Thursday": (r"Maundy Thursday", "Christian", "Religious", "Maundy Thursday"),
    "Feast of St. Francis Xavier": (r"Francis Xavier", "Christian", "Religious", "Francis Xavier"),
    "Missionary Day (Mizoram)": (r"Missionary Day", "Christian", "Commemoration", "Christianity in Mizoram"),
    "Unitarian Anniversary Day": (r"Unitarian", "Christian", "Commemoration", "Unitarian Union of North East India"),
    # ---------------- Sikh ----------------
    "Guru Nanak Jayanti (Gurpurab)": (r"Guru Nanak", "Sikh", "Religious", "Guru Nanak Gurpurab"),
    "Guru Gobind Singh Jayanti": (r"Gobind Singh", "Sikh", "Religious", "Guru Gobind Singh"),
    "Martyrdom Day of Guru Arjan Dev": (r"Arjun Dev", "Sikh", "Commemoration", "Guru Arjan"),
    "Guru Hargobind Jayanti": (r"Hargobind", "Sikh", "Commemoration", "Guru Hargobind"),
    "Baisakhi (Vaisakhi)": (r"Baisakhi", "Sikh", "Harvest", "Vaisakhi"),
    # ---------------- Jain ----------------
    "Mahavir Jayanti": (r"Mahavir", "Jain", "Religious", "Mahavir Janma Kalyanak"),
    "Samvatsari (Paryushan)": (r"Samvatsari", "Jain", "Religious", "Samvatsari"),
    # ---------------- Buddhist ----------------
    "Buddha Purnima": (r"Buddha Pournima", "Buddhist", "Religious", "Buddha's Birthday"),
    "Losar": (r"\bLosar\b", "Buddhist", "New Year", "Losar"),
    "Losoong / Namsoong": (r"Lo+s+o+ng|Namsoong", "Buddhist", "New Year", "Losoong (festival)"),
    "Drukpa Tshe-zi": (r"Drukpa", "Buddhist", "Religious", "Drukpa Tsheshi"),
    "Saga Dawa": (r"Saga Dawa", "Buddhist", "Religious", "Saga Dawa"),
    "Pang Lhabsol": (r"Pang-Lhabsol", "Buddhist", "Religious", "Pang Lhabsol"),
    # ---------------- Parsi ----------------
    "Parsi New Year (Navroz, Shahenshahi)": (r"Parsi New Year", "Parsi", "New Year", "Nowruz"),
    # ---------------- Tribal / Indigenous ----------------
    "Sarhul": (r"Sarhul", "Tribal/Indigenous", "Seasonal", "Sarhul"),
    "Karma Puja": (r"Karma Puja", "Tribal/Indigenous", "Harvest", "Karam festival"),
    "Chapchar Kut": (r"Chapchar Kut", "Tribal/Indigenous", "Seasonal", "Chapchar Kut"),
    "Kut (Chin-Kuki-Mizo)": (r"(^|/)Kut(/|$)", "Tribal/Indigenous", "Harvest", "Kut festival"),
    "Garia Puja": (r"Garia Puja", "Tribal/Indigenous", "Religious", "Garia Puja"),
    "Kharchi Puja": (r"Kharchi", "Tribal/Indigenous", "Religious", "Kharchi Puja"),
    "Ker Puja": (r"Ker Puja", "Tribal/Indigenous", "Religious", "Ker Puja"),
    "Wangala": (r"Wangala", "Tribal/Indigenous", "Harvest", "Wangala"),
    "Nongkrem Dance": (r"Nongkrem", "Tribal/Indigenous", "Religious", "Nongkrem Dance"),
    "Shad Suk Mynsiem": (r"Shad Suk Mynsiem", "Tribal/Indigenous", "Seasonal", "Shad Suk Mynsiem"),
    "Behdienkhlam": (r"Beh D[ie]{2}nkhlam", "Tribal/Indigenous", "Religious", "Behdienkhlam"),
    "Seng Kut Snem": (r"Seng Kut ?[Ss]nem", "Tribal/Indigenous", "Religious", "Seng Khasi"),
    "Nyokum": (r"Nyokum", "Tribal/Indigenous", "Religious", "Nyokum"),
    "Lui-Ngai-Ni": (r"Lui-Ngai-Ni", "Tribal/Indigenous", "Seasonal", "Lui-Ngai-Ni"),
    "Gaan-Ngai": (r"Gaan-Ngai", "Tribal/Indigenous", "Religious", "Gaan-Ngai"),
    "Indigenous Faith Day (Arunachal)": (r"Indigenous Faith Day", "Tribal/Indigenous", "Commemoration", "Donyi-Polo"),
    "Tendong Lho Rum Faat": (r"Tendong", "Tribal/Indigenous", "Religious", "Tendong Lho Rum Faat"),
    "Biju / Buisu": (r"Biju|Buisu", "Tribal/Indigenous", "New Year", "Bizu"),
    "Cheiraoba (Meitei New Year)": (r"Cheiraoba", "Tribal/Indigenous", "New Year", "Cheiraoba"),
    "Yaosang": (r"Yaosang", "Tribal/Indigenous", "Religious/Seasonal", "Yaoshang"),
    "Ningol Chakkouba": (r"Ningol Chakkouba", "Tribal/Indigenous", "Cultural", "Ningol Chakouba"),
    "Imoinu Iratpa": (r"Imoinu", "Tribal/Indigenous", "Religious", "Imoinu Iratpa"),
}

# Anything in the RBI description that is not a festival (civic / state days / elections /
# leader anniversaries / administrative closures).  Used to label rows as non-festival.
NON_FESTIVAL = (r"Republic Day|Independence Day|Gandhi Jayanti|Ambedkar|May Day|Maharashtra Din|State ?Day|Statehood|"
                r"State Formation|State Inauguration|Election|Poll day|Birthday of Netaji|Tagore|Nazrul|Vivekananda|"
                r"Jagjivan|Shivaji|Hari Singh|Bir Bikram|Patel|Birsa Munda|Mookerjee|Raghunath Murmu|Surendrasai|"
                r"Maharana Pratap|Ayyankali|Mannam|Accession Day|Liberation|Patriot|MHIP|YMA|Tirot|Kiang Nangbah|"
                r"SoSo Tham|Togan|New Year.?s (Day|Eve)|New Year Celebration|Rajyothsava|Himachal Day|Bihar Di|"
                r"close their yearly accounts|rains|Manmohan|Achuthanandan|Consecration|Remna Ni|Thomas Jones|"
                r"Bank employees in Nagaland|close at 1400")
