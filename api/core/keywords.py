# --- keyword mapping (expanded based on new detailed questions) ---
# symptoms - expanded based on kb details
class KeywordMappings:
    def __init__(self, bonus_specific_keyword=2.0):
        self.bonus_specific_keyword = bonus_specific_keyword
        self.symptom_keywords = {
            "itching (maybe rate severity?)": [
                "itch",
                "pruritus",
                "pruritic",
                "itchy",
                "prickly",  # added prickly (cholinergic urticaria)
            ],
            "pain": [
                "pain",
                "hurt",
                "painful",  # added painful
                "paroxysmal pain",  # glomus tumor
            ],
            "tenderness to touch": [
                "tender",
                "tenderness",
                "painful",  # added painful as overlap
            ],
            "burning sensation": [
                "burn",
                "burning",
                "sting",
                "stinging",  # seems complete
            ],
            "redness": [
                "red",
                "reddish",
                "erythema",
                "erythematous",  # added reddish
                "violaceous",
                "purpuric",
                "purple",  # grouped purple tones
                "flushing",
                "bright red",
                "beefy-red",  # specific red types
                "pink",
                "salmon",  # pink/salmon tones
                "brownish",  # keep, but less specific (sarcoid, ks, pih link)
                "dusky",  # important for ischemia/sjs/nec fasc
                "orange",  # specific for prp
                "ecchymotic",  # bruise-like redness
                # removed "violaceous" duplicate
            ],
            "swelling": [
                "swell",
                "edema",
                "swollen",
                "indurated",
                "thickened",
                "enlargement",
                "boggy",
                "puffy",
                "brawny",  # added puffy (mctd), brawny (lds)
                "nodule",
                "tumor",
                "mass",
                "plaque",
                "hyperplasia",  # added related structural terms implying swelling/thickening
                # 'indurated' & 'thickened' also relate to morphology: thickened skin
            ],
            "dryness/flaking/scaling": [
                "dry",
                "xerosis",
                "asteatotic",
                "flake",
                "flaky",
                "scale",
                "scaling",
                "scaly",
                "desquamation",
                "rough",
                "sandpaper",
                "cracked",
                "craquele",  # added roughness/cracking
                "keratotic",
                "hyperkeratotic",  # added keratin terms
                "lichenified",  # thickened and scaly/dry appearance often
            ],
            "blisters (fluid-filled)": [
                "blister",
                "bulla",
                "bullae",
                "vesicle",
                "vesicular",
                "fluid-filled",  # added vesicular
                "flaccid",
                "tense",  # added types of blisters
                "hemorrhagic bullae",  # specific type
            ],
            "pus bumps (pimples)": [
                "pimple",
                "pus",
                "pustule",
                "pustular",
                "follicular pustule",  # added pustular
                "abscess",
                "suppurative",
                "fluctuant",  # added fluctuant
                "furuncle",
                "carbuncle",
                "boil",  # specific types
                "pyoderma",  # pus in skin
            ],
            "bleeding": [
                "bleed",
                "bleeding",
                "hemorrhage",
                "hemorrhagic",
                "friable",  # seems complete
            ],
            "oozing/weeping": [
                "ooze",
                "oozing",
                "weep",
                "weeping",
                "discharge",
                "exudate",
                "macerated",
                "drainage",
                "serous",  # added drainage, serous
            ],
            "numbness/tingling": [
                "numb",
                "numbness",
                "tingling",
                "paresthesia",
                "sensory loss",
                "prodrome",  # added prodrome
            ],
            "None of the above": [],
        }

        # Medical Conditions - Expanded and refined
        self.condition_keywords = {
            "Eczema / Atopic Dermatitis": [
                "eczema",
                "atopic dermatitis",
                "ad",
                "atopy",
                "dermatitis",  # Added dermatitis
                "nummular",
                "discoid",
                "asteatotic",
                "dyshidrotic",
                "pompholyx",  # Types of eczema
                "lichen simplex chronicus",
                "lsc",
                "prurigo",
                "contact dermatitis",  # Related itchy conditions
                "stasis dermatitis",
                "xerosis",  # Related conditions often in context
            ],
            "Psoriasis": [
                "psoriasis",
                "psoriatic",
                "guttate",
                "plaque",
                "inverse",
                "flexural",
                "pustular psoriasis",
                "palmoplantar pustulosis",
                "ppp",  # Specific types
            ],
            "Acne (severe or treated)": [
                "acne",
                "comedone",
                "comedones",
                "acne vulgaris",
                "cystic acne",  # Added types
                "acneiform",
                "chloracne",
                "favre-racouchot",  # Related conditions
            ],
            "Rosacea": [
                "rosacea",
                "rhinophyma",
                "periorificial dermatitis",
                "demodicosis",  # Includes variants and related
            ],
            "Skin Cancer History (BCC/SCC/Melanoma)": [
                "skin cancer",
                "cancer",
                "malignancy",
                "malignant",  # Added synonyms
                "bcc",
                "basal cell carcinoma",
                "scc",
                "squamous cell carcinoma",  # Specific types
                "melanoma",
                "bowen",
                "paget",
                "merkel",
                "dfsp",
                "ks",
                "kaposi",  # Other skin cancers from KB
                "angiosarcoma",
                "metastasis",
                "lymphoma cutis",
                "mycosis fungoides",
                "mf",  # Other skin cancers from KB
            ],
            "Pre-cancerous spots (AKs)": [
                "actinic keratosis",
                "ak",
                "solar keratosis",
                "pre-cancer",
                "dysplasia",  # Added synonyms
                "actinic cheilitis",
                "leukoplakia",  # Related pre-malignant
            ],
            "Shingles (Herpes Zoster)": [
                "shingles",
                "zoster",
                "herpes zoster",
                "vzv",
                "varicella zoster",  # Added synonyms
            ],
            "Cold sores (Herpes Simplex)": [
                "cold sore",
                "herpes",
                "herpes simplex",
                "hsv",
                "whitlow",  # Added synonyms
                "eczema herpeticum",
                "kaposi varicelliform",  # HSV complications
            ],
            "Warts": [
                "wart",
                "verruca",
                "verruca vulgaris",
                "verruca plana",
                "verruca plantaris",  # Added specific types
                "hpv",
                "human papillomavirus",
                "condyloma",
                "condyloma acuminatum",  # Added HPV and genital warts
            ],
            "Fungal Infections (Tinea/Candida)": [
                "fungus",
                "fungal",
                "tinea",
                "ringworm",
                "candida",
                "yeast",
                "mycosis",
                "dermatophyte",
                "onychomycosis",
                "tinea pedis",
                "tinea cruris",
                "tinea corporis",  # Specific tinea
                "tinea capitis",
                "tinea versicolor",
                "pityriasis versicolor",
                "malassezia",  # More specific types
                "pityrosporum",
                "thrush",
                "intertrigo",  # Candida related
                "sporotrichosis",
                "chromoblastomycosis",
                "cryptococcosis",  # Deep fungal from KB
            ],
            "Hives (Urticaria)": [
                "hives",
                "urticaria",
                "wheal",
                "wheals",
                "angioedema",  # Added angioedema
                "dermatographism",
                "cholinergic",
                "cold urticaria",
                "pressure urticaria",  # Specific types
            ],
            "Significant Sunburns (blistering)": [
                "sunburn",
                "blistering sunburn",
                "sun damage",
                "photodamage",
                "solar elastosis",  # Added related terms
            ],
            "Allergies (Hay fever, Asthma)": [
                "allerg",
                "hay fever",
                "asthma",
                "rhinitis",
                "atopy",
                "allergic rhinitis",  # Added full term
                "hypersensitivity",  # Broader term
            ],
            "Diabetes (Type 1 / Type 2)": [
                "diabete",
                "insulin resistance",
                "dm",
                "iddm",
                "niddm",  # Added abbreviations
                "diabetic dermopathy",
                "necrobiosis lipoidica",  # Specific diabetic skin signs
            ],
            "Thyroid disease (Hyper/Hypo)": [
                "thyroid",
                "hyperthyroid",
                "hypothyroid",
                "graves",
                "hashimoto",  # Added hashimoto
                "pretibial myxedema",
                "thyroid dermopathy",
                "thyroid acropachy",  # Specific signs
            ],
            "Autoimmune disease (Lupus, RA, IBD etc)": [
                "autoimmune",
                "lupus",
                "sle",
                "dle",
                "scle",
                "acle",  # Added lupus variants
                "rheumatoid arthritis",
                "ra",
                "ibd",
                "inflammatory bowel disease",
                "crohn",
                "ulcerative colitis",  # Added specifics
                "sjogren",
                "scleroderma",
                "ssc",
                "systemic sclerosis",
                "morphoea",  # Added specifics
                "pemphigoid",
                "pemphigus",
                "dermatomyositis",
                "dm",  # Added DM
                "connective tissue disease",
                "ctd",
                "mctd",  # Added MCTD
                "vasculitis",
                "polyarteritis nodosa",
                "pan",
                "gpa",
                "wegener",
                "mpa",
                "egpa",
                "churg-strauss",  # Vasculitides
                "behcet",
                "sarcoidosis",
                "alopecia areata",
                "vitiligo",
                "celiac",  # Others from KB review
                "relapsing polychondritis",  # Added RP
            ],
            "Immune system issues (HIV, Transplant)": [
                "immune",
                "immunosuppressed",
                "immunocompromised",
                "immunodeficiency",  # Added synonym
                "hiv",
                "aids",
                "transplant",
                "chemotherapy",
                "biologics",
                "steroid therapy",  # Added common causes
            ],
            "None of the above": [],
        }

        # Duration - Seems good, adding related KB terms
        self.duration_keywords = {
            "Less than 1 week": [
                "acute",
                "abrupt",
                "sudden",
                "days",
                "<1 week",
                "<6 weeks",
            ],  # Added <6wks for acute urticaria
            "1-4 weeks": [
                "acute",
                "subacute",
                "weeks",
                "1-4 weeks",
                "days-weeks",
            ],  # Added from KB timing
            "1-3 months": [
                "subacute",
                "months",
                "1-3 months",
                "~3 months",
            ],  # Added common timeframe for TE
            "3-6 months": [
                "subacute",
                "chronic",
                "persistent",
                "months",
                "3-6 months",
                ">6mo",
            ],  # Added >6mo overlap
            "6 months - 1 year": [
                "chronic",
                "persistent",
                "long",
                "6-12 months",
                ">6 months",
            ],
            "More than 1 year": ["chronic", "persistent", "long", "years", ">1 year"],
            "Unsure": [
                "variable",
                "recurrent",
                "relapsing",
            ],  # Map unsure/variable/recurrent nature here
        }

        # Location - Expanded based on KB specificity
        self.location_keywords = {
            "Face": [
                "face",
                "facial",
                "periorificial",
                "perioral",
                "perinasal",
                "periocular",  # Periorificial group
                "malar",
                "cheek",
                "forehead",
                "lip",
                "vermilion",
                "chin",
                "eyelid",
                "nose",  # Specific areas
                "submental",
                "retroauricular",
                "periorbital",
                "glabella",
                "temples",
                "mandible",  # More specifics
                "central face",
                "beard area",
                "nasolabial fold",  # Common descriptive areas
            ],
            "Scalp": [
                "scalp",
                "nuchae",
                "occipital",
                "posterior neck",
                "nape",
                "hairline",
                "vertex",
                "crown",  # Added crown
                "frontal hairline",
                "temporal recession",  # AGA patterns
            ],
            "Eyelids": [
                "eyelid",
                "periocular",
                "periorbital",
                "helitrope",  # Added heliotrope area
            ],
            "Ears": [
                "ear",
                "auricular",
                "retroauricular",
                "earlobe",  # Added earlobe (spared in RP)
            ],
            "Neck": ["neck", "nape", "nuchae", "posterior neck"],  # Seems complete
            "Chest": [
                "chest",
                "trunk",
                "upper trunk",
                "sternal",
                "inframammary",  # Added inframammary
                "sun-protected",
                "sun-exposed",  # Added exposure status
            ],
            "Back": [
                "back",
                "trunk",
                "upper trunk",
                "interscapular",
                "sacrum",
                "lumbar",
                "sun-protected",
                "sun-exposed",  # Added exposure status
            ],
            "Abdomen": [
                "abdomen",
                "abdominal",
                "trunk",
                "umbilical",
                "periumbilical",
                "sun-protected",
                "sun-exposed",  # Added exposure status
            ],
            "Arms": [
                "arm",
                "limb",
                "extremity",
                "upper limb",
                "extensor",
                "flexor",
                "antecubital",  # Added flexor/antecubital
                "forearm",
                "shoulder",
                "upper outer arm",  # Added shoulder, specific KP site
            ],
            "Hands/Fingers": [
                "hand",
                "finger",
                "palm",
                "palmar",
                "dorsal hand",
                "knuckle",
                "gottron",  # Added gottron area
                "acral",
                "digit",
                "digital",
                "periungual",
                "subungual",
                "nail fold",
                "cuticle",  # Added nail structures
            ],
            "Legs": [
                "leg",
                "limb",
                "extremity",
                "lower limb",
                "extensor",
                "flexor",
                "popliteal",  # Added flexor/popliteal
                "shin",
                "anterior leg",
                "pretibial",
                "calf",
                "posterior leg",
                "thigh",
                "knee",  # Added anterior/posterior/pretibial
            ],
            "Feet/Toes": [
                "foot",
                "feet",
                "toe",
                "sole",
                "plantar",
                "dorsal foot",
                "ankle",
                "acral",
                "digit",
                "digital",
                "periungual",
                "subungual",
                "nail fold",
                "cuticle",  # Added nail structures
                "interdigital",
                "web space",
                "toe web",  # Added synonyms
            ],
            "Groin": [
                "groin",
                "inguinal",
                "fold",
                "intertriginous",
                "sun-protected",  # Seems complete
            ],
            "Genitals": [
                "genital",
                "anogenital",
                "perianal",
                "penis",
                "scrotum",
                "vulva",
                "pubic",  # Seems complete
            ],
            "Buttocks": [
                "buttock",
                "gluteal",
                "fold",
                "intertriginous",
                "sacrum",
                "gluteal cleft",  # Added cleft
                "sun-protected",  # Seems complete
            ],
            "Underarms (Axillae)": [
                "axilla",
                "axillae",
                "underarm",
                "fold",
                "intertriginous",
                "sun-protected",  # Seems complete
            ],
            "Skin folds (general)": [
                "fold",
                "flexural",
                "intertriginous",
                "antecubital",
                "popliteal",
                "inframammary",
                "gluteal cleft",
                "sun-protected",  # Seems complete
            ],
            "Inside Mouth/Nose": [
                "oral",
                "mouth",
                "mucosa",
                "mucosal",
                "mucous membrane",  # Added synonym
                "buccal",
                "gingiva",
                "gingival",
                "tongue",
                "palate",
                "pharyngeal",  # Added gingival
                "nasal",
                "nose",
                "vermilion",  # Added vermilion border
            ],
            "All Over": [
                "widespread",
                "generalized",
                "diffuse",
                "trunk",
                "limbs",
                "extremities",
                "body",
                "systemic",
                "universal",
                "scattered",
                "disseminated",
                "multifocal",  # Added synonyms from patterns
            ],
            "Other: _________": [],
            "None of the above": [],
        }

        # Morphology - Expanded significantly
        self.morphology_keywords = {
            "Flat spots (discolored, not raised)": [
                "macule",
                "patch",
                "flat",
                "discolored",
                "spot",
                "mark",  # Added spot, mark
                "erythema",
                "purpura",
                "ecchymotic",
                "petechiae",
                "bruise-like",  # Color changes flat
                "hypopigmented",
                "hyperpigmented",
                "depigmented",
                "achromic",
                "white",  # Pigment loss flat
                "brown",
                "blue",
                "grey",
                "tan",
                "yellowish",
                "cafe-au-lait",
                "ashy",  # Other colors flat
                "lentigo",
                "ephelid",
                "freckle",
                "livedo",  # Specific flat lesion types
                "wickham's striae",  # Flat white lines in LP
            ],
            "Raised bumps (solid)": [
                "papule",
                "nodule",
                "plaque",
                "raised",
                "bump",
                "thickened",  # General raised terms
                "indurated",
                "firm",
                "hard",
                "soft",
                "doughy",
                "lobulated",  # Texture/consistency
                "dome-shaped",
                "polygonal",
                "planar",
                "flat-topped",
                "exophytic",  # Shape
                "fleshy",
                "pedunculated",
                "stalked",
                "fibroma",
                "neurofibroma",  # Specific types
                "vegetation",
                "papillomatous",
                "polypoid",  # Surface texture related
                "wheal",  # Urticaria lesion
                "horn",
                "keratosis",
                "hyperkeratotic",  # Keratin related bumps
                "xanthoma",
                "granuloma",
                "angioma",
                "hemangioma",  # Specific lesion types
                "comedo",
                "comedone",  # Specific acne lesion
            ],
            "Blisters (clear fluid-filled)": [
                "blister",
                "vesicle",
                "bulla",
                "bullae",
                "fluid-filled",
                "clear fluid",
                "flaccid",
                "tense",
                "vesiculopustule",  # Added types and mixed
                "lymphangioma",
                "frog spawn",  # Specific vesicular appearance
            ],
            "Pustules (pus-filled bumps)": [
                "pustule",
                "pus",
                "pus-filled",
                "pimple",
                "follicular pustule",
                "abscess",
                "suppurative",
                "fluctuant",
                "boil",
                "furuncle",
                "carbuncle",
                "pyoderma",
                "pyogenic",  # Pus related terms
                "vesiculopustule",
                "sterile pustule",  # Added mixed/specific types
            ],
            "Thickened/Leathery skin": [
                "thickened",
                "leathery",
                "lichenified",
                "indurated",
                "plaque",
                "sclerosis",
                "hardness",
                "fibrosis",
                "scar-like",
                "hyperkeratotic",  # Added related terms
            ],
            "Flaky/Scaly skin": [
                "flaky",
                "scale",
                "scaling",
                "scaly",
                "hyperkeratotic",
                "keratotic",
                "desquamation",
                "peeling",  # Added peeling
                "eczema-like",
                "psoriasis-like",
                "psoriasiform",  # Descriptive terms
                "ichthyosis",
                "ichthyosiform",
                "xerosis",
                "dry",  # Dry/scaling conditions
                "corn flake scale",
                "collarette of scale",  # Specific scale types
            ],
            "Crusts/Scabs": [
                "crust",
                "scab",
                "honey-colored crust",
                "serous crust",
                "hemorrhagic crust",  # Added types
            ],
            "Ulcer / Open sore": [
                "ulcer",
                "erosion",
                "sore",
                "open sore",
                "denuded",
                "excoriation",  # Added excoriation
                "punched-out",
                "crater",
                "fissure",  # Added related breakdown terms
                "eschar",
                "necrotic",
                "gangrene",  # Necrosis related
                "chancre",
                "aphthae",  # Specific ulcer types
            ],
            "Circular or Ring-shaped": [
                "circular",
                "ring",
                "annular",
                "coin-shaped",
                "nummular",
                "discoid",  # Added discoid
                "targetoid",
                "iris lesion",
                "bulls-eye",  # Target shapes
                "arcuate",
                "polycyclic",
                "serpiginous",  # Other shapes (serpiginous could be linear too)
                "round",
                "oval",  # Simple shapes
            ],
            "Linear (in a line)": [
                "linear",
                "line",
                "streak",
                "band",
                "striated",  # Added striated
                "dermatomal",
                "zosteriform",
                "koebner",
                "blaschko",  # Specific patterns
                "serpiginous",
                "track",  # Migrating line
            ],
            "Bruise-like / Purple discoloration": [
                "bruise",
                "bruise-like",
                "purple",
                "violaceous",
                "purpura",
                "palpable purpura",  # Added palpable
                "ecchymosis",
                "ecchymotic",
                "petechiae",
                "hemorrhagic",  # Bleeding related colors
                "dusky",
                "cyanotic",
                "livedo",
                "reticular",  # Vascular pattern colors
                "poikiloderma",  # Mixed atrophy, pigment, telangiectasia
            ],
            "Wart-like": [
                "wart-like",
                "verrucous",
                "papillomatous",
                "cauliflower",
                "hyperkeratotic",  # Overlap with flaky/scaly & raised bump
            ],
            "Other: _________": [],
            "None of the above": [],
        }

        # Systemic Symptoms - Enhanced
        self.systemic_symptons_keywords = {
            "Fever / Chills": [
                "fever",
                "febrile",
                "chill",
                "pyrexia",
                "systemic symptom",
                "malaise",
                "flu-like",
                "prodrome",
                "hypothermia",  # Added hypothermia (severe sepsis)
            ],
            "Unexplained Weight Loss (>10 lbs)": [
                "weight loss",
                "b symptom",
                "cachexia",  # Added cachexia
            ],
            "Unusual Fatigue / Tiredness": [
                "tired",
                "fatigue",
                "malaise",
                "systemic symptom",
                "lassitude",
                "lethargy",  # Added synonyms
            ],
            "Night Sweats": ["night sweats", "b symptom"],  # Seems complete
            "Joint Pain / Swelling": [
                "joint",
                "arthralgia",
                "arthritis",
                "arthropathy",
                "polyarthritis",
                "monoarthritis",  # Added types
            ],
            "Muscle Aches": [
                "muscle ache",
                "myalgia",
                "muscle weakness",
                "myopathy",
                "myositis",  # Added weakness/inflammation
            ],
            "Swollen Glands/Lymph Nodes (Neck/Armpits/Groin)": [
                "lump",
                "swollen",
                "lymphadenopathy",
                "adenopathy",
                "node",
                "gland",
                "lymph node",
                "bubo",
                "hilar lymphadenopathy",  # Added hilar for Sarcoid
            ],
            "Sores in mouth or genital area": [
                "sore",
                "ulcer",
                "erosion",
                "oral",
                "genital",
                "mucosal",
                "aphthae",
                "stomatitis",  # Added aphthae/stomatitis
                "gingivitis",
                "conjunctivitis",
                "uveitis",
                "ocular",  # Added other mucosal sites
            ],
            "Changes in hair or nails": [
                "hair loss",
                "alopecia",
                "shedding",
                "effluvium",
                "hirsutism",
                "hypertrichosis",  # Added shedding/excess hair
                "nail change",
                "onychodystrophy",
                "pitting",
                "ridging",
                "onycholysis",  # Added onycholysis
                "clubbing",
                "pterygium",
                "splinter hemorrhage",
                "beau lines",  # Added specific nail signs
            ],
            "None": ["asymptomatic"],  # Added asymptomatic here
        }

        # Triggers - Expanded based on KB examples
        self.trigger_keywords = {
            "Sunlight Exposure": [
                "sun",
                "photo",
                "light",
                "actinic",
                "uv",
                "sunlight",
                "phototoxic",
                "photoallergic",
            ],  # Added types
            "Heat / Sweating": [
                "heat",
                "sweat",
                "hot",
                "exercise",
                "occlusion",
            ],  # Added exercise/occlusion
            "Cold / Dry Air": ["cold", "dry air", "winter", "low humidity"],
            "Stress": ["stress", "emotional"],
            "Scratching / Rubbing": [
                "scratch",
                "rub",
                "friction",
                "koebner",
                "koebnerization",
                "excoriation",  # Added synonyms
                "trauma",
                "injury",
                "pressure",
                "mechanical",
                "pathergy",  # Added pathergy
            ],
            "Water (bathing, swimming)": [
                "water",
                "bathing",
                "swimming",
                "wet work",
                "aquatic",
                "seawater",
            ],  # Added aquatic/seawater
            "New soaps/lotions/detergents/cosmetics": [
                "contact",
                "allergen",
                "irritant",
                "soap",
                "cosmetic",
                "lotion",
                "preservative",  # Added preservative
                "fragrance",
                "detergent",
                "dye",
                "product",
                "topical",
                "shampoo",
                "hair dye",  # Added specifics
            ],
            "Contact with chemicals/metals": [
                "chemical",
                "metal",
                "nickel",
                "chromate",
                "rubber",
                "latex",  # Added specifics
                "contact",
                "allergen",
                "irritant",
                "exposure",
                "halogenated hydrocarbon",  # Added specific chem type
                "occupational",
                "solvent",  # Added solvent
            ],
            "Specific Foods: _________": [
                "food",
                "ingestion",
                "diet",
                "gluten",
                "seafood",  # Added examples
            ],
            "Specific Medications: _________": [
                "drug",
                "medication",
                "systemic",
                "topical",  # Added routes
                "steroid",
                "corticosteroid",
                "antibiotic",
                "lithium",
                "egfri",
                "ace inhibitor",  # Specific drug classes/examples from KB
                "anticonvulsant",
                "thiazide",
                "vaccine",
                "chemotherapy",
                "vancomycin",  # More examples
                "nsaid",
                "protein",
                "serum",  # Other substances
            ],
            "Hormonal changes (e.g., menstrual cycle)": [
                "hormone",
                "hormonal",
                "menstrual",
                "pregnancy",
                "postpartum",
                "ocp",
                "oral contraceptive",  # Added synonyms
                "puberty",
                "postmenopausal",
                "estrogen",  # Added life stages/specific hormone
            ],
            "Nothing specific noticed": [
                "idiopathic",
                "spontaneous",
                "unknown",
            ],  # Added related terms
            "Other: _________": [
                "infection",
                "strep",
                "viral",
                "bacterial",  # Infections as triggers
                "insect bite",
                "tick bite",
                "animal contact",
                "cat",
                "sheep",
                "goat",
                "cattle",  # Bites/Animal contact
                "plant",
                "poison ivy",
                "poison oak",
                "sumac",
                "furocoumarin",  # Plant triggers
                "tattoo",
                "vaccination",  # Procedure triggers
            ],
            "None of the above": [],
        }

        # Spread Pattern - Seems reasonable, refined based on KB terms
        self.spread_pattern_keywords = {
            "Outward from one spot": [
                "outward",
                "annular",
                "expanding",
                "central clearing",
                "peripheral",
                "centrifugal",
                "target",
                "radial growth",  # Added target, radial growth (melanoma)
            ],
            "In a straight line/band": [
                "linear",
                "line",
                "band",
                "streak",
                "striated",  # Added striated
                "dermatomal",
                "zosteriform",
                "sporotrichoid",
                "lymphatic spread",  # Added lymphatic
                "koebner",
                "blaschko",  # Patterns following lines
            ],
            "Same on both sides": ["symmetric", "bilateral"],  # Seems complete
            "Only one side": [
                "unilateral",
                "asymmetric",
                "dermatomal",
                "one side",
                "segmental",  # Added segmental (vitiligo/PWS)
            ],
            "Random spots": [
                "scattered",
                "random",
                "multiple",
                "disseminated",
                "multifocal",
                "crops",  # Existing seem good
                "irregular",
                "asymmetric",
                "grouped",
                "clustered",
                "satellite",  # Added clustered, satellite
                "moth-eaten",  # Specific pattern (syphilis alopecia)
            ],
            "Not spreading / Stable": [
                "stable",
                "not spreading",
                "static",
                "localized",
                "solitary",
                "fixed",  # Added localized/solitary/fixed (FDE)
            ],
        }

        # Age mapping - Expanded with KB terms
        self.age_keywords = {
            "Under 10": [
                "child",
                "infant",
                "infancy",
                "juvenile",
                "pediatric",
                "neonate",
                "neonatal",
                "<2 years",
                "<5",
                "<6 weeks",
                "age 3-14",
                "toddler",  # Added toddler
            ],
            "10-18": [
                "adolescent",
                "teen",
                "young",
                "juvenile",
                "pediatric",
                "child",
                "age 3-14",  # Seems reasonable
                "puberty",  # Added life stage
            ],
            "19-30": ["young adult", "young", "adult"],
            "31-45": ["adult", "middle-aged"],
            "46-65": [
                "middle-aged",
                "adult",
                "older",
                ">50",
                "postmenopausal",
            ],  # Added postmenopausal overlap
            "65+": ["elderly", "older adult", "age", ">50"],
            "Prefer not to say": [],
        }

        # Gender mapping - Looks good, added pregnancy terms
        self.gender_keywords = {
            "Male": ["male", "man", "men"],
            "Female": [
                "female",
                "woman",
                "women",
                "postmenopausal",
                "pregnancy",
                "pregnant",
                "postpartum",
                "gestationis",
            ],  # Added pregnant, gestationis
            "Prefer not to say": [],
        }

        self.specific_keyword_bonus_map = {
            "comedones": (
                "morphology",
                "Pustules (pus-filled bumps)",
                self.bonus_specific_keyword,
            ),  # Note: Comedones aren't pustules, maybe map to 'Raised bumps'? Revisit this mapping logic.
            "honey-colored crust": (
                "morphology",
                "Crusts/Scabs",
                self.bonus_specific_keyword,
            ),
            "pearly": (
                "morphology",
                "Raised bumps (solid)",
                self.bonus_specific_keyword,
            ),
            "telangiectasias": (
                "morphology",
                "Bruise-like / Purple discoloration",
                self.bonus_specific_keyword * 0.5,
            ),  # Telangiectasias are dilated vessels, not really bruises. Maybe map to 'Redness'? Revisit.
            "sandpaper": (
                "morphology",
                "Flaky/Scaly skin",
                self.bonus_specific_keyword,
            ),
            "burrow": (
                "morphology",
                "Linear (in a line)",
                self.bonus_specific_keyword * 1.5,
            ),
            "targetoid": (
                "morphology",
                "Circular or Ring-shaped",
                self.bonus_specific_keyword,
            ),
            "annular scaly border": (
                "morphology",
                "Circular or Ring-shaped",
                self.bonus_specific_keyword,
            ),  # Maybe better as "annular" AND "scaly"? Requires more complex logic.
            "satellite lesions": (
                "morphology",
                "Pustules (pus-filled bumps)",
                self.bonus_specific_keyword,
            ),  # Lesions could be papules too
            "satellite papules": (
                "morphology",
                "Raised bumps (solid)",
                self.bonus_specific_keyword,
            ),
            "umbilicated": (
                "morphology",
                "Raised bumps (solid)",
                self.bonus_specific_keyword * 1.5,
            ),
            "dermatomal": (
                "spread_pattern",
                "In a straight line/band",
                self.bonus_specific_keyword,
            ),
            "koplik spots": (
                "location",
                "Inside Mouth/Nose",
                self.bonus_specific_keyword * 2.0,
            ),
            "wickham's striae": (
                "morphology",
                "Flat spots (discolored, not raised)",
                self.bonus_specific_keyword * 1.5,
            ),
            "apple jelly": (
                "morphology",
                "Raised bumps (solid)",
                self.bonus_specific_keyword * 1.5,
            ),
            "heliotrope": (
                "location",
                "Eyelids",
                self.bonus_specific_keyword * 1.5,
            ),  # Could also be morphology 'Bruise-like/Purple discoloration'
            "gottron": (
                "location",
                "Hands/Fingers",
                self.bonus_specific_keyword * 1.5,
            ),  # Could also be morphology 'Raised bumps' or 'Purple discoloration'
            "sun-protected": ("location", "Chest", 3.0),
            "sun-protected": ("location", "Back", 3.0),
            "sun-protected": ("location", "Abdomen", 3.0),
            "sun-protected": ("location", "Buttocks", 3.0),
            "poikiloderma": ("morphology", "Bruise-like / Purple discoloration", 2.5),
            "chronic": ("duration", "More than 1 year", 1.5),
            "persistent": ("duration", "More than 1 year", 1.5),
            "lymphadenopathy": (
                "systemic_symptoms",
                "Swollen Glands/Lymph Nodes (Neck/Armpits/Groin)",
                2.0,
            ),
            "weight loss": (
                "systemic_symptoms",
                "Unexplained Weight Loss (>10 lbs)",
                2.0,
            ),
            # --- SUGGESTIONS FOR REVISITING SPECIFIC KEYWORD BONUS MAP ---
            # "comedones": Consider mapping to 'Raised bumps' or creating a specific 'Acne Lesions' category if needed. It's not a pustule.
            # "telangiectasias": Map to 'Redness' might be more accurate than 'Bruise-like'. Bonus weight seems low if it's a key feature (e.g., Rosacea ETR, BCC).
            # "annular scaly border": This needs AND logic ideally. As is, matching 'Circular or Ring-shaped' is okay but loses the 'scaly border' info which is key for Tinea.
            # "satellite lesions": This is vague. Could be papules or pustules. Need separate entries or map to a general 'spots' morphology?
            # "heliotrope"/"gottron": These are location *and* morphology. Current mapping is okay but maybe add morphology links too?
        }
