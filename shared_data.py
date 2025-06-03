preq = {
    "STA201": [], "HUM103": [], "BNG103": [], "EMB101": [],
    "MAT110": ["MAT120"], "MAT120": ["MAT215", "MAT216"], "MAT215": [], "MAT216": ["CSE330", "CSE423"],
    "PHY111": ["PHY112"], "PHY112": ["CSE250"],
    "ENG101": ["ENG102"], "ENG102": [],
    
    "CSE110": ["CSE111"], "CSE111": ["CSE220"], "CSE220": ["CSE221"],
    "CSE221": ["CSE321", "CSE331", "CSE370", "CSE422"],
    "CSE230": [], "CSE250": ["CSE251"], "CSE251": ["CSE260", "CSE350"],
    "CSE260": ["CSE340", "CSE341", "CSE460", "CSE461"],
    "CSE340": ["CSE341", "CSE420"], "CSE341": ["CSE360", "CSE461"],
    "CSE320": [], "CSE350": [], "CSE360": ["CSE461"],
    "CSE370": ["CSE470", "CSE471"], "CSE420": [], "CSE421": ["CSE400"], "CSE422": ["CSE400"],
    "CSE423": [], "CSE460": [], "CSE461": [], "CSE470": ["CSE400"], "CSE471": [],
    "CSE321": ["CSE420"], "CSE331": ["CSE420"], "CSE400": [], "CSE330": [],

    # Maximum one from
    "CST301": [], "CST302": [], "CST303": [], "CST304": [], "CST305": [],
    "CST306": [], "CST307": [], "CST308": [], "CST309": [], "CST310": [],

    # Minimum one from
    "PSY101": [], "SOC101": [], "ANT101": [], "POL101": [], "BUS201": [],
    "ECO101": [], "ECO102": [], "ECO105": [], "BUS102": [], "POL102": [],
    "DEV104": [], "POL201": [], "SOC201/ANT202": [], "ANT342": [], "ANT351": [], "BUS333": [],

    # Cannot be taken now
    "ACT201": [], "ACT202": [], "BUS101": [], "BUS202": [], "BCH101": [],
    "BTE101": [], "CHE110": [], "CHN101": [], "FRN101": [], "FIN301": [],
    "GEO101": [], "LAW101": [], "HUM111": [], "STA301": [],

    # Optional
    "CHE101": [], "BIO101": [], "ENV103": [],

    # Other general education
    "HUM101": [], "HUM102": [], "HST102": [], "HST104": [], "HUM207": [],
    "ENG113": [], "ENG114": [], "ENG115": [], "ENG333": []
}


science_st = {"CHE101", "BIO101", "ENV103"}

arts_st = {
    "HUM101", "HUM102", "HST102", "HST104", "HUM207",
    "ENG113", "ENG114", "ENG115", "ENG333"
}

cst_st = {
    "CST301", "CST302", "CST303", "CST304", "CST305",
    "CST306", "CST307", "CST308", "CST309", "CST310"
}

ss_st = {"PSY101", "SOC101", "ANT101", "POL101", "BUS201", "ECO101", "ECO102", "ECO105", "BUS102", "POL102", "DEV104", "POL201", "SOC201", "ANT342", "ANT351", "BUS333"}
to_remove = {'BRAC University', '', 'Kha 224, Bir Uttam Rafiqul Islam Avenue ', 'Merul Badda, Dhaka 1212.', '', 'Page 1 of 2', '', ' ', '', 'GRADE SHEET', '', 'UNOFFICIAL COPY', '', 'UNDERGRADUATE PROGRAM ', '',}

grades = ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "F", "W", "I"]

core = {
    "CSE110", "CSE111", "CSE220", "CSE221", "CSE230", "CSE250", "CSE251", "CSE260",
    "CSE320", "CSE321", "CSE330", "CSE331", "CSE340", "CSE341", "CSE350", "CSE360",
    "CSE370", "CSE420", "CSE421", "CSE422", "CSE423", "CSE460", "CSE461", "CSE470", "CSE471"
}

labs = {"CSE110", "CSE111", "CSE220", "CSE221", "CSE230", "CSE250", "CSE251", "CSE260",
    "CSE321", "CSE330", "CSE341", "CSE350", "CSE360",
    "CSE370", "CSE420", "CSE421", "CSE422", "CSE423", "CSE460", "CSE461", "CSE471", "PHY111", "PHY112", "MAT120"}