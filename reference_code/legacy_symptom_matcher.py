import re
import collections
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- Knowledge Base (Provided Text) ---
# IMPORTANT: This MUST contain the FULL text from your original prompt (all 23 sections).
# I have included placeholders for brevity here.
knowledge_base_text = """
Okay, here is the disease list reformatted into structured tags with simplified clinical rules, focusing on key differentiating features for the selected conditions within each category.

Disclaimer: These rules are simplified heuristics for illustrative or machine-learning conceptual purposes. They are not comprehensive diagnostic algorithms and cannot replace clinical judgment, patient history, examination, and appropriate investigations. Thresholds (e.g., "2+ Red Flags") are indicative.



1. Acne and Rosacea Photos

[Condition: Acne Vulgaris]

- Red Flags: Comedones (Open/Closed), Inflammatory Lesions (Papules/Pustules/Nodules/Cysts), Typical Distribution (Face/Chest/Back), Adolescent/Young Adult Onset

- Rule: IF Comedones AND 1+ Other Flag → Confidence Boost (Acne Vulgaris) + Suppress (Rosacea, Folliculitis)

- DDx: Rosacea, Folliculitis, Periorificial Dermatitis, Acneiform Drug Eruption

[Condition: Rosacea (Papulopustular)]

- Red Flags: Persistent Facial Erythema, Papules/Pustules (Central Face), Telangiectasias, NO Comedones, Flushing History

- Rule: IF NO Comedones AND 2+ Other Flags → Confidence Boost (Rosacea P/P) + Suppress (Acne Vulgaris, Periorificial Derm, Lupus)

- DDx: Acne Vulgaris, Periorificial Dermatitis, Seborrhoeic Dermatitis, Lupus Erythematosus

[Condition: Rosacea (Erythematotelangiectatic)]

- Red Flags: Persistent Facial Erythema, Prominent Telangiectasias, Flushing History, Skin Sensitivity, NO Comedones or Papules/Pustules

- Rule: IF Persistent Erythema AND Flushing AND NO Papules/Pustules/Comedones → Confidence Boost (Rosacea ETR) + Suppress (Acne, Lupus, Seborrhoeic Derm)

- DDx: Lupus Erythematosus, Seborrhoeic Dermatitis, Photodamage, Polycythemia

[Condition: Periorificial Dermatitis]

- Red Flags: Grouped Papules/Pustules (Small), Distribution (Perioral/Perinasal/Periocular), Vermilion Border Sparing, Female Predominance, Steroid Use History

- Rule: IF Typical Distribution AND Vermilion Sparing AND 2+ Other Flags → Confidence Boost (Periorificial Derm) + Suppress (Acne Vulgaris, Rosacea, Seborrhoeic Derm)

- DDx: Acne Vulgaris, Rosacea, Seborrhoeic Dermatitis, Contact Dermatitis

[Condition: Acneiform Drug Eruption]

- Red Flags: Abrupt Onset, Monomorphic Lesions (Papules OR Pustules), Atypical Distribution Possible, History of New Medication (Steroids, Lithium, EGFRi etc), Often Lacks Comedones

- Rule: IF Abrupt Onset AND Monomorphic Lesions AND Medication History → Confidence Boost (Acneiform Drug Eruption) + Suppress (Acne Vulgaris, Folliculitis)

- DDx: Acne Vulgaris, Bacterial Folliculitis, Malassezia Folliculitis

[Condition: Malassezia (Pityrosporum) Folliculitis]

- Red Flags: Itchy Follicular Papules/Pustules, Monomorphic Appearance, Distribution (Upper Trunk/Shoulders), Worsens with Sweat/Occlusion, KOH Positive for Yeast

- Rule: IF Itchy Follicular Lesions AND Typical Distribution AND (KOH Positive OR Monomorphic) → Confidence Boost (Malassezia Folliculitis) + Suppress (Acne Vulgaris, Bacterial Folliculitis)

- DDx: Acne Vulgaris, Bacterial Folliculitis, Acneiform Drug Eruption

[Condition: Bacterial Folliculitis]

- Red Flags: Follicular Pustules, Surrounding Erythema, Tender Lesions, Hair-Bearing Areas, Culture Positive (Staph aureus common)

- Rule: IF Follicular Pustules AND (Tenderness OR Culture Positive) → Confidence Boost (Bacterial Folliculitis) + Suppress (Acne Vulgaris, Malassezia Folliculitis)

- DDx: Acne Vulgaris, Malassezia Folliculitis, Pseudofolliculitis Barbae, Acneiform Drug Eruption

[Condition: Rhinophyma]

- Red Flags: Nasal Bulbous Enlargement, Thickened Skin, Prominent Pores/Sebaceous Hyperplasia, Erythema/Telangiectasias (Nose), History of Rosacea

- Rule: IF Nasal Enlargement AND Thickened Skin/Pores → Confidence Boost (Rhinophyma) + Suppress (Acne Scarring, Infection)

- DDx: Sebaceous Hyperplasia (severe), Basal Cell Carcinoma, Sarcoidosis, Lymphoma Cutis

[Condition: Hidradenitis Suppurativa (Axilla/Groin Focus)]

- Red Flags: Recurrent Painful Nodules/Abscesses, Intertriginous Areas (Axillae/Groin/Buttocks), Sinus Tracts, Scarring (Tombstone Comedones), Family History

- Rule: IF Recurrent Nodules/Abscesses AND Intertriginous Location AND 1+ Other Flag → Confidence Boost (Hidradenitis) + Suppress (Furunculosis, Acne Conglobata)

- DDx: Furunculosis, Crohn's Disease (metastatic), Acne Conglobata, Folliculitis

[Condition: Pseudofolliculitis Barbae]

- Red Flags: Inflammatory Papules/Pustules, Beard Area/Neck, Related to Shaving, Curly Hair Predisposition, Ingrown Hairs Visible

- Rule: IF Beard Area Lesions AND Shaving Related AND Ingrown Hairs → Confidence Boost (Pseudofolliculitis Barbae) + Suppress (Bacterial Folliculitis, Acne Vulgaris)

- DDx: Bacterial Folliculitis, Acne Vulgaris, Tinea Barbae

[Condition: Acne Keloidalis Nuchae]

- Red Flags: Firm Follicular Papules/Nodules, Occipital Scalp/Posterior Neck, Keloidal Scarring, Male Predominance, African Descent Common

- Rule: IF Occipital/Nape Location AND Keloidal Papules/Plaques → Confidence Boost (AKN) + Suppress (Folliculitis Decalvans, Acne Vulgaris)

- DDx: Folliculitis Decalvans, Dissecting Cellulitis, Acne Vulgaris (severe scarring)

[Condition: Chloracne]

- Red Flags: Numerous Comedones (Open/Closed), Straw-Colored Cysts, Distribution (Retroauricular/Malar/Axillae/Groin), History of Halogenated Hydrocarbon Exposure

- Rule: IF Numerous Comedones/Cysts AND Typical Distribution AND Exposure History → Confidence Boost (Chloracne) + Suppress (Acne Vulgaris, Favre-Racouchot)

- DDx: Acne Vulgaris, Favre-Racouchot Syndrome, Nevus Comedonicus

[Condition: Favre-Racouchot Syndrome]

- Red Flags: Elderly Patient, Severe Sun Damage (Solar Elastosis), Large Open/Closed Comedones, Cysts, Periorbital Predominance, Smoking History Common

- Rule: IF Elderly AND Severe Solar Elastosis AND Large Periorbital Comedones/Cysts → Confidence Boost (Favre-Racouchot) + Suppress (Acne Vulgaris, Chloracne)

- DDx: Acne Vulgaris, Chloracne, Sebaceous Hyperplasia

[Condition: Demodicosis (Rosacea-like)]

- Red Flags: Facial Erythema/Papules/Pustules, Dryness/Scaling, Follicular Scaling (Pityriasis Folliculorum), Burning/Itching, High Mite Count on Sampling

- Rule: IF Rosacea-like AND (Follicular Scaling OR High Mite Count) → Confidence Boost (Demodicosis) + Suppress (Rosacea [pure], Seborrhoeic Derm)

- DDx: Rosacea, Seborrhoeic Dermatitis, Periorificial Dermatitis, Contact Dermatitis

[Condition: Steroid Acne / Steroid Rosacea]
Red Flags: History of topical or systemic steroid use, Monomorphic papules/pustules (acne), Background erythema/telangiectasias/atrophy (rosacea variant), Often lacks comedones (steroid acne)
Rule: IF History of Steroid Use AND Acneiform/Rosacea-like Eruption → Confidence Boost (Steroid Acne/Rosacea) + Suppress (Acne Vulgaris, Rosacea [non-steroid], Folliculitis)
DDx: Acne Vulgaris, Rosacea (non-steroid), Folliculitis, Demodicosis

[Condition: Rosacea Fulminans (Pyoderma Faciale)]
Red Flags: Abrupt Onset, Severe Inflammatory Nodules/Cysts/Abscesses, Central Face, Primarily Young Women, NO Comedones, Negative Bacterial Cultures, NO Systemic Symptoms (unlike Acne Fulminans)
Rule: IF Abrupt Severe Cystic Facial Eruption AND Young Woman AND No Comedones/Systemic Symptoms → Confidence Boost (Rosacea Fulminans) + Suppress (Acne Fulminans, Severe Acne Vulgaris, Infection)
DDx: Acne Fulminans, Severe Acne Vulgaris (nodulocystic), Gram-negative folliculitis, Cutaneous infection

[Condition: Acne Mechanica]
Red Flags: History of Friction/Pressure/Occlusion (helmets, straps, clothing), Lesions Localized to Area of Mechanical Stress, Papules/Pustules/Comedones present
Rule: IF Acne Lesions AND Distribution Matches Friction/Pressure Area AND History of Exposure → Confidence Boost (Acne Mechanica) + Suppress (Acne Vulgaris [non-mechanical], Folliculitis)
DDx: Acne Vulgaris (non-mechanical), Folliculitis, Irritant Contact Dermatitis

[Condition: Neonatal Cephalic Pustulosis]
Red Flags: Onset First Few Weeks of Life (<6 weeks), Small Facial Papules/Pustules, NO Comedones, Likely Reaction to Malassezia
Rule: IF Neonate (<6 weeks) AND Facial Papules/Pustules AND NO Comedones → Confidence Boost (Neonatal Cephalic Pustulosis) + Suppress (Infantile Acne, Milia)
DDx: Infantile Acne, Milia, Transient Neonatal Pustular Melanosis

[Condition: Lupus Miliaris Disseminatus Faciei (LMDF)]
Red Flags: Chronic Facial Eruption, Small Discrete Dome-Shaped Reddish-Brown Papules, Often Periorificial (Eyes/Nose/Mouth), Heals with Scarring, Histology shows Caseating Granulomas
Rule: IF Chronic Discrete Facial Papules AND Periorificial Distribution AND Scarring → Confidence Boost (LMDF) + Suppress (Rosacea, Sarcoidosis, Acne)
DDx: Rosacea (Papulopustular), Sarcoidosis, Tuberculids, Syringoma, Trichoepithelioma



2. Actinic Keratosis Basal Cell Carcinoma and other Malignant Lesions

[Condition: Actinic Keratosis (AK)]

- Red Flags: Sun-Exposed Area, Rough/Sandpaper Texture, Erythematous Base, Adherent Scale, Elderly Patient

- Rule: IF Sun-Exposed AND Rough Texture AND Scaly Papule/Patch → Confidence Boost (AK) + Suppress (SCC, Seborrheic Keratosis)

- DDx: Squamous Cell Carcinoma (SCC), Seborrheic Keratosis, Bowen Disease, Discoid Lupus

[Condition: Squamous Cell Carcinoma in situ (Bowen Disease)]

- Red Flags: Persistent Scaly Patch/Plaque, Erythematous, Well-Demarcated, Sun-Exposed Area, No Spontaneous Resolution

- Rule: IF Persistent Well-Demarcated Scaly Plaque → Confidence Boost (Bowen's) + Suppress (Psoriasis, Eczema, Superficial BCC, AK)

- DDx: Psoriasis, Nummular Eczema, Superficial BCC, Actinic Keratosis

[Condition: Invasive Squamous Cell Carcinoma (SCC)]

- Red Flags: Indurated Papule/Nodule/Plaque, Keratotic/Crusted/Ulcerated Surface, Tender Lesion, Rapid Growth, Sun-Exposed Site (or Chronic Wound)

- Rule: IF Indurated AND (Ulcerated/Keratotic OR Rapid Growth) → Confidence Boost (SCC) + Suppress (AK, BCC, KA)

- DDx: Actinic Keratosis, Basal Cell Carcinoma, Keratoacanthoma, Verruca Vulgaris, Amelanotic Melanoma

[Condition: Keratoacanthoma (KA)]

- Red Flags: Very Rapid Growth (Weeks), Dome-Shaped Nodule, Central Keratin Plug/Crater, Sun-Exposed Site

- Rule: IF Rapid Growth AND Dome Shape AND Central Keratin Plug → Confidence Boost (KA) + Suppress (SCC, Verruca Vulgaris)

- DDx: Squamous Cell Carcinoma, Verruca Vulgaris, Prurigo Nodularis

[Condition: Basal Cell Carcinoma (BCC) - Nodular]

- Red Flags: Pearly Papule/Nodule, Telangiectasias Over Surface, Rolled Border, Central Ulceration Possible ('Rodent Ulcer'), Face Location Common

- Rule: IF Pearly Appearance AND Telangiectasias → Confidence Boost (Nodular BCC) + Suppress (Intradermal Nevus, Sebaceous Hyperplasia)

- DDx: Intradermal Nevus, Sebaceous Hyperplasia, SCC, Amelanotic Melanoma

[Condition: Basal Cell Carcinoma (BCC) - Superficial]

- Red Flags: Erythematous Patch/Plaque, Fine Thread-Like Pearly Border, Focal Erosions/Crusting, Trunk/Limbs Common, Slow Growth

- Rule: IF Erythematous Patch AND Fine Pearly Border → Confidence Boost (Superficial BCC) + Suppress (Bowen's, Eczema, Psoriasis)

- DDx: Bowen Disease, Nummular Eczema, Psoriasis, Tinea Corporis, AK

[Condition: Basal Cell Carcinoma (BCC) - Morphoeic/Infiltrative]

- Red Flags: Scar-Like Plaque, Indurated, Ill-Defined Borders, Whitish/Yellowish Color, Atrophy/Ulceration Possible, Face Location Common

- Rule: IF Scar-Like Plaque AND Indurated AND Ill-Defined → Confidence Boost (Morphoeic BCC) + Suppress (Scar, Morphoea)

- DDx: Scar, Morphoea (Localized Scleroderma), Microcystic Adnexal Carcinoma

[Condition: Actinic Cheilitis]

- Red Flags: Lower Lip Vermilion, Chronic Sun Exposure History, Dryness/Scaling/Atrophy, Blurring of Vermilion Border, Persistent Ulcer/Induration (Suggests SCC)

- Rule: IF Lower Lip AND Chronic Dryness/Scaling/Atrophy → Confidence Boost (Actinic Cheilitis) + Suppress (Eczematous Cheilitis, Herpes Labialis)

- DDx: Eczematous Cheilitis, Candidal Cheilitis, Lichen Planus, SCC

[Condition: Merkel Cell Carcinoma (MCC)]

- Red Flags: Rapidly Growing Nodule, Firm, Non-Tender, Red/Violaceous Color, Elderly/Immunosuppressed Patient, Head/Neck/Limbs Common

- Rule: IF Rapid Growth AND Firm Red/Violaceous Nodule AND Elderly/Immunosuppressed → Confidence Boost (MCC) + Suppress (BCC, SCC, Amelanotic Melanoma, Cyst)

- DDx: Basal Cell Carcinoma, Squamous Cell Carcinoma, Amelanotic Melanoma, Epidermoid Cyst (Inflamed), Lymphoma Cutis

[Condition: Dermatofibrosarcoma Protuberans (DFSP)]

- Red Flags: Slow-Growing Plaque/Nodule, Firm/Indurated, Adherent to Deeper Tissue, Trunk/Proximal Limbs Common, May Develop Nodules within Plaque

- Rule: IF Slow-Growing Firm Plaque AND Feels Deeply Fixed → Confidence Boost (DFSP) + Suppress (Keloid, Dermatofibroma)

- DDx: Keloid, Dermatofibroma (Cellular), Morphoea, Sarcoma (Other)

[Condition: Mycosis Fungoides (MF) - Patch/Plaque Stage]

- Red Flags: Persistent Eczema/Psoriasis-like Patches/Plaques, Chronic (>6mo), Poor Response to Steroids, Sun-Protected Areas (Buttocks/Trunk), Irregular Shapes, Atrophy/Poikiloderma Possible

- Rule: IF Chronic Persistent Patches/Plaques AND Sun-Protected Area AND 1+ Other Flag → Confidence Boost (MF) + Suppress (Eczema, Psoriasis, Parapsoriasis)

- DDx: Eczema (Nummular/Atopic), Psoriasis, Parapsoriasis, Contact Dermatitis

[Condition: Kaposi Sarcoma (KS)]

- Red Flags: Violaceous/Brownish Macules/Patches/Papules/Nodules, May Follow Skin Lines, Location Variable (Legs/Feet [Classic], Widespread [AIDS], Mucosa), ± Lymphedema, HHV-8 Association

- Rule: IF Violaceous/Brown Lesions AND (Typical Distribution OR HIV+ OR Immunosuppressed) → Confidence Boost (KS) + Suppress (Bruise, Angiosarcoma, Bacillary Angiomatosis)

- DDx: Bruise, Stasis Dermatitis, Angiosarcoma, Bacillary Angiomatosis, Melanoma (Nodular)

[Condition: Angiosarcoma]

- Red Flags: Elderly Patient, Scalp/Face Location Common, Bruise-Like Patches (Ecchymotic), Purpuric Lesions, Edema, History of Lymphedema (Stewart-Treves) or Radiation

- Rule: IF Bruise-Like Patch/Nodules AND (Scalp/Face elderly OR Lymphedema OR Radiation Field) → Confidence Boost (Angiosarcoma) + Suppress (Bruise, KS, Cellulitis)

- DDx: Bruise, Kaposi Sarcoma, Cellulitis, Rosacea (Severe Edematous)

[Condition: Extramammary Paget Disease (EMPD)]

- Red Flags: Persistent Eczema-like Plaque, Unilateral (Often), Genital/Perianal/Axillary Location, Itchy or Asymptomatic, Poor Response to Eczema Treatment

- Rule: IF Persistent Eczematous Plaque AND Typical Location (Apocrine areas) → Confidence Boost (EMPD) + Suppress (Eczema, Psoriasis, Tinea)

- DDx: Eczema (Contact/Atopic/Seborrhoeic), Inverse Psoriasis, Tinea Cruris, Bowen Disease

[Condition: Cutaneous Metastasis]
Red Flags: History of Primary Internal Malignancy (Lung, Breast, Colon, Melanoma etc.), Sudden Onset of Firm Nodule(s)/Plaque(s), Skin-Colored/Erythematous/Violaceous, Often Non-tender
Rule: IF History of Cancer AND New Firm Skin Nodule(s)/Plaque(s) → Confidence Boost (Cutaneous Metastasis - Biopsy confirms origin) + Suppress (Primary Skin Cancer, Cyst, Lymphoma Cutis)
DDx: Primary Skin Cancer (BCC, SCC, Melanoma), Epidermoid Cyst (Inflamed), Lymphoma Cutis, Sarcoidosis

[Condition: Atypical Fibroxanthoma (AFX)]
Red Flags: Elderly Patient, Sun-Damaged Head/Neck Skin, Rapidly Growing Reddish/Skin-Colored Papule/Nodule, Often Ulcerated
Rule: IF Elderly AND Sun-Damaged Head/Neck AND Rapidly Growing Papule/Nodule → Confidence Boost (AFX - Diagnosis of exclusion via biopsy) + Suppress (SCC, Amelanotic Melanoma, BCC)
DDx: Squamous Cell Carcinoma (SCC), Amelanotic Melanoma, Pyogenic Granuloma, Merkel Cell Carcinoma

[Condition: Verrucous Carcinoma]
Red Flags: Large Exophytic Warty Mass, Slow-Growing, Locally Destructive, Often on Foot (Epithelioma Cuniculatum), Oral Cavity, or Genitals (Buschke-Löwenstein)
Rule: IF Large Warty Exophytic Tumor AND Typical Location → Confidence Boost (Verrucous Carcinoma) + Suppress (Common Wart [Giant], SCC [conventional], KA)
DDx: Giant Condyloma Acuminatum, Squamous Cell Carcinoma (conventional), Keratoacanthoma, Deep Fungal Infection

[Condition: Lymphomatoid Papulosis (LyP)]
Red Flags: Chronic Recurrent Eruption, Crops of Reddish-Brown Papules/Nodules, Spontaneous Ulceration/Crusting/Healing (often with scarring), Histology Atypical (CD30+) but Clinically Benign Course
Rule: IF Recurrent Self-Healing Papulonodules/Ulcers → Confidence Boost (LyP - Biopsy essential) + Suppress (Insect Bites, Vasculitis, Pityriasis Lichenoides)
DDx: Persistent Insect Bite Reactions, Pityriasis Lichenoides et Varioliformis Acuta (PLEVA), Cutaneous Vasculitis, Arthropod Assault

[Condition: Cutaneous Pseudolymphoma]
Red Flags: History of Trigger (Insect Bite, Drug, Tattoo, Vaccination), Solitary or Few Papule(s)/Nodule(s)/Plaque(s), Reddish/Violaceous, Histology shows Dense Lymphoid Infiltrate (Polyclonal)
Rule: IF Solitary/Few Papule/Nodule AND Possible Trigger History AND Biopsy Shows Polyclonal Lymphoid Infiltrate → Confidence Boost (Pseudolymphoma) + Suppress (Lymphoma Cutis, Sarcoidosis, Jessner's)
DDx: Cutaneous B-Cell Lymphoma, Cutaneous T-Cell Lymphoma, Jessner's Lymphocytic Infiltrate, Sarcoidosis, Persistent Insect Bite Reaction


3. Atopic Dermatitis Photos

[Condition: Atopic Dermatitis (General)]

- Red Flags: Chronic Relapsing Course, Intense Pruritus, Typical Age-Dependent Distribution (Infant: Face/Extensors, Child/Adult: Flexures), Xerosis (Dry Skin), Personal/Family History of Atopy (Asthma/Allergic Rhinitis)

- Rule: IF Chronic Itch AND Typical Distribution/Morphology AND (Xerosis OR Atopy History) → Confidence Boost (Atopic Dermatitis) + Suppress (Scabies, Contact Derm, Psoriasis)

- DDx: Scabies, Allergic Contact Dermatitis, Seborrhoeic Dermatitis, Psoriasis, Nummular Eczema

[Condition: Infantile Atopic Dermatitis]

- Red Flags: Onset < 2 years, Facial (Cheeks) and Extensor Limb Involvement, Oozing/Crusting Lesions, Intense Itch (Rubbing), Family History of Atopy

- Rule: IF Infant AND Face/Extensor Eczema AND Itch/Oozing → Confidence Boost (Infantile AD) + Suppress (Seborrhoeic Derm, Scabies)

- DDx: Seborrhoeic Dermatitis, Scabies, Contact Dermatitis

[Condition: Childhood Atopic Dermatitis]

- Red Flags: Age 2-Puberty, Flexural Involvement Predominant (Antecubital/Popliteal fossae, Neck), Lichenified/Papular Lesions, Chronic Itch, Xerosis

- Rule: IF Child AND Flexural Eczema AND Lichenification/Itch → Confidence Boost (Childhood AD) + Suppress (Psoriasis, Contact Derm)

- DDx: Psoriasis, Allergic Contact Dermatitis, Tinea Corporis

[Condition: Adult Atopic Dermatitis]

- Red Flags: Adult Onset or Persistence, Flexural Lichenification, Hand/Eyelid/Face/Neck Involvement Common, Chronic Severe Itch, Xerosis

- Rule: IF Adult AND Flexural Lichenification AND Chronic Itch → Confidence Boost (Adult AD) + Suppress (Psoriasis, Contact Derm, Scabies, CTCL)

- DDx: Allergic/Irritant Contact Dermatitis, Psoriasis, Scabies, Cutaneous T-Cell Lymphoma (MF)

[Condition: Eczema Herpeticum]

- Red Flags: History of Atopic Dermatitis, Sudden Eruption of Monomorphic Vesicles/Punched-Out Erosions, Lesions Clustered in Areas of Eczema, Fever/Malaise Possible

- Rule: IF AD History AND Acute Monomorphic Vesicles/Erosions → Confidence Boost (Eczema Herpeticum) + Suppress (AD Flare, Impetigo)

- DDx: Severe Atopic Dermatitis Flare, Bullous Impetigo, Varicella

[Condition: Bacterial Impetiginization (of AD)]

- Red Flags: Underlying Atopic Dermatitis, Weeping/Oozing Lesions, Golden-Yellow Crusting, Increased Redness/Pain

- Rule: IF AD History AND Weeping AND Honey-Colored Crusts → Confidence Boost (Impetiginized AD) + Suppress (AD Flare, Eczema Herpeticum)

- DDx: Acute Atopic Dermatitis Flare, Eczema Herpeticum
[Condition: Xerosis (in Atopic Context)]

Red Flags: Generalized Dry Skin, Rough Texture, Flaking, Associated with Atopic Dermatitis, Winter exacerbation

Rule: IF Generalized Dry Skin AND History of Atopy → Confidence Boost (Xerosis related to AD) + Suppress (Ichthyosis, Asteatotic Eczema)

DDx: Ichthyosis Vulgaris, Asteatotic Eczema, Medication Side Effect

[Condition: Lichenification (in Atopic Context)]

Red Flags: Thickened Skin, Accentuated Skin Lines, Resulting from Chronic Rubbing/Scratching, Often in Flexures/Neck/Ankles in AD

Rule: IF Thickened Skin with Increased Skin Lines AND History of Chronic Itch/AD → Confidence Boost (Lichenification secondary to AD) + Suppress (Lichen Simplex Chronicus [primary], Psoriasis)

DDx: Lichen Simplex Chronicus (if primary focus), Chronic Eczema (other types), Psoriasis

[Condition: Nummular Eczema (Discoid Eczema) - As related to AD]

Red Flags: Coin-Shaped Plaques, Well-Demarcated, Intensely Itchy, Initially Vesicular then Scaly/Crusted, Limbs Common, Can occur within Atopic Dermatitis pattern

Rule: IF Coin-Shaped Eczematous Plaques (potentially with AD history) → Confidence Boost (Nummular Eczema) + Suppress (Tinea Corporis, Psoriasis, Impetigo)

DDx: Tinea Corporis, Psoriasis, Impetigo (Crusted Stage), Bowen Disease (Note: DDx from original standalone entry)

[Condition: Prurigo Nodularis (in Atopic Context)]

Red Flags: Intense Itch, Firm Dome-Shaped Nodules, Often Excoriated, Extensor Surfaces Common, Associated with Chronic Scratching (often in severe AD)

Rule: IF Intense Itch AND Firm Excoriated Nodules AND (Often History of AD) → Confidence Boost (Prurigo Nodularis) + Suppress (Hypertrophic Lichen Planus, Scabies Nodules, Insect Bites)

DDx: Hypertrophic Lichen Planus, Scabies Nodules, Persistent Insect Bite Reactions, Multiple Keratoacanthomas

[Condition: Keratosis Pilaris (Association with AD)]

Red Flags: Small Rough Follicular Papules ('Chicken Skin'), Often on Upper Outer Arms/Thighs/Cheeks, Common in Atopic Individuals, Dry Skin association

Rule: IF Rough Follicular Papules AND Typical Distribution (Arms/Thighs) → Confidence Boost (Keratosis Pilaris) + Suppress (Folliculitis, Acne)

DDx: Folliculitis, Acne Vulgaris, Lichen Spinulosus




4. Bullous Disease Photos

[Condition: Bullous Pemphigoid (BP)]

- Red Flags: Elderly Patient, Intense Pruritus (often precedes blisters), Tense Bullae (Large), Urticarial Plaques, Subepidermal Split (Biopsy), Linear IgG/C3 at DEJ (DIF)

- Rule: IF Elderly AND Tense Bullae AND Intense Itch → Confidence Boost (BP) + Suppress (Pemphigus Vulgaris, Bullous Drug Eruption)

- DDx: Pemphigus Vulgaris, Epidermolysis Bullosa Acquisita, Bullous Drug Eruption, Bullous Insect Bites, Dermatitis Herpetiformis

[Condition: Pemphigus Vulgaris (PV)]

- Red Flags: Oral Erosions (Common First Sign), Flaccid Blisters (Rupture Easily), Painful Erosions, Positive Nikolsky Sign, Intraepidermal Split (Acantholysis on Biopsy), Net-Like IgG/C3 (DIF)

- Rule: IF Oral Erosions AND Flaccid Blisters/Erosions → Confidence Boost (PV) + Suppress (BP, Aphthous Stomatitis, SJS/TEN)

- DDx: Bullous Pemphigoid, Mucous Membrane Pemphigoid, Aphthous Stomatitis, SJS/TEN, Paraneoplastic Pemphigus

[Condition: Pemphigus Foliaceus (PF)]

- Red Flags: Superficial Erosions/Crusts ('Corn Flake' Scale), Flaccid Blisters (Often Not Seen), Seborrhoeic Distribution (Scalp/Face/Upper Trunk), No/Rare Mucosal Involvement, Superficial Acantholysis (Biopsy)

- Rule: IF Crusted/Scaly Erosions AND Seborrhoeic Distribution AND NO Mucosal Lesions → Confidence Boost (PF) + Suppress (Impetigo, Seborrhoeic Dermatitis, BP)

- DDx: Impetigo, Seborrhoeic Dermatitis, Lupus Erythematosus, Bullous Pemphigoid (rare superficial variant)

[Condition: Mucous Membrane Pemphigoid (MMP)]

- Red Flags: Predominant Mucosal Involvement (Oral Erosions/Desquamative Gingivitis, Ocular Scarring/Symblepharon, Genital/Pharyngeal/Esophageal), Scarring Lesions (Skin/Mucosa), Subepidermal Split (Biopsy), Linear IgG/C3 at DEJ (DIF)

- Rule: IF Mucosal Erosions AND Scarring (Ocular/Skin) → Confidence Boost (MMP) + Suppress (PV, Oral Lichen Planus, BP)

- DDx: Pemphigus Vulgaris, Erosive Lichen Planus, Bullous Pemphigoid, Aphthous Stomatitis

[Condition: Dermatitis Herpetiformis (DH)]

- Red Flags: Intense Pruritus, Grouped Papules/Vesicles (Often Excoriated), Symmetrical Extensor Distribution (Elbows/Knees/Buttocks/Scalp), Gluten Sensitivity Association, Granular IgA in Papillae (DIF)

- Rule: IF Intense Itch AND Grouped Extensor Vesicles/Papules AND Granular IgA (DIF) → Confidence Boost (DH) + Suppress (Scabies, Eczema, BP)

- DDx: Scabies, Atopic/Nummular Eczema, Bullous Pemphigoid, Linear IgA Bullous Dermatosis

[Condition: Linear IgA Bullous Dermatosis (LABD)]

- Red Flags: Annular Vesicles/Bullae ('Cluster of Jewels' / 'String of Pearls'), Urticarial Plaques Possible, Pruritus, Linear IgA at DEJ (DIF), Can be Drug-Induced (Vancomycin common)

- Rule: IF Annular Blisters AND Linear IgA (DIF) → Confidence Boost (LABD) + Suppress (BP, DH, Bullous Drug Eruption)

- DDx: Bullous Pemphigoid, Dermatitis Herpetiformis, Bullous SLE, Bullous Drug Eruption

[Condition: Epidermolysis Bullosa Acquisita (EBA)]

- Red Flags: Skin Fragility, Trauma-Induced Blisters/Erosions (Mechanobullous), Acral Distribution (Hands/Feet/Elbows/Knees), Scarring, Milia Formation, Linear IgG/C3 at DEJ (Dermal side on Salt-Split DIF)

- Rule: IF Skin Fragility AND Acral Blistering/Scarring/Milia AND IgG on Dermal side (Salt-Split DIF) → Confidence Boost (EBA) + Suppress (BP, PCT, Dystrophic EB)

- DDx: Bullous Pemphigoid, Porphyria Cutanea Tarda, Dystrophic Epidermolysis Bullosa (inherited)

[Condition: Stevens-Johnson Syndrome / Toxic Epidermal Necrolysis (SJS/TEN)]

- Red Flags: Acute Onset Post Drug Exposure, Fever/Malaise, Painful Skin, Dusky Red Macules, Widespread Blistering/Epidermal Detachment, Severe Mucosal Involvement (Oral/Ocular/Genital), Positive Nikolsky Sign

- Rule: IF Acute Onset AND Widespread Detachment AND Severe Mucosal Involvement → Confidence Boost (SJS/TEN) + Suppress (SSSS, PV, AGEP)

- DDx: Staphylococcal Scalded Skin Syndrome, Pemphigus Vulgaris (severe), AGEP, Severe AD Flare with Eczema Herpeticum, GVHD (acute)

[Condition: Bullous Fixed Drug Eruption (BFDE)]

- Red Flags: Recurrent Blistering Lesion(s) in Same Site(s), Triggered by Specific Drug, Round/Oval Dusky Red/Violaceous Plaque Base, Heals with Hyperpigmentation

- Rule: IF Recurrent Blister(s) AND Same Site AND Drug History → Confidence Boost (BFDE) + Suppress (Herpes Simplex, Bullous Bite)

- DDx: Herpes Simplex, Bullous Insect Bite Reaction, Bullous Pemphigoid (localized)

[Condition: Hailey-Hailey Disease (Benign Familial Pemphigus)]

- Red Flags: Recurrent Erosions/Vesicles, Intertriginous Areas (Axillae/Groin/Neck), Macerated/Fissured Appearance ('Cobblestone'), Family History, Worsens with Heat/Friction, Acantholysis (Biopsy, No Autoantibodies)

- Rule: IF Recurrent Intertriginous Erosions AND Family History AND Acantholysis (Biopsy) → Confidence Boost (Hailey-Hailey) + Suppress (Candidiasis, Intertrigo, Pemphigus)

- DDx: Intertrigo (Candidal/Bacterial), Inverse Psoriasis, Pemphigus Vegetans, Darier Disease
[Condition: Pemphigoid Gestationis (PG)]

Red Flags: Pregnancy or Postpartum Onset, Intense Pruritus (often starts periumbilical), Urticarial Papules/Plaques progressing to Tense Blisters, Autoimmune (Antibodies to BP180)

Rule: IF Pregnancy/Postpartum AND Intense Pruritus/Urticarial Lesions THEN Blisters → Confidence Boost (PG) + Suppress (PUPPP, Bullous Pemphigoid, Drug Eruption)

DDx: Polymorphic Eruption of Pregnancy (PUPPP), Bullous Pemphigoid, Drug Eruption, Acute Urticaria



5. Cellulitis Impetigo and other Bacterial Infections

[Condition: Impetigo (Non-bullous)]

- Red Flags: Superficial Erosions, Golden-Yellow ('Honey-Colored') Crusts, Face (Perioral/Perinasal) or Extremities Common, Contagious (esp. Children)

- Rule: IF Honey-Colored Crusts → Confidence Boost (Impetigo) + Suppress (Eczema Herpeticum, Tinea Faciei)

- DDx: Eczema Herpeticum, Tinea Faciei/Corporis, Allergic Contact Dermatitis (crusted)

[Condition: Bullous Impetigo]

- Red Flags: Flaccid Superficial Blisters (Clear/Cloudy Fluid), Rupture Easily Leaving Collarette of Scale, Thin Brown Crust, Trunk Common (Infants/Children), Staph aureus Toxin

- Rule: IF Flaccid Blisters AND Collarette of Scale → Confidence Boost (Bullous Impetigo) + Suppress (BP, Pemphigus, SSSS)

- DDx: Bullous Pemphigoid, Pemphigus Foliaceus, Staphylococcal Scalded Skin Syndrome, Bullous Insect Bites

[Condition: Ecthyma]

- Red Flags: "Punched-Out" Ulcers, Thick Overlying Crust, Lower Extremities Common, Heals with Scarring, Deeper than Impetigo

- Rule: IF Punched-Out Ulcers AND Thick Crusts → Confidence Boost (Ecthyma) + Suppress (Impetigo, Vasculitis Ulcer)

- DDx: Impetigo (severe), Vasculitic Ulcer, Pyoderma Gangrenosum (small lesions)

[Condition: Cellulitis]

- Red Flags: Spreading Erythema/Warmth/Swelling/Tenderness, Ill-Defined Borders, Unilateral Limb Common, ± Fever/Chills, Portal of Entry Often Visible (Wound/Tinea Pedis)

- Rule: IF Spreading Erythema/Warmth/Swelling AND Ill-Defined Border → Confidence Boost (Cellulitis) + Suppress (Stasis Derm, Contact Derm, Erysipelas)

- DDx: Stasis Dermatitis, Lipodermatosclerosis, Contact Dermatitis, Deep Vein Thrombosis (DVT), Erysipelas

[Condition: Erysipelas]

- Red Flags: Bright Red Indurated Plaque, Sharply Demarcated Raised Border ('Step-Off'), Face ('Butterfly') or Lower Leg Common, Acute Onset, Fever Common, Strep pyogenes usual cause

- Rule: IF Bright Red Plaque AND Sharply Demarcated Raised Border → Confidence Boost (Erysipelas) + Suppress (Cellulitis, Lupus [Malar Rash], Contact Derm)

- DDx: Cellulitis, Malar Rash (Lupus), Allergic Contact Dermatitis, Angioedema

[Condition: Folliculitis (Bacterial)]

- Red Flags: Pustules Centered on Hair Follicles, Erythema, Tender, Hair-Bearing Areas, Staph aureus common

- Rule: IF Follicular Pustules → Confidence Boost (Bacterial Folliculitis) + Suppress (Acne, Malassezia Folliculitis)

- DDx: Acne Vulgaris, Malassezia Folliculitis, Pseudofolliculitis Barbae, Keratosis Pilaris (inflamed)

[Condition: Furuncle (Boil)]

- Red Flags: Tender Red Nodule Around Hair Follicle, Becomes Fluctuant, Points and Drains Pus, Staph aureus usual cause

- Rule: IF Tender Follicular Nodule AND Fluctuance/Drainage → Confidence Boost (Furuncle) + Suppress (Cyst [Inflamed], Hidradenitis)

- DDx: Epidermoid Cyst (Inflamed), Hidradenitis Suppurativa, Folliculitis (Deep)

[Condition: Carbuncle]

- Red Flags: Large Painful Abscess, Multiple Draining Follicular Openings, Nape of Neck/Back Common, Systemic Symptoms Likely, Staph aureus usual cause

- Rule: IF Large Follicular Abscess AND Multiple Drainage Points → Confidence Boost (Carbuncle) + Suppress (Furuncle, Hidradenitis Abscess)

- DDx: Large Furuncle, Hidradenitis Suppurativa Abscess, Cutaneous Anthrax (later stage)

[Condition: Staphylococcal Scalded Skin Syndrome (SSSS)]

- Red Flags: Infant/Young Child, Abrupt Fever/Irritability, Diffuse Erythema, Widespread Superficial Peeling/Blistering, Positive Nikolsky Sign, Mucosa Spared (Usually)

- Rule: IF Infant AND Widespread Peeling AND Positive Nikolsky AND SPARED Mucosa → Confidence Boost (SSSS) + Suppress (SJS/TEN, Bullous Impetigo)

- DDx: SJS/TEN (mucosa involved), Bullous Impetigo (localized), Kawasaki Disease (rash different), Severe Sunburn

[Condition: Necrotizing Fasciitis]

- Red Flags: Severe Pain Out of Proportion to Skin Signs, Rapid Progression, Dusky/Violaceous Skin, Blistering (Hemorrhagic), Crepitus (Gas), Systemic Toxicity (Shock)

- Rule: IF Severe Pain AND Rapid Progression AND Dusky Skin/Blistering/Crepitus → Confidence Boost (Necrotizing Fasciitis) + Suppress (Cellulitis, Gas Gangrene) - URGENT SURGICAL CONSULT

- DDx: Severe Cellulitis, Gas Gangrene (Clostridial Myonecrosis), Pyoderma Gangrenosum (Rapid)

[Condition: Erythrasma]

- Red Flags: Reddish-Brown Patches, Skin Folds (Groin/Axillae/Toe Webs), Well-Demarcated, Fine Scale/Wrinkling, Coral-Red Fluorescence (Wood's Lamp)

- Rule: IF Intertriginous Brownish Patch AND Coral-Red Fluorescence → Confidence Boost (Erythrasma) + Suppress (Tinea Cruris, Candida Intertrigo)

- DDx: Tinea Cruris, Candida Intertrigo, Inverse Psoriasis, Seborrhoeic Dermatitis

[Condition: Pitted Keratolysis]

- Red Flags: Multiple Small Pits ('Punched-Out'), Plantar Surface (Soles), Pressure-Bearing Areas, Malodor Common, Hyperhidrosis Association

- Rule: IF Plantar Pits AND Malodor/Hyperhidrosis → Confidence Boost (Pitted Keratolysis) + Suppress (Warts, Tinea Pedis)

- DDx: Plantar Warts (mosaic), Tinea Pedis, Corns/Calluses

[Condition: Cutaneous Tuberculosis (Lupus Vulgaris)]

- Red Flags: Chronic Persistent Plaque(s), Reddish-Brown Color, 'Apple Jelly' Nodules (on Diascopy), Face/Neck Common, Slow Progression, History of TB Exposure/Risk

- Rule: IF Chronic Brownish Plaque AND Apple Jelly Nodules → Confidence Boost (Lupus Vulgaris) + Suppress (Sarcoidosis, Leishmaniasis, Lymphoma)

- DDx: Sarcoidosis, Leishmaniasis, Deep Fungal Infection, Lymphoma Cutis, Tertiary Syphilis

[Condition: Atypical Mycobacterial Infection (M. marinum)]

- Red Flags: Papules/Nodules/Ulcers on Extremity, History of Aquatic Exposure (Fish Tank, Pool, Ocean), Slow Growth, ± Sporotrichoid Spread (Nodules along lymphatics)

- Rule: IF Extremity Lesion(s) AND Aquatic Exposure History AND Slow Growth → Confidence Boost (Atypical Mycobacteria) + Suppress (Sporotrichosis, Bacterial Infection)

- DDx: Sporotrichosis, Bacterial infection (Staph/Strep), Deep Fungal Infection, Foreign Body Granuloma

[Condition: Leprosy (Hansen Disease)]

- Red Flags: Hypopigmented/Erythematous Patch(es) with Sensory Loss, Thickened Peripheral Nerves, ± Nodules/Infiltration (Lepromatous), Endemic Area Exposure

- Rule: IF Skin Patch AND Sensory Loss AND/OR Thickened Nerves → Confidence Boost (Leprosy) + Suppress (Tinea Corporis, Sarcoid, Mycosis Fungoides)

- DDx: Tinea Corporis, Granuloma Annulare, Sarcoidosis, Mycosis Fungoides, Vitiligo

[Condition: Lyme Disease (Erythema Migrans)]

- Red Flags: Expanding Annular Red Rash (>5cm), ± Central Clearing ('Bull's-Eye'), History of Tick Bite/Exposure in Endemic Area, Days-Weeks Post Bite

- Rule: IF Expanding Annular Rash >5cm AND Tick Exposure History → Confidence Boost (Erythema Migrans) + Suppress (Tinea Corporis, Granuloma Annulare, Cellulitis)

- DDx: Tinea Corporis, Granuloma Annulare, Cellulitis, Insect Bite Reaction

[Condition: Cat Scratch Disease]

- Red Flags: Papule/Pustule at Scratch/Bite Site, Followed by Tender Regional Lymphadenopathy, ± Fever/Malaise, History of Cat Contact

- Rule: IF Inoculation Lesion AND Regional Lymphadenopathy AND Cat Contact → Confidence Boost (Cat Scratch Disease) + Suppress (Bacterial Lymphadenitis, Tularemia)

- DDx: Bacterial Lymphadenitis, Tularemia, Atypical Mycobacterial Infection, Lymphoma


[Condition: Necrotizing Fasciitis]

Red Flags: Severe Pain Out of Proportion to Skin Signs, Rapid Progression, Dusky/Violaceous Skin, Blistering (Hemorrhagic), Crepitus (Gas), Systemic Toxicity (Shock)

Rule: IF Severe Pain AND Rapid Progression AND Dusky Skin/Blistering/Crepitus → Confidence Boost (Necrotizing Fasciitis) - URGENT SURGICAL CONSULT + Suppress (Cellulitis, Gas Gangrene)

DDx: Severe Cellulitis, Gas Gangrene (Clostridial Myonecrosis), Pyoderma Gangrenosum (Rapid)

[Condition: Pitted Keratolysis]

Red Flags: Multiple Small Pits ('Punched-Out'), Plantar Surface (Soles), Pressure-Bearing Areas, Malodor Common, Hyperhidrosis Association

Rule: IF Plantar Pits AND Malodor/Hyperhidrosis → Confidence Boost (Pitted Keratolysis) + Suppress (Warts, Tinea Pedis)

DDx: Plantar Warts (mosaic), Tinea Pedis, Corns/Calluses

[Condition: Cutaneous Tuberculosis (Lupus Vulgaris)]

Red Flags: Chronic Persistent Plaque(s), Reddish-Brown Color, 'Apple Jelly' Nodules (on Diascopy), Face/Neck Common, Slow Progression, History of TB Exposure/Risk

Rule: IF Chronic Brownish Plaque AND Apple Jelly Nodules → Confidence Boost (Lupus Vulgaris) + Suppress (Sarcoidosis, Leishmaniasis, Lymphoma)

DDx: Sarcoidosis, Leishmaniasis, Deep Fungal Infection, Lymphoma Cutis, Tertiary Syphilis

[Condition: Atypical Mycobacterial Infection (M. marinum)]

Red Flags: Papules/Nodules/Ulcers on Extremity, History of Aquatic Exposure (Fish Tank, Pool, Ocean), Slow Growth, ± Sporotrichoid Spread (Nodules along lymphatics)

Rule: IF Extremity Lesion(s) AND Aquatic Exposure History AND Slow Growth → Confidence Boost (Atypical Mycobacteria) + Suppress (Sporotrichosis, Bacterial Infection)

DDx: Sporotrichosis, Bacterial infection (Staph/Strep), Deep Fungal Infection, Foreign Body Granuloma

[Condition: Leprosy (Hansen Disease)]

Red Flags: Hypopigmented/Erythematous Patch(es) with Sensory Loss, Thickened Peripheral Nerves, ± Nodules/Infiltration (Lepromatous), Endemic Area Exposure

Rule: IF Skin Patch AND Sensory Loss AND/OR Thickened Nerves → Confidence Boost (Leprosy) + Suppress (Tinea Corporis, Sarcoid, Mycosis Fungoides)

DDx: Tinea Corporis, Granuloma Annulare, Sarcoidosis, Mycosis Fungoides, Vitiligo

[Condition: Lyme Disease (Erythema Migrans)]

Red Flags: Expanding Annular Red Rash (>5cm), ± Central Clearing ('Bull's-Eye'), History of Tick Bite/Exposure in Endemic Area, Days-Weeks Post Bite

Rule: IF Expanding Annular Rash >5cm AND Tick Exposure History → Confidence Boost (Erythema Migrans) + Suppress (Tinea Corporis, Granuloma Annulare, Cellulitis)

DDx: Tinea Corporis, Granuloma Annulare, Cellulitis, Insect Bite Reaction (Note: Also listed under Scabies/Lyme/Bites)

[Condition: Cat Scratch Disease]

Red Flags: Papule/Pustule at Scratch/Bite Site, Followed by Tender Regional Lymphadenopathy, ± Fever/Malaise, History of Cat Contact

Rule: IF Inoculation Lesion AND Regional Lymphadenopathy AND Cat Contact → Confidence Boost (Cat Scratch Disease) + Suppress (Bacterial Lymphadenitis, Tularemia)

DDx: Bacterial Lymphadenitis, Tularemia, Atypical Mycobacterial Infection, Lymphoma

[Condition: Erysipeloid]

Red Flags: Occupational Exposure (Butchers, Fishermen), Well-defined Purplish-Red Lesion, Often Diamond-Shaped, Usually on Hand/Fingers, Spreads Slowly Peripherally, Pain/Burning Prominent

Rule: IF Purplish-Red Hand Lesion AND Occupational Exposure (Meat/Fish) → Confidence Boost (Erysipeloid) + Suppress (Cellulitis, Contact Dermatitis)

DDx: Cellulitis, Allergic Contact Dermatitis, Fixed Drug Eruption

[Condition: Actinomycosis]

Red Flags: Chronic Infection, Forms Abscesses/Draining Sinus Tracts, Often Cervicofacial ('Lumpy Jaw'), Discharges "Sulfur Granules" (Bacterial Colonies)

Rule: IF Chronic Draining Sinus/Abscess (esp. Jaw) AND Sulfur Granules → Confidence Boost (Actinomycosis) + Suppress (TB, Nocardiosis, Deep Fungal Infection)

DDx: Tuberculosis (Scrofuloderma), Nocardiosis, Deep Fungal Infection, Malignancy

[Condition: Botryomycosis]

Red Flags: Chronic Bacterial Infection (often Staph aureus), Forms Granules mimicking Fungal Mycetoma, Subcutaneous Nodules/Abscesses/Sinuses

Rule: IF Chronic Suppurative Nodules/Sinuses AND Granules (Bacterial on culture) → Confidence Boost (Botryomycosis) + Suppress (Mycetoma [Fungal], Actinomycosis, TB)

DDx: Mycetoma (Fungal), Actinomycosis, Tuberculosis, Deep Fungal Infection

[Condition: Anthrax (Cutaneous)]

Red Flags: Exposure History (Animals/Hides/Bioterrorism), Itchy Papule → Vesicle/Bulla → Painless Black Necrotic Eschar with surrounding Edema

Rule: IF Painless Black Eschar AND Edema AND Exposure History → Confidence Boost (Cutaneous Anthrax) + Suppress (Spider Bite, Infection [other])

DDx: Brown Recluse Spider Bite, Severe Bacterial Infection (e.g., Pseudomonas), Orf (later stage)

[Condition: Vibrio vulnificus Infection]

Red Flags: Seawater Exposure (Wound) or Raw Seafood Ingestion, Esp. Liver Disease/Immunocompromised, Rapidly Progressive Cellulitis, Hemorrhagic Bullae, Sepsis/Shock potential

Rule: IF Rapid Cellulitis/Bullae AND Seawater/Seafood Exposure (esp. with Liver Disease) → Confidence Boost (Vibrio vulnificus) + Suppress (Necrotizing Fasciitis, Other Cellulitis)

DDx: Necrotizing Fasciitis (Strep/Polymicrobial), Severe Cellulitis (Staph/Strep), Aeromonas Infection




6. Eczema Photos

[Condition: Contact Dermatitis (Allergic - ACD)]

- Red Flags: Itchy Eczematous Reaction, Localized to Contact Area, Sharp Margins/Geometric Shapes Possible, Linear Streaks (Plants), Delayed Onset (1-3 days post exposure)

- Rule: IF Eczema AND Distribution Matches Exposure AND Delayed Onset → Confidence Boost (ACD) + Suppress (ICD, Atopic Derm, Tinea)

- DDx: Irritant Contact Dermatitis, Atopic Dermatitis, Nummular Eczema, Tinea Corporis

[Condition: Contact Dermatitis (Irritant - ICD)]

- Red Flags: Burning/Stinging Sensation, Erythema/Dryness/Scaling/Fissuring, Occurs Quickly Post Exposure, Severity Dose-Dependent, Affects Anyone Exposed Sufficiently

- Rule: IF Burning/Stinging AND Related to Irritant Exposure → Confidence Boost (ICD) + Suppress (ACD, Atopic Derm)

- DDx: Allergic Contact Dermatitis, Atopic Dermatitis, Asteatotic Eczema

[Condition: Seborrhoeic Dermatitis]

- Red Flags: Greasy Yellowish Scale, Erythematous Base, Distribution (Scalp/Eyebrows/Nasolabial Folds/Chest), Malassezia Association

- Rule: IF Greasy Scale AND Typical Seborrhoeic Distribution → Confidence Boost (Seb Derm) + Suppress (Psoriasis, Rosacea, Tinea Faciei)

- DDx: Psoriasis (Sebopsoriasis), Rosacea, Tinea Faciei/Capitis, Atopic Dermatitis (Face)

[Condition: Nummular Eczema (Discoid Eczema)]

- Red Flags: Coin-Shaped Plaques, Well-Demarcated, Intensely Itchy, Vesicular Initially then Scaly/Crusted, Limbs Common

- Rule: IF Coin-Shaped Eczematous Plaques → Confidence Boost (Nummular Eczema) + Suppress (Tinea Corporis, Psoriasis)

- DDx: Tinea Corporis, Psoriasis, Impetigo (Crusted Stage), Bowen Disease

[Condition: Stasis Dermatitis (Gravitational Eczema)]

- Red Flags: Lower Legs (esp. Medial Ankle), Signs of Venous Insufficiency (Edema/Varicosities/Hemosiderin), Itchy/Scaly/Erythematous Plaques, ± Ulceration Risk

- Rule: IF Lower Leg Eczema AND Signs of Venous Insufficiency → Confidence Boost (Stasis Derm) + Suppress (Cellulitis, Contact Derm)

- DDx: Cellulitis, Allergic/Irritant Contact Dermatitis, Asteatotic Eczema, Lichen Simplex Chronicus

[Condition: Dyshidrotic Eczema (Pompholyx)]

- Red Flags: Deep-Seated Vesicles ('Tapioca Pudding'), Palms/Soles/Sides of Fingers/Toes, Intensely Itchy, Recurrent Episodes

- Rule: IF Deep Hand/Foot Vesicles AND Intense Itch → Confidence Boost (Pompholyx) + Suppress (ACD, Tinea Pedis/Manuum, Palmoplantar Pustulosis)

- DDx: Allergic Contact Dermatitis, Tinea Pedis/Manuum (Inflammatory), Palmoplantar Pustulosis, Id Reaction

[Condition: Asteatotic Eczema (Eczema Craquelé)]

- Red Flags: Dry Cracked Skin ('Crazy Paving' / 'Cracked Porcelain'), Lower Legs Common, Elderly Patient, Winter/Low Humidity Trigger

- Rule: IF Dry Cracked Pattern AND Lower Legs AND Elderly/Dry Environment → Confidence Boost (Asteatotic Eczema) + Suppress (ICD, Stasis Derm)

- DDx: Irritant Contact Dermatitis, Stasis Dermatitis, Xerosis (Severe)

[Condition: Lichen Simplex Chronicus (LSC)]

- Red Flags: Thickened Skin (Lichenification), Accentuated Skin Lines, Intense Localized Itch, Chronic Rubbing/Scratching History, Well-Demarcated Plaque(s)

- Rule: IF Lichenified Plaque AND Intense Localized Itch → Confidence Boost (LSC) + Suppress (Psoriasis, Chronic Eczema)

- DDx: Psoriasis, Chronic Atopic/Contact Eczema, Hypertrophic Lichen Planus, Prurigo Nodularis

[Condition: Juvenile Plantar Dermatosis]

- Red Flags: Child (Age 3-14), Symmetric Dry/Shiny/Glazed Skin, Scaling/Fissuring Possible, Weight-Bearing Soles (Spares Toe Webs/Dorsum), Improves in Summer/With Age

- Rule: IF Child AND Symmetric Glazed Soles (Spares Webs) → Confidence Boost (JPD) + Suppress (Tinea Pedis, Atopic Derm [Foot])

- DDx: Tinea Pedis, Atopic Dermatitis (Foot), Allergic Contact Dermatitis (Shoe)

[Condition: Id Reaction (Autosensitization)]

- Red Flags: Acute Symmetric Eruption (Papules/Vesicles), Often Hands/Feet (Pompholyx-like), Occurs During Flare of Primary Dermatitis/Infection Elsewhere (e.g., Tinea Pedis, Stasis Dermatitis)

- Rule: IF Acute Symmetric Papulovesicular Rash AND Concomitant Primary Inflammation Elsewhere → Confidence Boost (Id Reaction) + Suppress (Dyshidrotic Eczema [Primary], ACD)

- DDx: Dyshidrotic Eczema (Primary), Allergic Contact Dermatitis, Drug Eruption

[Condition: Pityriasis Alba]

- Red Flags: Ill-Defined Hypopigmented Patches, Slight Scale, Face/Neck/Upper Arms Common, Children/Young Adults, Often History of Atopy

- Rule: IF Ill-Defined Pale Scaly Patches AND Typical Location/Age → Confidence Boost (Pityriasis Alba) + Suppress (Tinea Versicolor, Vitiligo)

- DDx: Tinea Versicolor, Post-Inflammatory Hypopigmentation, Vitiligo, Nummular Eczema (Resolving)



7. Exanthems and Drug Eruptions

[Condition: Morbilliform Drug Eruption]

- Red Flags: Widespread Symmetric Maculopapular Rash, Starts Trunk -> Periphery, ± Itch/Low Fever, Onset 1-2 Weeks Post New Drug

- Rule: IF Widespread Maculopapular Rash AND Recent New Drug → Confidence Boost (Morbilliform Drug Eruption) + Suppress (Viral Exanthem)

- DDx: Viral Exanthem (Measles, Rubella etc.), Kawasaki Disease, Early SJS/DRESS

[Condition: Urticarial Drug Eruption]

- Red Flags: Acute Onset Itchy Wheals (<24h duration each) / Angioedema, Temporally Related to Drug Exposure

- Rule: IF Acute Wheals/Angioedema AND Drug History → Confidence Boost (Urticarial Drug Eruption) + Suppress (Food Allergy, Idiopathic Urticaria)

- DDx: Acute Urticaria (Other Causes), Urticarial Vasculitis (lesions >24h)

[Condition: Fixed Drug Eruption (FDE)]

- Red Flags: Recurrent Lesion(s) in Same Site(s), Triggered by Specific Drug, Round/Oval Dusky Red/Violaceous Plaque(s), ± Blistering, Post-Inflammatory Hyperpigmentation

- Rule: IF Recurrent Lesion(s) AND Same Site(s) AND Drug History → Confidence Boost (FDE) + Suppress (Herpes Simplex, EM)

- DDx: Herpes Simplex, Erythema Multiforme, Insect Bite Reaction (Persistent)

[Condition: Stevens-Johnson Syndrome / Toxic Epidermal Necrolysis (SJS/TEN)]

- Red Flags: Acute Onset Post Drug, Fever/Painful Skin, Dusky Macules -> Blistering/Detachment, Severe Mucosal Involvement (Oral/Ocular/Genital), Positive Nikolsky

- Rule: IF Acute Detachment AND Mucosal Involvement AND Drug History → Confidence Boost (SJS/TEN) + Suppress (SSSS, PV, AGEP) - URGENT

- DDx: Staphylococcal Scalded Skin Syndrome, Pemphigus Vulgaris, AGEP, Severe GVHD

[Condition: DRESS / DIHS]

- Red Flags: Delayed Onset (2-8 Weeks Post Drug), Widespread Rash (Morbilliform -> Erythroderma), Facial Edema, Fever, Lymphadenopathy, Eosinophilia, Internal Organ Involvement (Liver/Kidney etc)

- Rule: IF Delayed Onset AND Widespread Rash/Fever AND Eosinophilia AND Organ Involvement → Confidence Boost (DRESS) + Suppress (Morbilliform Eruption, SJS/TEN, Viral Exanthem with complications) - URGENT

- DDx: Severe Morbilliform Drug Eruption, SJS/TEN, Hypereosinophilic Syndrome, Viral Exanthem with organ involvement, Lymphoma

[Condition: Acute Generalized Exanthematous Pustulosis (AGEP)]

- Red Flags: Rapid Onset (Days Post Drug), High Fever, Numerous Small Non-Follicular Pustules on Erythema, Starts in Folds -> Generalizes, Resolves with Desquamation

- Rule: IF Rapid Onset AND Fever AND Widespread Small Pustules (Non-Follicular) → Confidence Boost (AGEP) + Suppress (Pustular Psoriasis, SJS/TEN with pustules)

- DDx: Generalized Pustular Psoriasis, SJS/TEN, Folliculitis (Widespread), Candidiasis (Generalized)

[Condition: Serum Sickness / SSLR]

- Red Flags: Onset 1-3 Weeks Post Drug/Protein, Fever, Rash (Urticarial/Morbilliform/Purpuric), Arthralgia/Arthritis, ± Lymphadenopathy

- Rule: IF Fever AND Rash AND Arthralgia AND 1-3 Week Latency Post Exposure → Confidence Boost (Serum Sickness/SSLR) + Suppress (Viral Exanthem, Drug Eruption [Simple])

- DDx: Viral Exanthem, Morbilliform Drug Eruption, Acute Urticaria, Early Vasculitis

[Condition: Drug-Induced Photosensitivity]

- Red Flags: Rash Limited to Sun-Exposed Areas, Exaggerated Sunburn (Phototoxic) OR Eczematous (Photoallergic), History of Photosensitizing Drug

- Rule: IF Sun-Exposed Distribution AND Drug History → Confidence Boost (Drug Photosensitivity) + Suppress (PMLE, Lupus [Cutaneous])

- DDx: Polymorphic Light Eruption (PMLE), Lupus Erythematosus (SCLE/ACLE), Solar Urticaria, Phytophotodermatitis

[Condition: Measles (Rubeola)]

- Red Flags: Prodrome (Fever, Cough, Coryza, Conjunctivitis), Koplik Spots (Oral), Descending Morbilliform Rash (Starts Face/Behind Ears), Unvaccinated Status

- Rule: IF Prodrome AND Koplik Spots AND Descending Rash → Confidence Boost (Measles) + Suppress (Rubella, Drug Eruption, Kawasaki)

- DDx: Rubella, Morbilliform Drug Eruption, Kawasaki Disease, Roseola Infantum, Erythema Infectiosum

[Condition: Rubella (German Measles)]

- Red Flags: Mild Fever/Malaise, Postauricular/Occipital Lymphadenopathy, Rapidly Spreading Maculopapular Rash (Face -> Down, Clears Quickly), Unvaccinated Status

- Rule: IF Mild Prodrome AND Posterior Lymphadenopathy AND Rapid Descending Rash → Confidence Boost (Rubella) + Suppress (Measles, Drug Eruption, Roseola)

- DDx: Measles, Morbilliform Drug Eruption, Roseola Infantum, Erythema Infectiosum

[Condition: Erythema Infectiosum (Fifth Disease)]

- Red Flags: 'Slapped Cheek' Facial Erythema, Followed by Reticular/Lacy Rash on Limbs/Trunk, Parvovirus B19 Cause, Often Affects Children

- Rule: IF 'Slapped Cheeks' AND Lacy Limb/Trunk Rash → Confidence Boost (Fifth Disease) + Suppress (Rubella, Drug Eruption)

- DDx: Rubella, Morbilliform Drug Eruption, Lupus Erythematosus

[Condition: Roseola Infantum (Exanthem Subitum)]

- Red Flags: Infant/Toddler, High Fever (3-5 days), Rash Appears AS Fever Breaks, Maculopapular Rash Primarily on Trunk, Child Often Well When Rash Appears, HHV-6/7 Cause

- Rule: IF Infant AND High Fever THEN Rash → Confidence Boost (Roseola) + Suppress (Measles, Rubella, Drug Eruption)

- DDx: Measles, Rubella, Morbilliform Drug Eruption, Enteroviral Exanthem

[Condition: Hand, Foot, and Mouth Disease (HFMD)]

- Red Flags: Oral Vesicles/Ulcers, Papules/Vesicles on Hands/Feet (Palms/Soles characteristic), Usually Children <5, Coxsackie/Enterovirus Cause

- Rule: IF Oral Lesions AND Hand/Foot Lesions → Confidence Boost (HFMD) + Suppress (Herpetic Gingivostomatitis, Varicella, Aphthous Stomatitis)

- DDx: Herpetic Gingivostomatitis, Varicella, Aphthous Stomatitis, Herpangina

[Condition: Varicella (Chickenpox)]

- Red Flags: Generalized Itchy Rash, Lesions in Multiple Stages Simultaneously (Papules/Vesicles/Crusts), 'Dewdrop on Rose Petal' Vesicles, Fever/Malaise, VZV Primary Infection

- Rule: IF Vesicular Rash AND Multiple Stages Present → Confidence Boost (Varicella) + Suppress (Insect Bites, HFMD, Disseminated Herpes)

- DDx: Insect Bites (Papular Urticaria), Hand Foot and Mouth Disease, Disseminated Herpes Simplex, Drug Eruption (Vesicular)

[Condition: Lichenoid Drug Eruption]

- Red Flags: Pruritic Violaceous Papules/Plaques (LP-like), ± Widespread/Photodistributed, History of Causative Drug (e.g., Thiazides, ACE-i), Onset Weeks-Months Post Drug

- Rule: IF LP-like Lesions AND Drug History → Confidence Boost (Lichenoid Drug Eruption) + Suppress (Lichen Planus [Idiopathic])

- DDx: Lichen Planus (Idiopathic), Psoriasis, Eczema



8. Hair Loss Photos Alopecia and other Hair Diseases

[Condition: Androgenetic Alopecia (Male Pattern)]

- Red Flags: Male Patient, Gradual Onset, Patterned Hair Loss (Temporal Recession / Vertex Thinning), Family History, Miniaturization on Trichoscopy

- Rule: IF Male AND Typical Pattern (Temples/Vertex) AND Gradual Onset → Confidence Boost (Male AGA) + Suppress (TE, Alopecia Areata)

- DDx: Telogen Effluvium, Alopecia Areata (Diffuse), Chronic Telogen Effluvium

[Condition: Androgenetic Alopecia (Female Pattern)]

- Red Flags: Female Patient, Gradual Diffuse Thinning (Crown/Top of Scalp), Frontal Hairline Preservation, Widened Central Part ('Christmas Tree'), Miniaturization on Trichoscopy

- Rule: IF Female AND Crown Thinning AND Frontal Preservation → Confidence Boost (Female AGA) + Suppress (TE, Alopecia Areata)

- DDx: Telogen Effluvium, Chronic Telogen Effluvium, Alopecia Areata (Diffuse), Thyroid Dysfunction

[Condition: Telogen Effluvium (TE)]

- Red Flags: Acute Diffuse Hair Shedding, Positive Hair Pull Test (Telogen Bulbs), History of Trigger (~3 months prior: Illness/Surgery/Childbirth/Stress/Diet), Scalp Appears Normal

- Rule: IF Diffuse Shedding AND Positive Pull Test AND Trigger History → Confidence Boost (TE) + Suppress (AGA, Alopecia Areata)

- DDx: Androgenetic Alopecia, Alopecia Areata (Diffuse), Chronic Telogen Effluvium, Drug-Induced Alopecia

[Condition: Alopecia Areata (AA)]

- Red Flags: Smooth Well-Demarcated Patch(es) of Hair Loss, Exclamation Mark Hairs (Periphery), Non-Scarring, Autoimmune Association Possible, Nail Pitting Possible

- Rule: IF Smooth Patch(es) AND Exclamation Mark Hairs → Confidence Boost (AA) + Suppress (Tinea Capitis, Trichotillomania)

- DDx: Tinea Capitis, Trichotillomania, Traction Alopecia, Secondary Syphilis

[Condition: Tinea Capitis]

- Red Flags: Child Predominance, Scaly Patch(es) with Hair Loss/Broken Hairs ('Black Dots'), ± Inflammation (Kerion), ± Occipital Lymphadenopathy, Fungal Culture/KOH Positive

- Rule: IF Scalp Scaling/Hair Loss AND (Black Dots OR Kerion OR Positive Mycology) → Confidence Boost (Tinea Capitis) + Suppress (AA, Seborrheic Derm, Psoriasis)

- DDx: Alopecia Areata, Seborrhoeic Dermatitis, Psoriasis, Trichotillomania, Bacterial Folliculitis

[Condition: Traction Alopecia]

- Red Flags: Hair Loss Along Marginal Hairline (Frontal/Temporal), History of Tight Hairstyles (Braids/Ponytails/Weaves), Follicular Inflammation Early -> Scarring Late, Fringe Sign Possible

- Rule: IF Marginal Hair Loss AND History of Hair Tension → Confidence Boost (Traction Alopecia) + Suppress (FFA, AA)

- DDx: Frontal Fibrosing Alopecia, Alopecia Areata (Ophiasis Pattern)

[Condition: Lichen Planopilaris (LPP)]

- Red Flags: Scarring Alopecia (Loss of Follicular Openings), Perifollicular Erythema/Scale, Vertex/Crown Predominance, ± Itch/Tenderness, Biopsy Confirms Interface Dermatitis around Follicle

- Rule: IF Scarring Alopecia AND Perifollicular Inflammation/Scale → Confidence Boost (LPP) + Suppress (DLE, FFA, CCCA)

- DDx: Discoid Lupus Erythematosus (Scalp), Frontal Fibrosing Alopecia, Central Centrifugal Cicatricial Alopecia, Folliculitis Decalvans

[Condition: Frontal Fibrosing Alopecia (FFA)]

- Red Flags: Postmenopausal Women Predominance, Progressive Frontotemporal Hairline Recession, Eyebrow Loss (Partial/Complete), ± Perifollicular Erythema/Scale, Facial Papules Possible

- Rule: IF Hairline Recession AND Eyebrow Loss AND Postmenopausal → Confidence Boost (FFA) + Suppress (Traction Alopecia, AGA)

- DDx: Traction Alopecia, Androgenetic Alopecia, Alopecia Areata

[Condition: Central Centrifugal Cicatricial Alopecia (CCCA)]

- Red Flags: Scarring Alopecia Starting on Vertex/Crown -> Spreading Outwards, Women of African Descent Predominance, Loss of Follicular Openings, ± Hair Breakage/Fragility

- Rule: IF Vertex/Central Scarring Alopecia AND African Descent → Confidence Boost (CCCA) + Suppress (LPP, AGA, Traction)

- DDx: Lichen Planopilaris, Androgenetic Alopecia (Female), Traction Alopecia (Chronic), Folliculitis Decalvans

[Condition: Dissecting Cellulitis of the Scalp]

- Red Flags: Boggy Scalp Swelling, Painful Inflammatory Nodules/Abscesses, Draining Sinus Tracts, Scarring Alopecia, Part of Follicular Occlusion Tetrad

- Rule: IF Boggy Scalp AND Nodules/Abscesses/Sinuses AND Scarring Alopecia → Confidence Boost (Dissecting Cellulitis) + Suppress (Kerion, Folliculitis Decalvans)

- DDx: Tinea Capitis (Kerion), Folliculitis Decalvans, Acne Keloidalis Nuchae (Severe), Bacterial Abscess

[Condition: Folliculitis Decalvans]

- Red Flags: Scarring Alopecia (Expanding Patches), Follicular Pustules/Crusting (Peripheral), Tufted Hairs (Multiple hairs/single opening), Vertex/Crown Common

- Rule: IF Scarring Alopecia AND Pustules AND Tufted Hairs → Confidence Boost (Folliculitis Decalvans) + Suppress (LPP, CCCA, Dissecting Cellulitis)

- DDx: Lichen Planopilaris, Central Centrifugal Cicatricial Alopecia, Dissecting Cellulitis of Scalp, Tinea Capitis (Kerion)

[Condition: Anagen Effluvium]

- Red Flags: Abrupt Diffuse Severe Hair Loss, Occurs Days-Weeks After Trigger (Chemotherapy common), >80% Hair Shed, Dystrophic/Broken Hairs

- Rule: IF Abrupt Severe Hair Loss AND Chemotherapy/Toxin Exposure → Confidence Boost (Anagen Effluvium) + Suppress (TE, Alopecia Totalis)

- DDx: Telogen Effluvium (Severe), Alopecia Totalis

[Condition: Trichotillomania]

- Red Flags: Patchy Hair Loss with Varying Lengths, Broken Hairs, Bizarre Shapes, Accessible Areas (Scalp/Eyebrows/Lashes), Patient May Deny Pulling

- Rule: IF Patchy Loss AND Hairs of Different Lengths/Broken Hairs → Confidence Boost (Trichotillomania) + Suppress (AA, Tinea Capitis)

- DDx: Alopecia Areata, Tinea Capitis, Traction Alopecia

[Condition: Secondary Syphilis (Alopecia)]

- Red Flags: Patchy 'Moth-Eaten' Non-Scarring Alopecia, Occurs with Other Signs of Secondary Syphilis (Rash esp Palms/Soles, Condyloma Lata), Positive Syphilis Serology

- Rule: IF 'Moth-Eaten' Alopecia AND Other Secondary Syphilis Signs → Confidence Boost (Syphilitic Alopecia) + Suppress (AA, Trichotillomania)

- DDx: Alopecia Areata, Trichotillomania, Telogen Effluvium



9. Herpes HPV and other STDs Photos

[Condition: Genital Herpes (HSV)]

- Red Flags: Grouped Vesicles on Erythematous Base (Genital/Anal), Progress to Painful Erosions/Ulcers, Tingling/Pain Prodrome, Recurrent Episodes

- Rule: IF Grouped Genital Vesicles/Ulcers AND Recurrent → Confidence Boost (Genital Herpes) + Suppress (Chancroid, Aphthous Ulcers)

- DDx: Chancroid, Syphilis (Chancre), Aphthous Ulcers (Genital), Behcet Disease, FDE

[Condition: Genital Warts (Condyloma Acuminatum)]

- Red Flags: Soft Fleshy Papules/Plaques (Cauliflower-like), Anogenital Region, HPV Cause (Types 6/11 common), Sexually Transmitted

- Rule: IF Fleshy Anogenital Papules/Plaques → Confidence Boost (Genital Warts) + Suppress (Condyloma Lata, Molluscum, Pearly Penile Papules)

- DDx: Condyloma Lata (Syphilis), Molluscum Contagiosum, Pearly Penile Papules, Seborrheic Keratosis

[Condition: Syphilis (Primary Chancre)]

- Red Flags: Painless Indurated Ulcer (Genital/Oral/Anal), Clean Base, Raised Border, Painless Regional Lymphadenopathy, Treponema pallidum Cause

- Rule: IF Painless Indurated Ulcer → Confidence Boost (Primary Syphilis) + Suppress (Genital Herpes, Chancroid)

- DDx: Genital Herpes, Chancroid, Granuloma Inguinale, Trauma

[Condition: Syphilis (Secondary)]

- Red Flags: Widespread Non-Itchy Rash (Macular/Papular/Papulosquamous), Palm/Sole Involvement Classic, Condyloma Lata (Moist Plaques in Folds), Patchy Alopecia, Generalized Lymphadenopathy, Positive Serology

- Rule: IF Polymorphous Rash AND Palm/Sole Involvement AND Positive Serology → Confidence Boost (Secondary Syphilis) + Suppress (Drug Eruption, Pityriasis Rosea, Viral Exanthem)

- DDx: Drug Eruption, Pityriasis Rosea, Viral Exanthem, Guttate Psoriasis, Lichen Planus

[Condition: Chancroid]

- Red Flags: Painful Soft Genital Ulcer(s), Ragged Undermined Edges, Purulent Base, Tender Suppurative Inguinal Lymphadenopathy (Bubo), Haemophilus ducreyi Cause

- Rule: IF Painful Genital Ulcer(s) AND Tender Bubo → Confidence Boost (Chancroid) + Suppress (Genital Herpes, Syphilis)

- DDx: Genital Herpes, Syphilis (Chancre), Lymphogranuloma Venereum

[Condition: Granuloma Inguinale (Donovanosis)]

- Red Flags: Painless Progressive Ulcers (Genital/Inguinal), Beefy-Red Friable Base, No Lymphadenopathy Typically, Klebsiella granulomatis Cause (Donovan Bodies on Biopsy)

- Rule: IF Painless Beefy-Red Ulcer AND No Adenopathy AND Donovan Bodies → Confidence Boost (Donovanosis) + Suppress (Syphilis, Chancroid, SCC)

- DDx: Syphilis (Chancre/Gumma), Chancroid, Squamous Cell Carcinoma, Amebiasis Cutis

[Condition: Lymphogranuloma Venereum (LGV)]

- Red Flags: Transient Genital Papule/Ulcer (Often Missed), Followed by Tender Inguinal/Femoral Lymphadenopathy ('Groove Sign'), ± Proctocolitis, Caused by C. trachomatis L1-L3

- Rule: IF Tender Inguinal Adenopathy ('Groove Sign') ± Ulcer/Proctitis → Confidence Boost (LGV) + Suppress (Chancroid Bubo, Hernia, Bacterial Lymphadenitis)

- DDx: Chancroid (Bubo), Inguinal Hernia, Bacterial Lymphadenitis, Syphilis, Herpes Simplex (with adenopathy)

[Condition: Pubic Lice (Pediculosis Pubis)]

- Red Flags: Itching in Pubic Area, Visible Lice (Crab-like) at Hair Base, Nits on Hair Shafts, ± Maculae Ceruleae

- Rule: IF Pubic Itch AND Visible Lice/Nits → Confidence Boost (Pubic Lice) + Suppress (Scabies, Folliculitis, Eczema)

- DDx: Scabies, Folliculitis, Eczema, Tinea Cruris

[Condition: Scabies (Genital)]

- Red Flags: Intense Itch (esp. Night), Papules/Nodules on Penis/Scrotum/Vulva, Burrows Elsewhere (Finger Webs/Wrists), Mite on Scraping

- Rule: IF Genital Papules/Nodules AND Intense Itch AND Burrows Elsewhere → Confidence Boost (Scabies) + Suppress (Pubic Lice, Folliculitis)

- DDx: Pubic Lice, Folliculitis, Eczema, Insect Bites

[Condition: Molluscum Contagiosum (Genital)]

- Red Flags: Firm Dome-Shaped Papules (2-5mm), Central Umbilication, Pearly/Flesh-Colored, Genital/Lower Abdomen/Thighs (Adults - STD), Poxvirus Cause

- Rule: IF Umbilicated Papules AND Typical Distribution (STD context) → Confidence Boost (Molluscum) + Suppress (Genital Warts, Folliculitis)

- DDx: Genital Warts, Folliculitis, Herpes Simplex (Atypical)

[Condition: Condyloma Lata]

- Red Flags: Moist Flat-Topped Papules/Plaques, Greyish-White, Intertriginous Areas (Anogenital/Axillae), Occurs with other Secondary Syphilis Signs, Positive Syphilis Serology

- Rule: IF Moist Flat Anogenital Plaques AND Secondary Syphilis Signs/Serology → Confidence Boost (Condyloma Lata) + Suppress (Genital Warts [HPV])

- DDx: Genital Warts (Condyloma Acuminata), Pemphigus Vegetans, Granuloma Inguinale



10. Light Diseases and Disorders of Pigmentation

[Condition: Melasma]

- Red Flags: Symmetric Blotchy Hyperpigmentation, Face (Cheeks/Forehead/Upper Lip), Triggered/Worsened by Sun/Hormones (Pregnancy/OCPs), Female Predominance

- Rule: IF Symmetric Facial Hyperpigmentation AND Sun/Hormone Trigger → Confidence Boost (Melasma) + Suppress (PIH, Solar Lentigines)

- DDx: Post-Inflammatory Hyperpigmentation, Solar Lentigines, Lichen Planus Pigmentosus, Drug-Induced Pigmentation

[Condition: Vitiligo]

- Red Flags: Well-Demarcated Depigmented (Chalk-White) Patches, Symmetric Distribution Common (Acral/Periorificial), Leukotrichia (White Hair in Patches), Autoimmune Association, Wood's Lamp Accentuation

- Rule: IF Chalk-White Patches AND Well-Demarcated → Confidence Boost (Vitiligo) + Suppress (Pityriasis Alba, Tinea Versicolor, PI Hypopigmentation)

- DDx: Pityriasis Alba, Tinea Versicolor, Post-Inflammatory Hypopigmentation, Nevus Depigmentosus, Piebaldism

[Condition: Post-Inflammatory Hyperpigmentation (PIH)]

- Red Flags: Hyperpigmentation (Tan/Brown/Grey), Confined to Site of Prior Inflammation/Injury (Acne/Eczema/Trauma), Follows Pattern of Prior Lesion, More Common/Persistent in Darker Skin

- Rule: IF Hyperpigmentation AND Matches Site of Prior Inflammation → Confidence Boost (PIH) + Suppress (Melasma, Lentigo)

- DDx: Melasma, Solar Lentigo, Ashy Dermatosis, Lichen Planus Pigmentosus, FDE (Resolved)

[Condition: Solar Lentigo ('Age Spot')]

- Red Flags: Well-Demarcated Pigmented Macule/Patch, Light to Dark Brown, Sun-Exposed Areas (Face/Hands/Shoulders), Older Adults, History of Sun Exposure

- Rule: IF Pigmented Macule AND Sun-Exposed Site AND Older Adult → Confidence Boost (Solar Lentigo) + Suppress (LM, SK, Freckle)

- DDx: Lentigo Maligna, Seborrheic Keratosis (Flat), Ephelis (Freckle), Junctional Nevus

[Condition: Ephelides (Freckles)]

- Red Flags: Small Light Brown Macules (<3mm), Appear After Sun Exposure, Fade Without Sun, Fair-Skinned Individuals, Face/Arms/Upper Trunk

- Rule: IF Small Light Brown Macules AND Sun-Induced AND Fade → Confidence Boost (Ephelides) + Suppress (Solar Lentigo, Simple Lentigo)

- DDx: Solar Lentigo, Lentigo Simplex, CALM (Small)

[Condition: Polymorphic Light Eruption (PMLE)]

- Red Flags: Itchy Rash Hours-Days After Sun Exposure (esp. Spring/Early Summer), Various Morphologies (Papules/Vesicles/Plaques), Sun-Exposed Areas (Spares Face Often), Recurrent Pattern Each Year

- Rule: IF Itchy Rash AND Sun-Exposed Site AND Delayed Onset Post Sun → Confidence Boost (PMLE) + Suppress (Sunburn, Lupus [Cutaneous], Contact Derm [Photo])

- DDx: Sunburn, Lupus Erythematosus (SCLE/ACLE), Photoallergic/Phototoxic Reaction, Solar Urticaria (immediate)

[Condition: Chronic Actinic Dermatitis (CAD)]

- Red Flags: Severe Persistent Eczema, Sun-Exposed Areas Predominant (May Spread), Lichenified/Thickened Skin, Extreme Photosensitivity (UVA/UVB/Visible), Older Men Predominance

- Rule: IF Severe Chronic Eczema AND Sun-Exposed Distribution AND Marked Photosensitivity → Confidence Boost (CAD) + Suppress (Atopic Derm, Contact Derm [Photoallergic])

- DDx: Atopic Dermatitis (Severe Photosensitive), Photoallergic Contact Dermatitis, Airborne Contact Dermatitis, Cutaneous T-Cell Lymphoma (MF)

[Condition: Porphyria Cutanea Tarda (PCT)]

- Red Flags: Skin Fragility/Blistering/Erosions on Sun-Exposed Hands, Milia Formation, Facial Hypertrichosis/Hyperpigmentation, Trigger Factors (Alcohol/Estrogen/Hep C/Iron), Elevated Urine/Plasma Porphyrins

- Rule: IF Hand Blisters/Fragility AND Hypertrichosis AND Elevated Porphyrins → Confidence Boost (PCT) + Suppress (Pseudoporphyria, EBA)

- DDx: Pseudoporphyria (Drug-Induced), Epidermolysis Bullosa Acquisita, Bullous Pemphigoid

[Condition: Drug-Induced Photosensitivity]

- Red Flags: Rash Limited to Sun-Exposed Areas, Temporal Relation to New Photosensitizing Drug, Exaggerated Sunburn (Phototoxic) OR Eczematous (Photoallergic)

- Rule: IF Sun-Exposed Rash AND Photosensitizing Drug History → Confidence Boost (Drug Photosensitivity) + Suppress (PMLE, Lupus)

- DDx: Polymorphic Light Eruption, Lupus Erythematosus, Phytophotodermatitis, Contact Dermatitis (Photoallergic)

[Condition: Phytophotodermatitis]

- Red Flags: Erythema/Blistering After Sun Exposure, Bizarre/Linear Shapes (Reflecting Plant Contact), Followed by Marked Hyperpigmentation, History of Contact with Causative Plant (Limes/Parsnip/Celery etc)

- Rule: IF Blistering/Hyperpigmentation AND Bizarre Shapes AND Plant Contact + Sun History → Confidence Boost (Phytophotodermatitis) + Suppress (ACD [Plant], Drug Photosensitivity)

- DDx: Allergic Contact Dermatitis (Plant), Drug-Induced Photosensitivity, Thermal Burn

[Condition: Idiopathic Guttate Hypomelanosis (IGH)]

- Red Flags: Small White Macules (2-5mm, 'Confetti'), Well-Defined, Sun-Exposed Limbs (Shins/Forearms), Older Adults, Asymptomatic

- Rule: IF Small White Macules AND Sun-Exposed Limbs AND Older Adult → Confidence Boost (IGH) + Suppress (Vitiligo, Pityriasis Alba)

- DDx: Vitiligo (Guttate), Pityriasis Alba, Post-Inflammatory Hypopigmentation, Tinea Versicolor

[Condition: Pityriasis Versicolor (Tinea Versicolor)]

- Red Flags: Multiple Oval Macules/Patches, Fine Scale (Visible on Scraping), Upper Trunk/Neck/Arms, Hypo- or Hyperpigmented or Pink, KOH Positive ('Spaghetti & Meatballs')

- Rule: IF Scaly Macules AND Typical Distribution AND Positive KOH → Confidence Boost (Pityriasis Versicolor) + Suppress (Vitiligo, Pityriasis Alba, Seborrhoeic Derm)

- DDx: Vitiligo, Pityriasis Alba, Seborrhoeic Dermatitis, Secondary Syphilis, PIH/PI Hypopigmentation

[Condition: Oculocutaneous Albinism (OCA)]

- Red Flags: Congenital Lack of Pigment (Skin/Hair/Eyes), Photophobia, Nystagmus, Reduced Visual Acuity, Increased Skin Cancer Risk

- Rule: IF Congenital Hypopigmentation AND Ocular Signs (Nystagmus/Reduced Acuity) → Confidence Boost (OCA) + Suppress (Vitiligo [Congenital])

- DDx: Vitiligo (Universal), Piebaldism, Chediak-Higashi Syndrome

[Condition: Piebaldism]

- Red Flags: Congenital White Patch (Often Central Forehead/White Forelock), Stable Depigmentation, Ventral Trunk/Limbs Affected Symmetrically, Islands of Normal/Hyperpigmentation within White Patches, Autosomal Dominant (KIT gene)

- Rule: IF Congenital White Forelock/Patch AND Stable Ventral Distribution → Confidence Boost (Piebaldism) + Suppress (Vitiligo)

- DDx: Vitiligo (Segmental/Focal)

[Condition: Ashy Dermatosis (Erythema Dyschromicum Perstans)]

- Red Flags: Asymptomatic Slate-Grey/Blue-Brown Macules/Patches, Trunk/Neck/Upper Arms Predominant, ± Thin Erythematous Border Initially, Darker Skin Types Common

- Rule: IF Asymptomatic Grey/Blue Macules AND Typical Distribution → Confidence Boost (Ashy Dermatosis) + Suppress (PIH, LPPigm, FDE)

- DDx: Post-Inflammatory Hyperpigmentation, Lichen Planus Pigmentosus, Fixed Drug Eruption (Resolved), Pityriasis Versicolor (Hyperpigmented)



11. Lupus and other Connective Tissue diseases

[Condition: Systemic Lupus Erythematosus (SLE)]

- Red Flags: Multi-System Involvement (Joints/Kidney/CNS etc), Malar Rash, Photosensitivity, Discoid Lesions, Oral Ulcers, Positive ANA/dsDNA/Sm Antibodies

- Rule: IF Malar Rash AND Systemic Symptoms AND Positive ANA/dsDNA/Sm → Confidence Boost (SLE) + Suppress (Rosacea, Dermatomyositis)

- DDx: Rosacea, Dermatomyositis, Subacute Cutaneous Lupus, Drug-Induced Lupus, Mixed Connective Tissue Disease

[Condition: Acute Cutaneous Lupus Erythematosus (ACLE)]

- Red Flags: Malar ('Butterfly') Rash, Photosensitive Maculopapular Rash, Non-Scarring, Associated with SLE Activity, Positive ANA/dsDNA

- Rule: IF Malar Rash AND Photosensitivity AND Non-Scarring → Confidence Boost (ACLE) + Suppress (Rosacea, Seborrhoeic Derm)

- DDx: Rosacea, Seborrhoeic Dermatitis, Polymorphic Light Eruption, Dermatomyositis

[Condition: Subacute Cutaneous Lupus Erythematosus (SCLE)]

- Red Flags: Annular or Papulosquamous Plaques, Photosensitive Distribution (Upper Trunk/Arms, Spares Face often), Non-Scarring, Anti-Ro/SSA Positive Common, Can be Drug-Induced

- Rule: IF Annular/Papulosquamous Plaques AND Photosensitive AND Non-Scarring AND Anti-Ro Positive → Confidence Boost (SCLE) + Suppress (Psoriasis, Tinea Corporis, PMLE)

- DDx: Psoriasis, Tinea Corporis, Polymorphic Light Eruption, Granuloma Annulare, Erythema Annulare Centrifugum

[Condition: Discoid Lupus Erythematosus (DLE)]

- Red Flags: Well-Demarcated Indurated Plaques, Adherent Scale, Follicular Plugging, Central Atrophy/Scarring, Pigment Changes, Sun-Exposed Areas (Face/Scalp/Ears)

- Rule: IF Indurated Plaque AND Atrophy/Scarring AND Follicular Plugging → Confidence Boost (DLE) + Suppress (Psoriasis, Sarcoidosis, Lichen Planus)

- DDx: Psoriasis, Sarcoidosis, Lichen Planus, Keratoacanthoma, SCC

[Condition: Dermatomyositis (DM)]

- Red Flags: Heliotrope Rash (Eyelids), Gottron's Papules (Knuckles/Joints), Photosensitive Rash ('Shawl Sign'), Periungual Telangiectasias/Cuticular Dystrophy, Proximal Muscle Weakness, ± Malignancy Association (Adults)

- Rule: IF Heliotrope Rash AND Gottron's Papules ± Muscle Weakness → Confidence Boost (Dermatomyositis) + Suppress (SLE, Contact Derm [Eyelid])

- DDx: Systemic Lupus Erythematosus, Allergic Contact Dermatitis (Eyelid), Polymorphic Light Eruption, Psoriasis (Inverse/Scalp)

[Condition: Systemic Sclerosis (SSc) / Scleroderma]

- Red Flags: Skin Thickening/Hardening (Sclerodactyly), Raynaud's Phenomenon, Telangiectasias, Calcinosis Cutis, Nailfold Capillary Abnormalities, ± Internal Organ Fibrosis (Lung/GI/Kidney)

- Rule: IF Sclerodactyly AND Raynaud's AND Nailfold Changes → Confidence Boost (SSc) + Suppress (Morphoea, Eosinophilic Fasciitis)

- DDx: Morphoea, Eosinophilic Fasciitis, Nephrogenic Systemic Fibrosis, Scleredema, Chronic GVHD

[Condition: Localized Scleroderma (Morphoea)]

- Red Flags: Indurated Plaque(s) of Skin Sclerosis, Violaceous Border (Active) -> Ivory Center, Progresses to Atrophy/Hyperpigmentation, NO Raynaud's/Sclerodactyly/Systemic Fibrosis

- Rule: IF Indurated Plaque(s) AND Absence of Systemic Sclerosis Features → Confidence Boost (Morphoea) + Suppress (SSc, Lichen Sclerosus)

- DDx: Systemic Sclerosis, Lichen Sclerosus, Scar, Post-Inflammatory Hyperpigmentation with atrophy

[Condition: Mixed Connective Tissue Disease (MCTD)]

- Red Flags: Overlapping Features (SLE/SSc/Polymyositis), Raynaud's Phenomenon, Swollen Hands/Puffy Fingers, Arthralgia/Myositis, High Titer Anti-U1-RNP Antibodies

- Rule: IF Overlap Features AND Raynaud's AND Puffy Fingers AND High Anti-RNP → Confidence Boost (MCTD) + Suppress (SLE, SSc, Undifferentiated CTD)

- DDx: Systemic Lupus Erythematosus, Systemic Sclerosis, Undifferentiated Connective Tissue Disease

[Condition: Sjögren Syndrome]

- Red Flags: Dry Eyes (Keratoconjunctivitis Sicca), Dry Mouth (Xerostomia), ± Xerosis (Dry Skin), ± Annular Erythema, ± Vasculitis, Anti-Ro/SSA, Anti-La/SSB Positive Common

- Rule: IF Sicca Symptoms AND (Positive Lip Biopsy OR Positive Ro/La Antibodies) → Confidence Boost (Sjögren's) + Suppress (Age-Related Dryness, Medication Side Effects)

- DDx: Age-Related Dryness, Medication Side Effects, Sarcoidosis, Primary Biliary Cholangitis

[Condition: Ehlers-Danlos Syndrome (EDS)]

- Red Flags: Joint Hypermobility, Skin Hyperextensibility, Abnormal Scarring ('Cigarette Paper'), Easy Bruising, Tissue Fragility (Hernias/Prolapse/Vascular Issues in some types)

- Rule: IF Joint Hypermobility AND Skin Hyperextensibility AND Abnormal Scarring → Confidence Boost (EDS) + Suppress (Marfan, Cutis Laxa)

- DDx: Benign Joint Hypermobility Syndrome, Marfan Syndrome, Cutis Laxa, Osteogenesis Imperfecta

[Condition: Pseudoxanthoma Elasticum (PXE)]

- Red Flags: Yellowish 'Cobblestone' Papules in Flexures (Neck/Axillae/Groin), Angioid Streaks (Retina), Cardiovascular Complications (Hypertension/Bleeding/Claudication), Autosomal Recessive (ABCC6 gene)

- Rule: IF Yellow Flexural Papules AND Angioid Streaks → Confidence Boost (PXE) + Suppress (Cutis Laxa, Solar Elastosis)

- DDx: Cutis Laxa, Solar Elastosis, Darier Disease (Flexural)

[Condition: Cutis Laxa]

- Red Flags: Loose Sagging Inelastic Skin, Premature Aged Appearance, ± Systemic Involvement (Emphysema/Hernias/Diverticula), Inherited or Acquired

- Rule: IF Loose Inelastic Skin AND Lack of Recoil → Confidence Boost (Cutis Laxa) + Suppress (EDS, PXE, Ageing)

- DDx: Ehlers-Danlos Syndrome, Pseudoxanthoma Elasticum, Normal Ageing, Anetoderma

[Condition: Relapsing Polychondritis]

- Red Flags: Recurrent Inflammation of Cartilage (Ears [spares lobe], Nose [saddle deformity], Joints, Airways), ± Skin Lesions (Vasculitis), ± Eye Inflammation

- Rule: IF Recurrent Ear/Nose Cartilage Inflammation → Confidence Boost (Relapsing Polychondritis) + Suppress (Infection [Perichondritis], GPA)

- DDx: Infectious Perichondritis, Granulomatosis with Polyangiitis (GPA), Trauma



12. Melanoma Skin Cancer Nevi and Moles

[Condition: Common Acquired Melanocytic Nevus (Mole)]

- Red Flags: Symmetric Shape, Uniform Color (Tan/Brown), Well-Defined Border, Stable Size/Appearance, Looks Similar to Other Moles (No 'Ugly Duckling')

- Rule: IF Symmetric AND Uniform Color AND Sharp Border AND Stable → Confidence Boost (Benign Nevus) + Suppress (Melanoma, Dysplastic Nevus)

- DDx: Melanoma, Dysplastic Nevus, Seborrheic Keratosis, Lentigo

[Condition: Atypical / Dysplastic Nevus]

- Red Flags: Asymmetry, Border Irregularity, Color Variegation (>1 color), Diameter >6mm, Evolution (Change), Looks Different ('Ugly Duckling')

- Rule: IF 2+ ABCDE Features → Confidence Boost (Atypical Nevus - Biopsy/Monitor) + Suppress (Benign Nevus)

- DDx: Melanoma, Common Nevus, Lentigo Maligna, Seborrheic Keratosis (Irritated)

[Condition: Congenital Melanocytic Nevus (CMN)]

- Red Flags: Present at Birth/Infancy, Variable Size (Small to Giant), May Have Increased Hair Growth, Risk of Melanoma (esp. Giant CMN)

- Rule: IF Pigmented Lesion AND Present Since Birth → Confidence Boost (CMN) + Suppress (Acquired Nevus, CALM)

- DDx: Large Acquired Nevus, Cafe-au-Lait Macule, Becker Nevus (appears later)

[Condition: Spitz Nevus]

- Red Flags: Pink/Red/Pigmented Dome-Shaped Nodule, Rapid Growth Phase Common, Usually Children/Young Adults, Face/Extremities Common, Specific Dermoscopy Patterns (Starburst/Globular)

- Rule: IF Pink/Red Nodule AND Rapid Growth AND Child/Young Adult → Confidence Boost (Spitz Nevus - Excision Recommended) + Suppress (Melanoma, Pyogenic Granuloma)

- DDx: Melanoma (esp. Nodular/Amelanotic), Pyogenic Granuloma, Hemangioma, Common Wart

[Condition: Blue Nevus]

- Red Flags: Uniformly Blue/Grey/Black Papule/Nodule, Well-Defined, Stable Appearance, Usually <1cm (Common type)

- Rule: IF Uniform Blue/Black Color AND Stable → Confidence Boost (Blue Nevus) + Suppress (Melanoma [Nodular/Metastatic], Tattoo)

- DDx: Nodular Melanoma, Metastatic Melanoma, Tattoo Granuloma, Pigmented BCC

[Condition: Halo Nevus (Sutton Nevus)]

- Red Flags: Central Pigmented Nevus, Surrounded by Symmetric Depigmented Halo, Usually Children/Adolescents, Central Nevus May Regress

- Rule: IF Central Nevus AND Symmetric White Halo → Confidence Boost (Halo Nevus) + Suppress (Melanoma with Halo [Rare])

- DDx: Melanoma with Regression/Halo Phenomenon (Halo often irregular), Vitiligo around Nevus

[Condition: Melanoma (General - Applying ABCDE)]

- Red Flags: Asymmetry, Border Irregularity, Color Variegation, Diameter >6mm, Evolution (Change in Size/Shape/Color/Symptoms)

- Rule: IF 2+ ABCDE Flags OR Evolution OR Ugly Duckling Sign → Confidence Boost (Melanoma - Biopsy Required) + Suppress (Benign Nevus, SK, Lentigo)

- DDx: Dysplastic Nevus, Benign Nevus, Seborrheic Keratosis, Pigmented BCC, Solar Lentigo, Dermatofibroma

[Condition: Superficial Spreading Melanoma (SSM)]

- Red Flags: Flat or Slightly Raised Plaque, Asymmetric, Irregular Borders, Color Variation, Radial Growth Phase Precedes Vertical

- Rule: IF Asymmetric Plaque AND Irregular Border/Color → Confidence Boost (SSM) + Suppress (Large Nevus, Lentigo Maligna)

- DDx: Large Dysplastic Nevus, Lentigo Maligna, Pigmented BCC, Seborrheic Keratosis (Flat)

[Condition: Nodular Melanoma (NM)]

- Red Flags: Rapidly Growing Nodule/Papule, Darkly Pigmented (or Amelanotic Pink/Red), Often Symmetric/Uniform Color Initially, Ulceration/Bleeding Common, Early Vertical Growth

- Rule: IF Rapidly Growing Nodule → Confidence Boost (NM - Urgent Biopsy) + Suppress (Pyogenic Granuloma, Hemangioma, Spitz Nevus)

- DDx: Pyogenic Granuloma, Hemangioma, Spitz Nevus, Pigmented BCC, Metastatic Melanoma

[Condition: Lentigo Maligna (LM) / Lentigo Maligna Melanoma (LMM)]

- Red Flags: Large Irregular Pigmented Macule/Patch, Sun-Damaged Skin (Face/Neck Elderly), Slow Enlargement, Color Variation, Asymmetric Follicular Openings (Dermoscopy). Nodule/Thickening suggests LMM (Invasion).

- Rule: IF Large Irregular Pigmented Patch AND Sun-Damaged Face/Neck Elderly → Confidence Boost (LM/LMM) + Suppress (Solar Lentigo, Pigmented AK)

- DDx: Solar Lentigo (Large/Irregular), Pigmented Actinic Keratosis, Lichen Planus Pigmentosus

[Condition: Acral Lentiginous Melanoma (ALM)]

- Red Flags: Palm/Sole/Nail Location, Irregular Pigmented Patch (Palm/Sole), Parallel Ridge Pattern (Dermoscopy - Sole), Longitudinal Melanonychia (>3mm, Variable Color/Width, Hutchinson Sign, Nail Dystrophy)

- Rule: IF Acral Location AND Irregular Pigment OR Suspicious Nail Band → Confidence Boost (ALM - Biopsy) + Suppress (Benign Acral Nevus, Subungual Hematoma)

- DDx: Benign Acral Nevus, Junctional Nevus, Subungual Hematoma, Fungal Melanonychia, Tinea Nigra

[Condition: Amelanotic Melanoma]

- Red Flags: Pink/Red Papule/Nodule, Recent Growth/Change, May Ulcerate/Bleed, Lack of Pigment Makes Diagnosis Difficult, Atypical Vessels (Dermoscopy)

- Rule: IF Pink/Red Growing Nodule → Confidence Boost (Amelanotic Melanoma - Consider Biopsy) + Suppress (Pyogenic Granuloma, BCC, SCC, Spitz)

- DDx: Pyogenic Granuloma, Basal Cell Carcinoma, Squamous Cell Carcinoma, Spitz Nevus, Hemangioma

[Condition: Subungual Melanoma]

- Red Flags: Longitudinal Melanonychia (Irregular/Wide/>3mm/Variable Color), Hutchinson's Sign (Pigment onto Fold), Nail Plate Destruction/Bleeding, History of Trauma Often Misleading

- Rule: IF Suspicious Longitudinal Melanonychia OR Nail Destruction without Clear Benign Cause → Confidence Boost (Subungual Melanoma - Biopsy) + Suppress (Subungual Hematoma, Benign Melanonychia, Fungal Infection)

- DDx: Subungual Hematoma, Benign Longitudinal Melanonychia, Fungal Melanonychia, Subungual Wart/SCC

[Condition: Metastatic Melanoma (Cutaneous)]

- Red Flags: Firm Papule(s)/Nodule(s), May be Pigmented or Amelanotic, Often Near Prior Melanoma Scar (In-transit) or Distant Site, History of Prior Melanoma

- Rule: IF New Firm Papule/Nodule AND History of Melanoma → Confidence Boost (Metastatic Melanoma - Biopsy) + Suppress (BCC, SCC, Neurofibroma, Cyst)

- DDx: Basal Cell Carcinoma, Squamous Cell Carcinoma, Neurofibroma, Epidermoid Cyst, Blue Nevus



13. Nail Fungus and other Nail Disease

[Condition: Onychomycosis (Tinea Unguium)]

- Red Flags: Nail Thickening, Discoloration (Yellow/White/Brown), Subungual Debris/Hyperkeratosis, Onycholysis, Positive Fungal Test (KOH/Culture/PAS)

- Rule: IF Nail Thickening/Discoloration/Debris AND Positive Mycology → Confidence Boost (Onychomycosis) + Suppress (Psoriasis, Trauma, Lichen Planus)

- DDx: Nail Psoriasis, Traumatic Onychodystrophy, Lichen Planus of Nails, Eczema (Nail Changes)

[Condition: Paronychia (Acute)]

- Red Flags: Rapid Onset Pain/Redness/Swelling of Nail Fold, Pus Collection (Abscess) Possible, History of Minor Trauma/Hangnail

- Rule: IF Acute Nail Fold Inflammation AND Pain ± Pus → Confidence Boost (Acute Paronychia) + Suppress (Herpetic Whitlow, Chronic Paronychia)

- DDx: Herpetic Whitlow, Chronic Paronychia, Psoriasis (Pustular)

[Condition: Paronychia (Chronic)]

- Red Flags: Persistent (>6wk) Nail Fold Inflammation (Swollen/Erythematous/Tender), Loss of Cuticle, ± Nail Plate Irregularity, Wet Work/Irritant Exposure History, Candida Often Involved

- Rule: IF Chronic Nail Fold Swelling AND Cuticle Loss AND Wet Work History → Confidence Boost (Chronic Paronychia) + Suppress (Psoriasis, Eczema)

- DDx: Nail Psoriasis, Eczema (Periungual), Lichen Planus

[Condition: Nail Psoriasis]

- Red Flags: Nail Pitting (Irregular), Onycholysis (± Red Border), Subungual Hyperkeratosis, Oil Drop/Salmon Patch Discoloration, Personal/Family History of Psoriasis (Skin/Joints)

- Rule: IF Pitting AND Onycholysis/Oil Drop AND Psoriasis History → Confidence Boost (Nail Psoriasis) + Suppress (Onychomycosis, Trauma)

- DDx: Onychomycosis, Traumatic Onychodystrophy, Lichen Planus of Nails, Alopecia Areata (Pitting)

[Condition: Lichen Planus (Nail Involvement)]

- Red Flags: Nail Thinning, Longitudinal Ridging/Fissuring, Distal Splitting, Pterygium Unguis (Proximal Nail Fold Scarring to Bed), Potential Nail Loss, ± Skin/Oral LP

- Rule: IF Longitudinal Ridging/Splitting AND Pterygium → Confidence Boost (Nail LP) + Suppress (Psoriasis, Trauma, Ageing)

- DDx: Nail Psoriasis, Traumatic Onychodystrophy, Age-Related Nail Changes, Twenty-Nail Dystrophy

[Condition: Ingrown Toenail (Onychocryptosis)]

- Red Flags: Pain/Redness/Swelling of Lateral Nail Fold (Great Toe Common), Nail Edge Embedded in Skin, ± Granulation Tissue/Discharge

- Rule: IF Lateral Fold Pain/Inflammation AND Nail Embedding → Confidence Boost (Ingrown Toenail) + Suppress (Paronychia)

- DDx: Paronychia, Subungual Exostosis, Glomus Tumor

[Condition: Subungual Hematoma]

- Red Flags: Purple/Black Discoloration Under Nail, History of Acute Trauma, Grows Out with Nail, Dermoscopy (Homogenous Globules/Color, No Lines)

- Rule: IF Subungual Discoloration AND Trauma History AND Grows Out → Confidence Boost (Subungual Hematoma) + Suppress (Subungual Melanoma)

- DDx: Subungual Melanoma, Fungal Melanonychia, Splinter Hemorrhage (Large)

[Condition: Beau's Lines]

- Red Flags: Transverse Groove(s) Across Nail Plate(s), Affects Multiple Nails Simultaneously, Moves Distally with Growth, History of Systemic Illness/Stress ~3mo Prior

- Rule: IF Transverse Nail Groove(s) AND History of Systemic Event → Confidence Boost (Beau's Lines) + Suppress (Habit Tic, Ridging)

- DDx: Habit Tic Deformity (Central/Washboard), Longitudinal Ridging (Ageing/LP)

[Condition: Onycholysis]

- Red Flags: Separation of Nail Plate from Bed (Appears White/Yellow), Distal or Lateral Onset Usually, Many Causes (Trauma/Psoriasis/Onychomycosis/Drugs/Thyroid)

- Rule: IF Nail Separation from Bed → Investigate Underlying Cause (Onycholysis) + Suppress (Normal Lunula)

- DDx: Cause needs identification (Psoriasis, Onychomycosis, Trauma, Drug etc.)

[Condition: Longitudinal Melanonychia]

- Red Flags: Brown/Black Linear Band in Nail Plate, Common in Darker Skin. Concern if: New/Changing, Wide (>3mm), Irregular Color/Border, Hutchinson Sign, Nail Dystrophy.

- Rule: IF Longitudinal Pigmented Band AND Concerning Features → Confidence Boost (Melanoma Suspicion - Biopsy) + Suppress (Benign Melanonychia, Hematoma)

- DDx: Subungual Melanoma, Benign Ethnic Melanonychia, Nevus (Matrix), Subungual Hematoma (Linear), Fungal Melanonychia

[Condition: Median Canaliform Dystrophy]

- Red Flags: Central Longitudinal Groove/Split in Nail(s), Often Thumbs, ± Transverse Ridges ('Fir Tree'), Possible Habit Tic Association

- Rule: IF Central Longitudinal Groove/Split → Confidence Boost (Median Canaliform Dystrophy) + Suppress (LP, Trauma)

- DDx: Lichen Planus (Nail), Traumatic Nail Dystrophy, Habit Tic Deformity

[Condition: Habit-Tic Deformity]

- Red Flags: Central Longitudinal Groove or Transverse 'Washboard' Ridges, Damaged Cuticle Possible, Usually Thumbs, History of Repetitive Manipulation

- Rule: IF Central Groove/Washboard Ridges AND History of Manipulation → Confidence Boost (Habit Tic) + Suppress (Median Canaliform Dystrophy, Beau's Lines)

- DDx: Median Canaliform Dystrophy, Beau's Lines, Lichen Planus (Nail)



14. Poison Ivy Photos and other Contact Dermatitis

[Condition: Allergic Contact Dermatitis (ACD) - Poison Ivy/Oak/Sumac]

- Red Flags: Intense Itch, Linear Streaks of Papules/Vesicles, Exposed Skin Areas, History of Plant Exposure (Woods/Garden), Delayed Onset (1-3 days)

- Rule: IF Linear Vesicular Rash AND Plant Exposure History → Confidence Boost (Poison Ivy/Oak/Sumac ACD) + Suppress (Insect Bites, Phytophotodermatitis)

- DDx: Insect Bites (Linear), Phytophotodermatitis, Herpes Zoster (Early/Linear)

[Condition: Allergic Contact Dermatitis (ACD) - Nickel]

- Red Flags: Eczematous Rash Localized to Metal Contact Site (Jewelry/Buckle/Button), Itchy, Positive Patch Test to Nickel

- Rule: IF Eczema AND Matches Metal Contact Site → Confidence Boost (Nickel ACD) + Suppress (ICD, Atopic Derm)

- DDx: Irritant Contact Dermatitis, Atopic Dermatitis, Intertrigo (if buckle in fold)

[Condition: Irritant Contact Dermatitis (ICD) - Hand ('Housewife's Eczema')]

- Red Flags: Dryness/Scaling/Fissuring/Erythema of Hands, Burning/Stinging, History of Wet Work/Detergent/Solvent Exposure, Affects Anyone Exposed Sufficiently

- Rule: IF Hand Dermatitis AND Wet Work/Irritant Exposure History → Confidence Boost (Hand ICD) + Suppress (ACD, Atopic Hand Eczema)

- DDx: Allergic Contact Dermatitis (Gloves/Soaps), Atopic Hand Eczema, Dyshidrotic Eczema, Tinea Manuum

[Condition: Phytophotodermatitis]

- Red Flags: Erythema/Blistering After Sun Exposure, Bizarre/Linear Shapes (Plant Contact), Followed by Hyperpigmentation, History of Contact with Furocoumarin Plant (Lime/Parsnip etc) + Sun

- Rule: IF Blistering/Hyperpigmentation AND Bizarre Shapes AND Plant+Sun History → Confidence Boost (Phytophotodermatitis) + Suppress (ACD [Plant], Sunburn)

- DDx: Allergic Contact Dermatitis (Plant), Severe Sunburn, Bullous Insect Bite

[Condition: Hair Dye Allergy (PPD)]

- Red Flags: Severe Itching/Eczema/Edema of Scalp/Face/Neck, Onset 1-3 Days After Hair Dye Use, ± Blistering/Weeping, Positive PPD Patch Test

- Rule: IF Scalp/Face Edema/Eczema AND Recent Hair Dye Use → Confidence Boost (PPD Allergy) + Suppress (Scalp Psoriasis/Seb Derm Flare, Cellulitis)

- DDx: Scalp Psoriasis Flare, Seborrhoeic Dermatitis Flare, Cellulitis (Facial), Angioedema

[Condition: Fragrance Allergy]

- Red Flags: Eczema in Sites of Application (Neck/Wrists) or Transfer (Eyelids/Face), History of Reaction to Perfumes/Cosmetics, Positive Patch Test to Fragrance Mix/Specifics

- Rule: IF Eczema in Typical Sites AND Cosmetic Use → Confidence Boost (Fragrance Allergy) + Suppress (Atopic Derm, ICD)

- DDx: Atopic Dermatitis, Irritant Contact Dermatitis, Photoallergic Reaction

[Condition: Preservative Allergy (e.g., MI/MCI, Formaldehyde Releasers)]

- Red Flags: Eczema Related to Cosmetic/Wipe Use, Face/Hands/Perineal Areas Common, Positive Patch Test to Specific Preservative(s)

- Rule: IF Eczema Pattern Matches Product Use AND Positive Patch Test → Confidence Boost (Preservative Allergy) + Suppress (Atopic Derm, ICD)

- DDx: Atopic Dermatitis, Irritant Contact Dermatitis, Inverse Psoriasis (Perineal)

[Condition: Latex Allergy (Type IV - ACD)]

- Red Flags: Delayed Eczematous Reaction (1-3 days), Dorsum of Hands Common Site, History of Latex Glove Use, Positive Patch Test to Rubber Accelerators

- Rule: IF Hand Eczema (Delayed) AND Latex Glove Use → Confidence Boost (Latex ACD - Type IV) + Suppress (ICD, Latex Urticaria [Type I])

- DDx: Irritant Contact Dermatitis (Gloves), Latex Urticaria (Type I - immediate), Dyshidrotic Eczema

[Condition: Shoe Dermatitis (ACD)]

- Red Flags: Eczema on Dorsum of Feet/Toes, Spares Interdigital Spaces Often, Related to Specific Footwear, Positive Patch Test (Rubber Chemicals/Chromates/Glues/Dyes)

- Rule: IF Foot Eczema (Dorsal) AND Spares Webs → Confidence Boost (Shoe ACD) + Suppress (Tinea Pedis, Atopic Foot Eczema)

- DDx: Tinea Pedis, Atopic Dermatitis (Foot), Dyshidrotic Eczema, Juvenile Plantar Dermatosis

[Condition: Airborne Contact Dermatitis]

- Red Flags: Dermatitis on Exposed Skin (Face/Neck/Arms) BUT also Accentuated in Sheltered Sites (Eyelids/Submental/Retroauricular), History of Exposure to Airborne Irritant/Allergen (Pollen/Dust/Chemicals)

- Rule: IF Exposed Site Dermatitis AND Accentuation in Sheltered Folds → Confidence Boost (Airborne CD) + Suppress (Photodermatitis, Atopic Derm)

- DDx: Photodermatitis (PMLE/CAD/Drug), Atopic Dermatitis (Face/Neck), Seborrhoeic Dermatitis



15. Psoriasis pictures Lichen Planus and related diseases

[Condition: Psoriasis (Chronic Plaque)]

- Red Flags: Well-Demarcated Erythematous Plaques, Thick Silvery Scale, Extensor Surfaces (Elbows/Knees)/Scalp/Sacrum, Nail Pitting/Onycholysis, Auspitz Sign

- Rule: IF Well-Demarcated Plaque AND Silvery Scale AND Extensor/Scalp Location → Confidence Boost (Plaque Psoriasis) + Suppress (Eczema, Tinea, Bowen's)

- DDx: Nummular Eczema, Tinea Corporis, Bowen Disease, Lichen Simplex Chronicus, Cutaneous T-Cell Lymphoma

[Condition: Guttate Psoriasis]

- Red Flags: Abrupt Onset Small 'Drop-Like' Papules/Plaques (<1cm), Scattered Trunk/Proximal Limbs, Fine Scale, Often Follows Strep Infection, Young Patient Common

- Rule: IF Acute Drop-Like Lesions AND Strep History → Confidence Boost (Guttate Psoriasis) + Suppress (Pityriasis Rosea, Drug Eruption, Secondary Syphilis)

- DDx: Pityriasis Rosea, Drug Eruption (Papular), Secondary Syphilis, Folliculitis

[Condition: Inverse (Flexural) Psoriasis]

- Red Flags: Well-Demarcated Bright Red Plaques, Skin Folds (Axillae/Groin/Inframammary/Gluteal Cleft), Minimal/Absent Scale (Due to Moisture), Fissuring Possible

- Rule: IF Bright Red Well-Demarcated Plaques AND Flexural Location → Confidence Boost (Inverse Psoriasis) + Suppress (Candida Intertrigo, Tinea Cruris, Seborrhoeic Derm)

- DDx: Candida Intertrigo, Tinea Cruris, Seborrhoeic Dermatitis, Erythrasma, Hailey-Hailey Disease

[Condition: Pustular Psoriasis (Generalized - von Zumbusch)]

- Red Flags: Acute Onset Widespread Erythema, Sheets of Small Sterile Pustules ('Lakes of Pus'), Fever/Malaise/Leukocytosis, Trigger Possible (Steroid Withdrawal)

- Rule: IF Acute Fever AND Widespread Pustules on Erythema → Confidence Boost (GPP) + Suppress (AGEP, SJS/TEN with pustules, Infection) - URGENT

- DDx: Acute Generalized Exanthematous Pustulosis (AGEP), SJS/TEN, Drug Eruption, Bacterial Sepsis with pustules

[Condition: Palmoplantar Psoriasis (Plaque type)]

- Red Flags: Well-Demarcated Thickened Red Plaques, Scaly, Palms/Soles, Fissuring Common, May Occur with Psoriasis Elsewhere

- Rule: IF Well-Demarcated Scaly Plaques AND Palms/Soles → Confidence Boost (Palmoplantar Psoriasis) + Suppress (Hand/Foot Eczema, Tinea)

- DDx: Hyperkeratotic Hand/Foot Eczema, Tinea Manuum/Pedis, Lichen Planus, Keratoderma

[Condition: Palmoplantar Pustulosis (PPP)]

- Red Flags: Chronic Recurrent Sterile Pustules, Palms/Soles, Evolve to Brown Spots/Scale, Background Erythema Possible, Strong Smoking Association

- Rule: IF Chronic Palm/Sole Pustules AND Smoking History → Confidence Boost (PPP) + Suppress (Dyshidrotic Eczema [Pustular], Tinea [Inflammatory])

- DDx: Dyshidrotic Eczema (Pustular/Infected), Tinea Manuum/Pedis (Inflammatory/Pustular), Acute Palmoplantar Eccrine Hidradenitis

[Condition: Lichen Planus (Cutaneous)]

- Red Flags: Pruritic, Purple, Polygonal, Planar Papules/Plaques (6 P's), Wickham's Striae (Surface White Lines), Flexor Wrists/Ankles/Lumbar Back Common, Koebner Phenomenon

- Rule: IF Purple Polygonal Papules AND Wickham's Striae AND Typical Location → Confidence Boost (Cutaneous LP) + Suppress (Psoriasis, Eczema, Lichenoid Drug Eruption)

- DDx: Psoriasis, Eczema (Nummular/LSC), Lichenoid Drug Eruption, Secondary Syphilis, Graft Versus Host Disease (Chronic)

[Condition: Lichen Planus (Oral - OLP)]

- Red Flags: Reticular White Lines (Wickham's Striae) on Buccal Mucosa, ± Erosions/Ulcers (Painful), ± White Plaques, ± Gingivitis (Desquamative)

- Rule: IF Reticular White Lines (Buccal) OR Erosions with Peripheral Striae → Confidence Boost (OLP) + Suppress (Candidiasis, Leukoplakia, Pemphigus/Pemphigoid)

- DDx: Candidiasis (Thrush/Erythematous), Leukoplakia, Pemphigus Vulgaris, Mucous Membrane Pemphigoid, Aphthous Stomatitis (for erosive OLP)

[Condition: Lichen Planopilaris (LPP)]

- Red Flags: Scarring Alopecia, Perifollicular Erythema/Scale, Vertex/Crown Common, Itch/Tenderness Possible, Loss of Follicular Openings

- Rule: IF Scarring Alopecia AND Perifollicular Inflammation/Scale → Confidence Boost (LPP) + Suppress (DLE, FFA, CCCA) - (Same as Hair Loss Category Rule)

- DDx: Discoid Lupus (Scalp), Frontal Fibrosing Alopecia, CCCA, Folliculitis Decalvans

[Condition: Pityriasis Rubra Pilaris (PRP)]

- Red Flags: Reddish-Orange Plaques/Erythroderma, Follicular Papules ('Nutmeg Grater'), Islands of Spared Skin within Plaques, Thick Orange Palmoplantar Keratoderma ('Sandals')

- Rule: IF Orange Hue AND Follicular Prominence AND Islands of Sparing OR Keratodermic Sandals → Confidence Boost (PRP) + Suppress (Psoriasis, Erythrodermic Eczema)

- DDx: Psoriasis (esp. Erythrodermic), Erythrodermic Eczema/Drug Reaction, Seborrhoeic Dermatitis (Severe), CTCL

[Condition: Pityriasis Rosea]

- Red Flags: Herald Patch (Single Larger Oval Plaque), Followed by Smaller Oval Pink/Tan Patches, Collarette of Scale (Inside Edge), 'Christmas Tree' Pattern on Trunk, Self-Limiting (6-8 weeks)

- Rule: IF Herald Patch AND Oval Lesions in Christmas Tree Pattern → Confidence Boost (Pityriasis Rosea) + Suppress (Guttate Psoriasis, Secondary Syphilis, Drug Eruption)

- DDx: Guttate Psoriasis, Secondary Syphilis, Drug Eruption, Tinea Corporis (Multiple)



16. Scabies Lyme Disease and other Infestations and Bites

[Condition: Scabies]

- Red Flags: Intense Itch (Worse at Night), Burrows (Finger Webs/Wrists), Papules/Vesicles/Nodules (Genitals/Axillae common), Household Contacts Itchy, Mite/Eggs on Scraping/Dermoscopy

- Rule: IF Intense Nocturnal Itch AND Burrows OR Typical Distribution/Contacts Itchy → Confidence Boost (Scabies) + Suppress (Eczema, Insect Bites)

- DDx: Eczema (Atopic/Contact/Dyshidrotic), Insect Bites (Papular Urticaria), Folliculitis, Dermatitis Herpetiformis

[Condition: Lyme Disease (Erythema Migrans)]

- Red Flags: Expanding Annular Red Rash (>5cm), ± Central Clearing ('Bull's-Eye'), History of Tick Bite/Exposure in Endemic Area, Days-Weeks Post Bite

- Rule: IF Expanding Annular Rash >5cm AND Tick Exposure History → Confidence Boost (Erythema Migrans) + Suppress (Tinea Corporis, Granuloma Annulare, Cellulitis) - (Same as Bacterial Category Rule)

- DDx: Tinea Corporis, Granuloma Annulare, Cellulitis, Insect Bite Reaction (Large Local)

[Condition: Pediculosis Capitis (Head Lice)]

- Red Flags: Itchy Scalp (Occiput/Retroauricular), Visible Live Lice on Scalp, Nits (Eggs) Firmly Attached to Hair Shafts near Scalp

- Rule: IF Itchy Scalp AND Visible Lice OR Nits → Confidence Boost (Head Lice) + Suppress (Dandruff, Psoriasis)

- DDx: Seborrhoeic Dermatitis (Dandruff), Scalp Psoriasis, Hair Casts, Book Lice (Environmental)

[Condition: Pediculosis Pubis (Pubic Lice)]

- Red Flags: Itching in Pubic Area/Axillae/Eyelashes, Visible Lice (Crab-like) at Hair Base, Nits on Hairs, ± Maculae Ceruleae

- Rule: IF Pubic Itch AND Visible Lice/Nits → Confidence Boost (Pubic Lice) + Suppress (Scabies, Folliculitis) - (Same as Herpes/STD Category Rule)

- DDx: Scabies, Folliculitis, Eczema

[Condition: Bed Bug Bites (Cimicosis)]

- Red Flags: Itchy Papules/Wheals, Linear Groups ('Breakfast/Lunch/Dinner') or Clusters, Exposed Areas During Sleep, Finding Bugs/Fecal Spots in Environment (Mattress etc)

- Rule: IF Grouped/Linear Itchy Papules AND Nocturnal Onset → Confidence Boost (Bed Bug Bites) + Suppress (Flea Bites, Scabies)

- DDx: Flea Bites, Mosquito Bites, Scabies, Papular Urticaria, Folliculitis

[Condition: Flea Bites]

- Red Flags: Small Itchy Papules (often with Central Punctum), Grouped Lesions, Lower Legs/Ankles Predominant, History of Pet Contact or Infested Environment

- Rule: IF Grouped Itchy Papules AND Lower Leg Predominance AND Pet/Environment History → Confidence Boost (Flea Bites) + Suppress (Bed Bug Bites, Papular Urticaria)

- DDx: Bed Bug Bites, Papular Urticaria, Folliculitis, Scabies

[Condition: Papular Urticaria (Insect Bite Hypersensitivity)]

- Red Flags: Recurrent Crops of Persistent Itchy Papules/Nodules, Often Grouped on Exposed Limbs, Common in Children, History Suggestive of Bites (Fleas/Mosquitoes etc)

- Rule: IF Persistent Itchy Papules AND History Suggests Bites → Confidence Boost (Papular Urticaria) + Suppress (Scabies, Eczema, Lymphoma Cutis)

- DDx: Scabies, Atopic Dermatitis, Prurigo Nodularis, Lymphomatoid Papulosis, Dermatitis Herpetiformis

[Condition: Tick Bites]

- Red Flags: Attached Tick Visible, Localized Erythema/Papule at Bite Site, History of Outdoor Exposure in Endemic Area (Consider Tick-Borne Disease Risk)

- Rule: IF Attached Tick OR History of Removal → Monitor for Rash/Symptoms (Tick Bite) + Suppress (Simple Insect Bite)

- DDx: Other Insect Bite, Folliculitis, Early Erythema Migrans

[Condition: Cutaneous Larva Migrans (Creeping Eruption)]

- Red Flags: Itchy Serpiginous (Snake-like) Elevated Tracks, Slowly Migrating (mm-cm/day), Usually Feet/Buttocks/Hands, History of Exposure to Contaminated Soil/Sand (Beaches/Tropics)

- Rule: IF Serpiginous Migrating Track AND Itchy → Confidence Boost (CLM) + Suppress (Larva Currens, Phytophotodermatitis [Linear])

- DDx: Larva Currens (Strongyloides - faster), Phytophotodermatitis (Linear), Contact Dermatitis (Linear)

[Condition: Tungiasis (Jiggers)]

- Red Flags: Painful Papule/Nodule with Central Black Dot, Feet (Periungual/Soles), History of Travel to Endemic Area (Tropics/Subtropics) / Walking Barefoot

- Rule: IF Painful Foot Lesion AND Central Black Dot AND Travel History → Confidence Boost (Tungiasis) + Suppress (Wart, Foreign Body, Paronychia)

- DDx: Plantar Wart, Foreign Body Reaction, Paronychia, Myiasis (Furuncular)

[Condition: Myiasis (Cutaneous)]

- Red Flags: Boil-like Lesion with Central Pore (Furuncular), ± Movement Sensation/Visible Larva, ± Wound Infestation, History of Travel to Endemic Area (for certain types)

- Rule: IF Furuncular Lesion AND Central Pore AND Travel History (if relevant) → Confidence Boost (Myiasis) + Suppress (Furuncle, Cyst [Inflamed])

- DDx: Furuncle, Epidermoid Cyst (Inflamed), Pyogenic Granuloma, Foreign Body Reaction

[Condition: Leishmaniasis (Cutaneous)]

- Red Flags: Persistent Papule/Nodule/Ulcer ('Volcano Sign'), Exposed Skin, History of Travel/Residence in Endemic Area (Sandfly Vector), Weeks-Months Incubation, Positive Biopsy/PCR

- Rule: IF Chronic Ulcer/Nodule AND Endemic Exposure History → Confidence Boost (Leishmaniasis) + Suppress (SCC, Deep Fungal, TB)

- DDx: Squamous Cell Carcinoma, Deep Fungal Infection (Sporo/Chromo etc), Cutaneous Tuberculosis, Atypical Mycobacteria, Insect Bite (Persistent)



17. Seborrheic Keratoses and other Benign Tumors

[Condition: Seborrheic Keratosis (SK)]

- Red Flags: 'Stuck-On' Appearance, Waxy/Verrucous Surface, Variable Pigmentation (Tan/Brown/Black), Milia-like Cysts / Comedo-like Openings (Dermoscopy), Common in Middle-Aged/Elderly

- Rule: IF 'Stuck-On' AND Waxy/Verrucous AND Dermoscopy Features → Confidence Boost (SK) + Suppress (Melanoma, Pigmented BCC, Wart)

- DDx: Melanoma (Pigmented), Pigmented Basal Cell Carcinoma, Verruca Vulgaris (Wart), Actinic Keratosis (Pigmented), Lentigo Maligna

[Condition: Skin Tag (Acrochordon)]

- Red Flags: Soft Pedunculated (Stalked) Papule, Flesh-Colored or Brownish, Neck/Axillae/Groin/Eyelids Common, Often Multiple

- Rule: IF Soft Pedunculated Papule AND Typical Location → Confidence Boost (Skin Tag) + Suppress (Neurofibroma, Nevus)

- DDx: Neurofibroma, Intradermal Nevus, Pedunculated Seborrheic Keratosis

[Condition: Dermatofibroma]

- Red Flags: Firm Dermal Papule/Nodule, Limbs Common, ± Pigmented Rim, Dimples Inward on Lateral Pressure ('Dimple Sign'), Central White Patch (Dermoscopy)

- Rule: IF Firm Nodule AND Dimple Sign → Confidence Boost (Dermatofibroma) + Suppress (Nevus, Melanoma, BCC)

- DDx: Intradermal Nevus, Melanoma (Nodular/Desmoplastic), Basal Cell Carcinoma, Keloid/Hypertrophic Scar

[Condition: Cherry Angioma]

- Red Flags: Small Bright Red/Violaceous Papule, Dome-Shaped, Multiple Lesions Common, Trunk Predominant, Increases with Age, Red/Purple Lacunae (Dermoscopy)

- Rule: IF Small Bright Red Papule AND Typical Appearance → Confidence Boost (Cherry Angioma) + Suppress (Amelanotic Melanoma, Angiokeratoma)

- DDx: Amelanotic Melanoma (Small), Angiokeratoma, Pyogenic Granuloma (Small), Glomus Tumor

[Condition: Epidermoid Cyst]

- Red Flags: Subcutaneous Nodule, Firm or Fluctuant, ± Central Punctum, Contains Cheesy Keratin Material, Can Become Inflamed

- Rule: IF Subcutaneous Nodule AND ± Punctum AND Expresses Keratin → Confidence Boost (Epidermoid Cyst) + Suppress (Lipoma, Pilar Cyst)

- DDx: Lipoma, Pilar Cyst, Abscess (Inflamed Cyst), Neurofibroma

[Condition: Pilar Cyst (Trichilemmal Cyst)]

- Red Flags: Firm Smooth Mobile Subcutaneous Nodule, Scalp Predominant (>90%), No Punctum Usually, Often Multiple/Familial

- Rule: IF Firm Scalp Nodule AND Mobile AND No Punctum → Confidence Boost (Pilar Cyst) + Suppress (Epidermoid Cyst, Lipoma)

- DDx: Epidermoid Cyst, Lipoma, Metastasis (Scalp)

[Condition: Lipoma]

- Red Flags: Soft Lobulated Mobile Subcutaneous Mass, Doughy Consistency, Overlying Skin Normal, Asymptomatic Usually

- Rule: IF Soft Mobile Subcutaneous Mass → Confidence Boost (Lipoma) + Suppress (Epidermoid Cyst, Angiolipoma)

- DDx: Epidermoid Cyst, Angiolipoma (Tender), Abscess, Neurofibroma

[Condition: Nevus Sebaceus]

- Red Flags: Congenital/Infancy Onset Plaque, Yellowish/Waxy/Hairless Initially, Becomes Verrucous/Nodular at Puberty, Scalp/Face Common

- Rule: IF Congenital Yellowish Hairless Plaque → Confidence Boost (Nevus Sebaceus) + Suppress (Epidermal Nevus, Juvenile Xanthogranuloma)

- DDx: Epidermal Nevus, Juvenile Xanthogranuloma, Solitary Mastocytoma

[Condition: Neurofibroma (Solitary)]

- Red Flags: Soft Skin-Colored/Pinkish Papule/Nodule, Compressible ('Button-Hole' Sign), ± Pedunculated

- Rule: IF Soft Compressible Papule/Nodule → Confidence Boost (Neurofibroma) + Suppress (Intradermal Nevus, Skin Tag)

- DDx: Intradermal Nevus, Skin Tag, Dermatofibroma

[Condition: Syringoma]

- Red Flags: Multiple Small (1-3mm) Firm Papules, Skin-Colored/Yellowish, Periocular Predominance (Lower Lids), Female Predominance

- Rule: IF Multiple Small Periocular Papules → Confidence Boost (Syringoma) + Suppress (Trichoepithelioma, Milia, Xanthelasma)

- DDx: Trichoepithelioma, Milia, Xanthelasma, Microcystic Adnexal Carcinoma

[Condition: Pyogenic Granuloma]

- Red Flags: Rapidly Growing Red/Violaceous Papule/Nodule, Bleeds Easily, Often Crusted/Ulcerated, ± Collarette of Scale, Fingers/Lips/Gums Common

- Rule: IF Rapidly Growing Friable Red Nodule → Confidence Boost (Pyogenic Granuloma) + Suppress (Amelanotic Melanoma, SCC, Hemangioma)

- DDx: Amelanotic Melanoma, Squamous Cell Carcinoma, Hemangioma, Spitz Nevus, Glomus Tumor

[Condition: Sebaceous Hyperplasia]

- Red Flags: Yellowish Papule(s), Central Umbilication, Face Common (Forehead/Cheeks), Middle-Aged/Elderly, ± Fine Telangiectasias (around edge)

- Rule: IF Yellowish Papule AND Central Umbilication AND Face → Confidence Boost (Sebaceous Hyperplasia) + Suppress (BCC, Milia)

- DDx: Basal Cell Carcinoma (Nodular), Milia, Molluscum Contagiosum, Intradermal Nevus



18. Systemic Disease

[Condition: Diabetic Dermopathy ('Shin Spots')]

- Red Flags: History of Diabetes, Asymptomatic Brownish Atrophic Macules/Patches, Bilateral Anterior Lower Legs (Shins), Often Multiple

- Rule: IF Diabetes History AND Atrophic Shin Spots → Confidence Boost (Diabetic Dermopathy) + Suppress (PIH, Stasis Changes)

- DDx: Post-Inflammatory Hyperpigmentation, Stasis Dermatitis (Hemosiderin), Trauma

[Condition: Necrobiosis Lipoidica (NL / NLD)]

- Red Flags: Well-Demarcated Yellowish Atrophic Plaques, Shins Common, Prominent Telangiectasias Visible, ± Ulceration, Diabetes Association (often, but not always)

- Rule: IF Yellow Atrophic Plaque AND Shins AND Telangiectasias → Confidence Boost (NL) + Suppress (Granuloma Annulare, Sarcoidosis, Stasis Derm)

- DDx: Granuloma Annulare (Generalized/Patch), Sarcoidosis (Plaque), Stasis Dermatitis (Chronic), Morphoea

[Condition: Pretibial Myxedema (Thyroid Dermopathy)]

- Red Flags: History of Graves' Disease (Hyperthyroidism), Bilateral Firm Non-Pitting Edema/Plaques/Nodules, Anterior Lower Legs (Shins), 'Peau d'Orange' Appearance, ± Thyroid Acropachy/Exophthalmos

- Rule: IF Graves' History AND Non-Pitting Shin Edema/Plaques → Confidence Boost (Pretibial Myxedema) + Suppress (Lymphedema, Stasis Derm)

- DDx: Chronic Lymphedema, Stasis Dermatitis, Cellulitis (Chronic), Erythema Nodosum

[Condition: Sarcoidosis (Cutaneous)]

- Red Flags: Papules/Plaques/Nodules (often Violaceous/Brownish), Lupus Pernio (Nose/Cheeks/Ears), Scar Infiltration, Erythema Nodosum, Systemic Symptoms (Cough/Dyspnea), Bilateral Hilar Lymphadenopathy (CXR), Non-Caseating Granulomas (Biopsy)

- Rule: IF Papules/Nodules/Lupus Pernio AND Systemic Signs OR Biopsy → Confidence Boost (Sarcoidosis) + Suppress (Lupus [DLE], Lymphoma, Infection)

- DDx: Lupus Erythematosus (DLE), Lymphoma Cutis, Deep Fungal Infection, Cutaneous TB, Granuloma Annulare

[Condition: Pyoderma Gangrenosum (PG)]

- Red Flags: Rapidly Expanding Painful Ulcer(s), Violaceous Undermined Border, Purulent Base, ± Pathergy, Association with IBD/Arthritis/Hematologic Malignancy (~50%)

- Rule: IF Rapid Painful Ulcer AND Violaceous Undermined Border → Confidence Boost (PG) + Suppress (Vasculitis, Infection, Factitial)

- DDx: Vasculitic Ulcer, Infectious Ulcer (Bacterial/Fungal/Mycobacterial), Arterial/Venous Ulcer, Factitial Ulcer

[Condition: Acanthosis Nigricans]

- Red Flags: Symmetric Velvety Hyperpigmentation/Thickening, Flexural Areas (Neck/Axillae/Groin), Associated with Insulin Resistance (Obesity/Diabetes/PCOS) or Malignancy (Rare, Abrupt Onset)

- Rule: IF Velvety Flexural Hyperpigmentation → Confidence Boost (Acanthosis Nigricans) + Investigate Cause (Insulin Resistance/Malignancy)

- DDx: Post-Inflammatory Hyperpigmentation, Confluent and Reticulated Papillomatosis, Terra Firma-Forme Dermatosis

[Condition: Xanthomas (Eruptive)]

- Red Flags: Sudden Onset Crops of Small Yellow Papules (± Red Halo), Extensor Surfaces/Buttocks, Associated with Very High Triglycerides (Diabetes/Genetic)

- Rule: IF Acute Yellow Papules AND High Triglycerides → Confidence Boost (Eruptive Xanthomas) + Suppress (Folliculitis, Insect Bites)

- DDx: Folliculitis, Insect Bites (Papular Urticaria), Disseminated Granuloma Annulare

[Condition: Neurofibromatosis Type 1 (NF1)]

- Red Flags: ≥6 Café-au-Lait Macules, ≥2 Neurofibromas (or 1 Plexiform), Axillary/Inguinal Freckling (Crowe Sign), Optic Glioma, Lisch Nodules (Iris)

- Rule: IF ≥2 NF1 Criteria Met → Confidence Boost (NF1) + Suppress (McCune-Albright, Legius Syndrome)

- DDx: McCune-Albright Syndrome, Legius Syndrome, Multiple Lentigines Syndrome

[Condition: Tuberous Sclerosis Complex (TSC)]

- Red Flags: Facial Angiofibromas, Hypomelanotic Macules ('Ash Leaf'), Shagreen Patch, Periungual Fibromas, ± Seizures/Developmental Delay

- Rule: IF Facial Angiofibromas AND Hypomelanotic Macules AND/OR Other Major Features → Confidence Boost (TSC) + Suppress (Acne, Birt-Hogg-Dube)

- DDx: Acne Vulgaris (Facial Papules), Birt-Hogg-Dubé Syndrome, Multiple Trichoepitheliomas

[Condition: Calciphylaxis]

- Red Flags: End-Stage Renal Disease History, Extremely Painful Retiform Purpura -> Necrotic Ulcers (Black Eschar), Fatty Areas Common (Abdomen/Thighs)

- Rule: IF ESRD AND Painful Necrotic Ulcers/Reticular Purpura → Confidence Boost (Calciphylaxis) + Suppress (Vasculitis, Warfarin Necrosis) - URGENT

- DDx: Vasculitis (Severe), Warfarin Necrosis, Atheroembolism, Antiphospholipid Syndrome

[Condition: Erythema Nodosum (EN)]

- Red Flags: Acute Tender Erythematous Subcutaneous Nodules, Bilateral Anterior Shins, Bruise-like Evolution, No Ulceration, Often Associated with Trigger (Infection/Drug/Sarcoid/IBD)

- Rule: IF Acute Tender Shin Nodules AND No Ulceration → Confidence Boost (EN) + Suppress (Panniculitis [Other], Cellulitis)

- DDx: Other Panniculitis (e.g., Pancreatic, Alpha-1), Cellulitis, Superficial Thrombophlebitis

[Condition: Porphyria Cutanea Tarda (PCT)]

- Red Flags: Skin Fragility/Blisters/Erosions on Sun-Exposed Hands, Milia, Facial Hypertrichosis, ± Hyperpigmentation, Triggers (Alcohol/Estrogen/Hep C/Iron), Elevated Porphyrins

- Rule: IF Hand Blisters/Fragility AND Hypertrichosis AND Elevated Porphyrins → Confidence Boost (PCT) + Suppress (Pseudoporphyria, EBA) - (Same as Light/Bullous Category Rule)

- DDx: Pseudoporphyria (Drug-Induced), Epidermolysis Bullosa Acquisita, Bullous Pemphigoid



19. Tinea Ringworm Candidiasis and other Fungal Infections

[Condition: Tinea Pedis]

- Red Flags: Itchy Scaling/Maceration/Fissures Between Toes (Interdigital), Diffuse Scaling on Sole/Sides (Moccasin), ± Vesicles/Blisters (Inflammatory), KOH/Culture Positive

- Rule: IF Foot Scaling/Itch AND (Interdigital Maceration OR Moccasin Pattern OR Positive Mycology) → Confidence Boost (Tinea Pedis) + Suppress (Eczema, Psoriasis, Erythrasma)

- DDx: Dyshidrotic Eczema, Contact Dermatitis, Psoriasis, Erythrasma, Pitted Keratolysis

[Condition: Tinea Corporis]

- Red Flags: Annular Plaque(s), Raised Erythematous Scaly Border, Central Clearing, Itchy, KOH/Culture Positive

- Rule: IF Annular Plaque AND Scaly Border AND Positive Mycology → Confidence Boost (Tinea Corporis) + Suppress (Nummular Eczema, Granuloma Annulare, Psoriasis)

- DDx: Nummular Eczema, Granuloma Annulare, Psoriasis, Pityriasis Rosea (Herald Patch), Erythema Annulare Centrifugum

[Condition: Tinea Cruris]

- Red Flags: Well-Demarcated Red Patch in Groin/Inner Thighs, Raised Scaly Border, Central Clearing, Spares Scrotum Often, Itchy, KOH/Culture Positive

- Rule: IF Groin Rash AND Scaly Border AND Spares Scrotum → Confidence Boost (Tinea Cruris) + Suppress (Candida Intertrigo, Erythrasma, Inverse Psoriasis)

- DDx: Candida Intertrigo, Erythrasma, Inverse Psoriasis, Seborrhoeic Dermatitis

[Condition: Tinea Capitis]

- Red Flags: Child Predominance, Scalp Scaling/Patchy Hair Loss, Broken Hairs ('Black Dots'), ± Kerion (Inflammatory Mass), ± Occipital Lymphadenopathy, KOH/Culture Positive (Hair)

- Rule: IF Scalp Scaling/Hair Loss AND (Black Dots OR Kerion OR Positive Mycology) → Confidence Boost (Tinea Capitis) + Suppress (AA, Seb Derm, Psoriasis) - (Same as Hair Loss Category Rule)

- DDx: Alopecia Areata, Seborrhoeic Dermatitis, Scalp Psoriasis, Bacterial Folliculitis/Abscess (Kerion DDx)

[Condition: Candidiasis (Intertrigo)]

- Red Flags: Bright Red Moist Patches in Folds (Groin/Axillae/Inframammary), Satellite Papules/Pustules, Itchy/Burning, KOH Positive (Yeast/Pseudohyphae)

- Rule: IF Bright Red Fold Rash AND Satellite Lesions AND Positive KOH → Confidence Boost (Candida Intertrigo) + Suppress (Tinea Cruris, Inverse Psoriasis, Erythrasma)

- DDx: Tinea Cruris, Inverse Psoriasis, Seborrhoeic Dermatitis, Erythrasma, Irritant Contact Dermatitis

[Condition: Candidiasis (Oral - Thrush)]

- Red Flags: White Curd-Like Plaques (Scrape Off) on Oral Mucosa, ± Erythematous Base, ± Angular Cheilitis, Risk Factors (Infant/Dentures/Steroids/Immunosuppression), KOH Positive

- Rule: IF White Oral Plaques (Removable) ± Risk Factors → Confidence Boost (Oral Thrush) + Suppress (Leukoplakia, Lichen Planus)

- DDx: Oral Leukoplakia, Oral Lichen Planus (Plaque type), Geographic Tongue, Food Debris

[Condition: Pityriasis (Tinea) Versicolor]

- Red Flags: Multiple Oval Macules/Patches, Fine Scale (Scrapes Off), Upper Trunk/Neck/Arms, Hypo- or Hyperpigmented or Pink, KOH Positive ('Spaghetti & Meatballs')

- Rule: IF Multiple Scaly Macules AND Typical Distribution AND Positive KOH → Confidence Boost (Pityriasis Versicolor) + Suppress (Vitiligo, Pityriasis Alba) - (Same as Light/Pigmentary Category Rule)

- DDx: Vitiligo, Pityriasis Alba, Seborrhoeic Dermatitis (Mild), Post-Inflammatory Pigment Changes

[Condition: Malassezia (Pityrosporum) Folliculitis]

- Red Flags: Itchy Monomorphic Follicular Papules/Pustules, Upper Trunk/Shoulders Common, Worsens with Sweat/Occlusion, KOH Positive (Yeast in Follicle)

- Rule: IF Itchy Follicular Pustules AND Upper Trunk AND KOH Positive → Confidence Boost (Malassezia Folliculitis) + Suppress (Acne, Bacterial Folliculitis) - (Same as Acne Category Rule)

- DDx: Acne Vulgaris, Bacterial Folliculitis, Acneiform Drug Eruption

[Condition: Tinea Incognito]

- Red Flags: Atypical Fungal Infection Appearance (Reduced Scale/Indistinct Border/Pustules/Atrophy), History of Topical Steroid Use on Lesion, KOH/Culture Still Positive (May be Difficult)

- Rule: IF Atypical Rash AND Topical Steroid Use History AND Positive Mycology → Confidence Boost (Tinea Incognito) + Suppress (Eczema, Psoriasis, Lupus)

- DDx: Eczema, Psoriasis, Discoid Lupus, Bacterial Folliculitis

[Condition: Sporotrichosis (Lymphocutaneous)]

- Red Flags: Primary Lesion (Papule/Ulcer) at Trauma Site, Secondary Nodules Develop Along Lymphatic Drainage ('Sporotrichoid Spread'), History of Plant Trauma ('Rose Gardener'), Biopsy/Culture Positive (Dimorphic Fungus)

- Rule: IF Primary Lesion AND Nodules Along Lymphatics AND Plant Trauma History → Confidence Boost (Sporotrichosis) + Suppress (Atypical Mycobacteria, Nocardia)

- DDx: Atypical Mycobacterial Infection (M. marinum), Nocardiosis, Tularemia, Leishmaniasis (Rarely Sporotrichoid)

[Condition: Chromoblastomycosis]

- Red Flags: Slow-Growing Verrucous (Warty) Plaques/Nodules, Lower Extremities Common, History of Trauma in Tropics/Subtropics, Sclerotic Bodies ('Copper Pennies') on Biopsy

- Rule: IF Chronic Warty Leg Lesion AND Endemic Exposure AND Sclerotic Bodies (Biopsy) → Confidence Boost (Chromoblastomycosis) + Suppress (SCC, Blastomycosis, TB)

- DDx: Squamous Cell Carcinoma (Verrucous), Blastomycosis, Cutaneous Tuberculosis (Verrucosa Cutis), Leishmaniasis

[Condition: Cryptococcosis (Cutaneous)]

- Red Flags: Immunocompromised Host (esp. HIV/Organ Transplant), Skin Lesions (Papules/Nodules [often Umbilicated], Ulcers, Abscesses), Often Head/Neck, Indicates Systemic Infection, Positive Biopsy/Culture/Serum Antigen

- Rule: IF Skin Lesions (esp. Umbilicated) AND Immunocompromised AND Positive Crypto Test → Confidence Boost (Cutaneous Cryptococcosis) + Suppress (Molluscum, BCC, Histoplasmosis)

- DDx: Molluscum Contagiosum, Basal Cell Carcinoma, Histoplasmosis, Penicilliosis (Talaromycosis), Bacterial Abscess



20. Urticaria Hives

[Condition: Acute Urticaria]

- Red Flags: Sudden Onset Itchy Wheals, Individual Lesions Last <24h, Total Episode <6 Weeks, Identifiable Trigger Often (Infection/Food/Drug)

- Rule: IF Acute Wheals (<24h each) AND Duration <6 Weeks → Confidence Boost (Acute Urticaria) + Suppress (Chronic Urticaria, Urticarial Vasculitis)

- DDx: Chronic Urticaria (Early), Urticarial Vasculitis, Insect Bites, Drug Eruption (Urticarial)

[Condition: Chronic Spontaneous Urticaria (CSU)]

- Red Flags: Recurrent Wheals (Lasting <24h each) ± Angioedema, Occurring Most Days for ≥6 Weeks, No Identifiable External Trigger, Autoimmune Basis Common

- Rule: IF Recurrent Wheals (≥6 Weeks) AND No Clear Trigger → Confidence Boost (CSU) + Suppress (Inducible Urticaria, Urticarial Vasculitis)

- DDx: Inducible Urticaria, Urticarial Vasculitis, Mastocytosis, Food Allergy (Rare for Chronic)

[Condition: Dermatographism (Symptomatic)]

- Red Flags: Linear Itchy Wheals Induced by Stroking/Scratching Skin, Appears within Minutes, Fades within ~30-60 min

- Rule: IF Wheals Form on Stroking AND Itchy → Confidence Boost (Symptomatic Dermatographism) + Suppress (Other Urticarias)

- DDx: Simple Dermatographism (Non-itchy), Other Physical Urticarias

[Condition: Cold Urticaria]

- Red Flags: Wheals/Angioedema on Cold-Exposed Skin (esp. on Rewarming), Positive Ice Cube Test, Risk of Anaphylaxis with Systemic Cooling (Swimming)

- Rule: IF Wheals After Cold Exposure AND Positive Ice Cube Test → Confidence Boost (Cold Urticaria) + Suppress (Chilblains, Raynaud's)

- DDx: Chilblains, Raynaud's Phenomenon, Cryoglobulinemia, Cold Panniculitis

[Condition: Cholinergic Urticaria]

- Red Flags: Small Punctate Wheals (1-4mm) with Large Flare, Triggered by Sweating/Exercise/Heat/Stress, Itchy/Prickly Sensation

- Rule: IF Small Wheals with Flare AND Triggered by Heat/Exercise/Stress → Confidence Boost (Cholinergic Urticaria) + Suppress (Heat Contact Urticaria, Miliaria)

- DDx: Heat Contact Urticaria, Miliaria (Heat Rash), Anaphylaxis (Exercise-Induced)

[Condition: Delayed Pressure Urticaria (DPU)]

- Red Flags: Deep Painful/Burning Swelling, Appears 3-12 Hours After Sustained Pressure, Lasts >24 Hours, Often Debilitating

- Rule: IF Delayed Swelling After Pressure → Confidence Boost (DPU) + Suppress (Angioedema [Other Causes], Simple Bruising)

- DDx: Angioedema (Histaminergic/Bradykinin), Bruising/Trauma, Panniculitis

[Condition: Angioedema (without Urticaria)]

- Red Flags: Recurrent Deep Swelling (Lips/Tongue/Throat/Limbs/Bowel), NO Hives, Consider Bradykinin-Mediated (HAE/ACE-i) vs Histaminergic

- Rule: IF Recurrent Swelling AND NO Hives → Confidence Boost (Angioedema) + Investigate Cause (HAE/ACE-i/Idiopathic)

- DDx: Allergic Reaction (with Angioedema Only), Cellulitis (Facial), Lymphedema (Acute)

[Condition: Hereditary Angioedema (HAE)]

- Red Flags: Recurrent Angioedema WITHOUT Hives, Family History, Laryngeal Edema Risk, Abdominal Pain Attacks, Triggered by Trauma/Stress, Low C4 / Low/Dysfunctional C1-INH

- Rule: IF Recurrent Angioedema (No Hives) AND Family History OR Low C4/C1-INH → Confidence Boost (HAE) + Suppress (Allergic Angioedema, ACE-i Angioedema)

- DDx: ACE Inhibitor Angioedema, Allergic Angioedema, Idiopathic Angioedema

[Condition: ACE Inhibitor-Induced Angioedema]

- Red Flags: Angioedema (esp. Lips/Tongue/Throat) WITHOUT Hives, Patient Taking ACE Inhibitor (Any Duration), Airway Compromise Risk

- Rule: IF Angioedema (No Hives) AND Taking ACE Inhibitor → Confidence Boost (ACE-i Angioedema) + Suppress (HAE, Allergic Angioedema)

- DDx: Hereditary Angioedema, Allergic Angioedema, Idiopathic Angioedema

[Condition: Urticarial Vasculitis (UV)]

- Red Flags: Urticarial Lesions Lasting >24 Hours, May Burn or Hurt, Resolve with Bruising/Hyperpigmentation, ± Systemic Symptoms (Fever/Arthralgia/Abdominal Pain), ± Hypocomplementemia, Biopsy shows LCV

- Rule: IF Urticarial Lesions >24h AND Bruising/Pain → Confidence Boost (UV) + Suppress (Simple Urticaria, Serum Sickness)

- DDx: Chronic Urticaria, Serum Sickness, Erythema Multiforme, Sweet Syndrome



21. Vascular Tumors

[Condition: Cherry Angioma]

- Red Flags: Small Bright Red Papule, Multiple Lesions Common, Trunk Predominant, Increases with Age, Dermoscopy (Red Lacunae)

- Rule: IF Small Bright Red Papule AND Typical Appearance → Confidence Boost (Cherry Angioma) + Suppress (Amelanotic Melanoma, Angiokeratoma) - (Same as Benign Tumor Rule)

- DDx: Amelanotic Melanoma (Small), Angiokeratoma, Pyogenic Granuloma (Small)

[Condition: Infantile Hemangioma (IH)]

- Red Flags: Appears Post-Birth -> Rapid Growth (Proliferation) -> Slow Involution, Bright Red ('Strawberry') or Bluish Nodule, GLUT-1 Positive (Immunohistochemistry)

- Rule: IF Appears Post-Birth AND Rapid Growth Phase → Confidence Boost (IH) + Suppress (Vascular Malformation, Congenital Hemangioma)

- DDx: Vascular Malformation (PWS/Venous/Lymphatic), Congenital Hemangioma (RICH/NICH), Pyogenic Granuloma, Spitz Nevus

[Condition: Nevus Simplex (Salmon Patch / Stork Bite)]

- Red Flags: Flat Pink/Red Macular Patch, Nape/Glabella/Eyelids Common, Present at Birth, Blanches with Pressure, Facial Lesions Often Fade

- Rule: IF Flat Pink Patch AND Typical Location AND Present at Birth → Confidence Boost (Nevus Simplex) + Suppress (Port Wine Stain)

- DDx: Port Wine Stain, Cutis Marmorata Telangiectatica Congenita

[Condition: Port-Wine Stain (Nevus Flammeus)]

- Red Flags: Flat Pink/Red Patch at Birth -> Darkens/Thickens with Age, Unilateral Often, Follows Dermatome Often (esp. Face - V1 risk of Sturge-Weber), Persists Throughout Life, GLUT-1 Negative

- Rule: IF Flat Red/Purple Patch AND Present at Birth AND Persists/Darkens → Confidence Boost (PWS) + Suppress (Nevus Simplex, IH [Macular])

- DDx: Nevus Simplex, Infantile Hemangioma (Macular/Abortive), Cutis Marmorata Telangiectatica Congenita

[Condition: Venous Lake]

- Red Flags: Soft Compressible Blue/Purple Papule, Lip/Ear/Face Common, Elderly Patient, Sun-Exposed Site, Diascopy shows Emptying

- Rule: IF Compressible Blue Papule AND Lip/Ear/Face Elderly → Confidence Boost (Venous Lake) + Suppress (Melanoma [Nodular], Blue Nevus)

- DDx: Nodular Melanoma, Blue Nevus, Angiokeratoma

[Condition: Pyogenic Granuloma]

- Red Flags: Rapidly Growing Red/Violaceous Papule/Nodule, Bleeds Easily, Often Crusted/Ulcerated, ± Collarette of Scale, Fingers/Lips/Gums Common

- Rule: IF Rapidly Growing Friable Red Nodule → Confidence Boost (Pyogenic Granuloma) + Suppress (Amelanotic Melanoma, SCC, Hemangioma) - (Same as Benign Tumor Rule)

- DDx: Amelanotic Melanoma, Squamous Cell Carcinoma, Hemangioma, Spitz Nevus

[Condition: Spider Angioma]

- Red Flags: Central Red Punctum, Radiating Capillary 'Legs', Blanches with Central Pressure (Legs Refill Centrifugally), Face/Neck/Upper Trunk Common, Associated with Estrogen Excess (Pregnancy/Liver Disease)

- Rule: IF Central Punctum AND Radiating Legs AND Blanches Centrally → Confidence Boost (Spider Angioma) + Suppress (Telangiectasia [Simple], Cherry Angioma)

- DDx: Simple Telangiectasia, Cherry Angioma (Small), Insect Bite

[Condition: Angiokeratoma]

- Red Flags: Dark Red/Black Papules, ± Hyperkeratotic/Warty Surface, Scrotum/Vulva (Fordyce) or Limbs (Solitary/Circumscriptum) or Generalized (Fabry Disease)

- Rule: IF Dark Red/Black Warty Papules → Confidence Boost (Angiokeratoma) + Suppress (Melanoma, Wart, Angioma)

- DDx: Melanoma (Nodular), Verruca Vulgaris, Cherry Angioma, Kaposi Sarcoma

[Condition: Lymphatic Malformation (Lymphangioma Circumscriptum)]

- Red Flags: Clusters of Deep-Seated Vesicles ('Frog Spawn'), Translucent or Hemorrhagic Content, Often Present Since Childhood, Trunk/Proximal Limbs Common

- Rule: IF Clustered 'Frog Spawn' Vesicles → Confidence Boost (Lymphatic Malformation) + Suppress (Herpes, Hemangioma)

- DDx: Herpes Simplex/Zoster, Hemangioma (Verrucous), Angiokeratoma

[Condition: Glomus Tumor]

- Red Flags: Small Blue/Red Nodule, Often Subungual, Severe Paroxysmal Pain, Cold Sensitivity, Localized Tenderness

- Rule: IF Small Nodule AND Severe Pain/Cold Sensitivity AND Subungual Common → Confidence Boost (Glomus Tumor) + Suppress (Neuroma, Hemangioma)

- DDx: Neuroma, Hemangioma, Eccrine Spiradenoma, Melanoma (Amelanotic)

[Condition: Kaposi Sarcoma (KS)]

- Red Flags: Violaceous/Brownish Macules/Patches/Papules/Nodules, May Follow Skin Lines, Location Variable, ± Lymphedema, HHV-8 Association, Immunosuppression Link (esp AIDS)

- Rule: IF Violaceous/Brown Lesions AND (Typical Distribution OR Immunosuppressed) → Confidence Boost (KS) + Suppress (Bruise, Angiosarcoma, Bacillary Angiomatosis) - (Same as Malignant Lesions Rule)

- DDx: Bruise, Stasis Dermatitis, Angiosarcoma, Bacillary Angiomatosis, Melanoma

[Condition: Angiosarcoma]

- Red Flags: Elderly Patient, Scalp/Face Common, Bruise-Like Patches (Ecchymotic), Edema, History of Lymphedema or Radiation

- Rule: IF Bruise-Like Patch/Nodules AND (Scalp/Face elderly OR Lymphedema OR Radiation Field) → Confidence Boost (Angiosarcoma) + Suppress (Bruise, KS, Cellulitis) - (Same as Malignant Lesions Rule)

- DDx: Bruise, Kaposi Sarcoma, Cellulitis, Hematoma



22. Vasculitis Photos

[Condition: Leukocytoclastic Vasculitis (LCV) / CSVV]

- Red Flags: Palpable Purpura (Classic), Lower Legs Predominant, ± Macules/Vesicles/Ulcers, Recent Trigger (Infection/Drug) Possible, Biopsy shows Neutrophilic Vessel Inflammation/Debris

- Rule: IF Palpable Purpura AND Lower Legs → Confidence Boost (LCV) + Suppress (Thrombocytopenic Purpura, Schamberg's)

- DDx: Thrombocytopenic Purpura (ITP/TTP - non-palpable), Pigmented Purpuric Dermatosis (Schamberg's), Septic Emboli, Antiphospholipid Syndrome

[Condition: Henoch-Schönlein Purpura (HSP) / IgA Vasculitis]

- Red Flags: Palpable Purpura (Buttocks/Legs), Arthritis/Arthralgia, Abdominal Pain, Hematuria/Proteinuria (Renal), Often Children Post-URI, IgA Deposition (DIF)

- Rule: IF Purpura AND Arthritis AND Abdominal Pain OR Renal Involvement → Confidence Boost (HSP) + Suppress (LCV [Other], ITP)

- DDx: Leukocytoclastic Vasculitis (Other causes), Idiopathic Thrombocytopenic Purpura (ITP), Acute Abdomen (Other causes), Post-Streptococcal Glomerulonephritis

[Condition: Urticarial Vasculitis (UV)]

- Red Flags: Urticarial Lesions Lasting >24 Hours, Burning/Pain > Itch, Resolve with Bruising/Hyperpigmentation, ± Systemic Symptoms (Arthralgia/Fever), ± Hypocomplementemia, Biopsy shows LCV

- Rule: IF Urticarial Lesions >24h AND Bruising/Pain → Confidence Boost (UV) + Suppress (Simple Urticaria, Serum Sickness) - (Same as Urticaria Category Rule)

- DDx: Chronic Urticaria, Serum Sickness, Erythema Multiforme, Sweet Syndrome, SLE

[Condition: Cryoglobulinemic Vasculitis]

- Red Flags: Palpable Purpura, Ulcers, Livedo, Acral Necrosis (Cold-Related Possible), Associated Arthralgia/Neuropathy/Glomerulonephritis, Positive Serum Cryoglobulins, Often Hep C Association

- Rule: IF Purpura/Ulcers AND Positive Cryoglobulins AND/OR Hep C → Confidence Boost (Cryo Vasculitis) + Suppress (LCV [Other], APS)

- DDx: Leukocytoclastic Vasculitis (Other causes), Antiphospholipid Syndrome, Polyarteritis Nodosa, Cholesterol Emboli

[Condition: Cutaneous Polyarteritis Nodosa (cPAN)]

- Red Flags: Tender Subcutaneous Nodules, Livedo Reticularis/Racemosa, Ulcers ('Punched Out'), Digital Infarcts Possible, Lower Legs Common, Confined to Skin/Joints/Muscle

- Rule: IF Subcutaneous Nodules AND Livedo AND Ulcers/Infarcts → Confidence Boost (cPAN) + Suppress (Systemic PAN, Nodular Vasculitis)

- DDx: Systemic Polyarteritis Nodosa, Nodular Vasculitis, Erythema Nodosum, Thrombophlebitis

[Condition: Granulomatosis with Polyangiitis (GPA / Wegener's)]

- Red Flags: Purpura/Ulcers/Nodules (Skin), Sinusitis/Epistaxis/Saddle Nose (Upper Respiratory), Cough/Hemoptysis (Lower Respiratory), Glomerulonephritis (Kidney), c-ANCA/Anti-PR3 Positive

- Rule: IF Multi-System (Resp/Kidney/Skin) Vasculitis AND c-ANCA Positive → Confidence Boost (GPA) + Suppress (MPA, EGPA, Infection)

- DDx: Microscopic Polyangiitis (MPA), Eosinophilic Granulomatosis with Polyangiitis (EGPA), Infections (TB/Fungal), Cocaine-Induced Midline Destruction (CIMD), Lymphoma

[Condition: Microscopic Polyangiitis (MPA)]

- Red Flags: Palpable Purpura Common, Rapidly Progressive Glomerulonephritis, Pulmonary Hemorrhage, NO Granulomas, p-ANCA/Anti-MPO Positive Often

- Rule: IF Glomerulonephritis AND Pulmonary Hemorrhage AND p-ANCA Positive → Confidence Boost (MPA) + Suppress (GPA, Goodpasture's)

- DDx: Granulomatosis with Polyangiitis (GPA), Goodpasture Syndrome, SLE Nephritis

[Condition: Eosinophilic Granulomatosis with Polyangiitis (EGPA / Churg-Strauss)]

- Red Flags: History of Asthma/Allergic Rhinitis, Marked Peripheral Eosinophilia, Purpura/Nodules/Urticaria (Skin), Neuropathy Common, Pulmonary Infiltrates, ± ANCA Positive (p-ANCA/MPO)

- Rule: IF Asthma AND Eosinophilia AND Systemic Vasculitis Signs → Confidence Boost (EGPA) + Suppress (GPA, MPA, Hypereosinophilic Syndrome)

- DDx: Granulomatosis with Polyangiitis (GPA), Microscopic Polyangiitis (MPA), Hypereosinophilic Syndrome, Allergic Bronchopulmonary Aspergillosis

[Condition: Giant Cell Arteritis (GCA / Temporal Arteritis)]

- Red Flags: Age >50, New Headache (Temporal), Jaw Claudication, Visual Symptoms (Amaurosis Fugax), Tender/Pulseless Temporal Artery, Elevated ESR/CRP

- Rule: IF Age >50 AND New Headache AND Jaw Claudication OR Visual Symptoms → Confidence Boost (GCA) + Suppress (Migraine, Tension Headache) - URGENT OPHTHO/RHEUM CONSULT

- DDx: Migraine, Tension Headache, Trigeminal Neuralgia, Polymyalgia Rheumatica (overlaps)

[Condition: Behçet Disease]

- Red Flags: Recurrent Painful Oral Aphthae, Recurrent Painful Genital Ulcers, Eye Inflammation (Uveitis), Skin Lesions (EN-like/Pseudofolliculitis/Papulopustular), Positive Pathergy Test

- Rule: IF Recurrent Oral AND Genital Ulcers AND (Eye OR Skin Lesions OR Pathergy) → Confidence Boost (Behçet's) + Suppress (SLE, Crohn's, Herpes)

- DDx: Systemic Lupus Erythematosus, Crohn's Disease, Herpes Simplex (Recurrent), Reactive Arthritis, Sweet Syndrome

[Condition: Nodular Vasculitis / Erythema Induratum]

- Red Flags: Tender Deep-Seated Nodules/Plaques, Posterior Lower Legs (Calves), Often Ulcerate, Chronic Course, Middle-Aged Women Common, ± Association with TB (Bazin)

- Rule: IF Tender Calf Nodules ± Ulceration → Confidence Boost (Nodular Vasculitis) + Suppress (EN, Panniculitis [Other], PAN)

- DDx: Erythema Nodosum, Pancreatic Panniculitis, Alpha-1-Antitrypsin Deficiency Panniculitis, Cutaneous Polyarteritis Nodosa



23. Warts Molluscum and other Viral Infections

[Condition: Common Warts (Verruca Vulgaris)]

- Red Flags: Hyperkeratotic Papule/Nodule, Rough ('Cauliflower') Surface, Hands/Fingers/Knees Common, Thrombosed Capillaries ('Black Dots'), Disruption of Skin Lines

- Rule: IF Hyperkeratotic Papule AND Black Dots AND Disrupted Skin Lines → Confidence Boost (Common Wart) + Suppress (Corn, SCC, Lichen Planus)

- DDx: Corn/Callus, Squamous Cell Carcinoma, Seborrheic Keratosis, Lichen Planus (Hypertrophic)

[Condition: Plantar Warts (Verruca Plantaris)]

- Red Flags: Hyperkeratotic Papule/Plaque on Sole, Interrupts Skin Lines, Thrombosed Capillaries ('Black Dots'), Tender with Lateral Pressure (Squeeze)

- Rule: IF Plantar Lesion AND Black Dots AND Interrupts Skin Lines → Confidence Boost (Plantar Wart) + Suppress (Corn, Callus, Foreign Body)

- DDx: Corn, Callus, Foreign Body Reaction, Porokeratosis Plantaris

[Condition: Plane Warts (Verruca Plana)]

- Red Flags: Multiple Small Flat-Topped Papules (1-5mm), Skin-Colored/Light Brown, Smooth Surface, Face/Dorsal Hands/Shins Common, Often Grouped/Linear (Koebner)

- Rule: IF Multiple Small Flat-Topped Papules AND Typical Location → Confidence Boost (Plane Warts) + Suppress (Lichen Nitidus, Syringoma)

- DDx: Lichen Nitidus, Syringoma, Molluscum Contagiosum (Small/Flat), Acrokeratosis Verruciformis

[Condition: Molluscum Contagiosum]

- Red Flags: Dome-Shaped Papules (2-5mm), Central Umbilication, Pearly/Flesh-Colored, Children Common (Trunk/Limbs/Face), Adults (Genital - STD), Poxvirus Cause

- Rule: IF Dome-Shaped Papule AND Central Umbilication → Confidence Boost (Molluscum) + Suppress (Wart, Folliculitis, Crypto [HIV])

- DDx: Verruca Vulgaris (Small), Folliculitis, Cryptococcosis (Cutaneous in HIV), Basal Cell Carcinoma (Small Nodular)

[Condition: Herpes Zoster (Shingles)]

- Red Flags: Unilateral Vesicular Eruption, Confined to Dermatome, Does Not Cross Midline, Preceding Pain/Tingling Common, VZV Reactivation

- Rule: IF Unilateral Vesicular Rash AND Dermatomal Distribution → Confidence Boost (Shingles) + Suppress (Herpes Simplex [Zosteriform], Contact Derm)

- DDx: Herpes Simplex (Zosteriform Presentation), Allergic Contact Dermatitis (Linear), Insect Bites (Linear)

[Condition: Herpes Simplex (e.g., Oral/Whitlow)]

- Red Flags: Grouped Vesicles on Erythematous Base, Progress to Erosions/Ulcers, Lip ('Cold Sore') or Finger ('Whitlow') Common Sites, Recurrent Episodes, Tingling Prodrome

- Rule: IF Grouped Vesicles/Erosions AND Recurrent AND Typical Site → Confidence Boost (Herpes Simplex) + Suppress (Aphthous Ulcer, Impetigo, Paronychia)

- DDx: Aphthous Ulcer (Oral), Impetigo, Paronychia (Bacterial/Fungal), Hand Foot and Mouth Disease (Oral)

[Condition: Hand, Foot, and Mouth Disease (HFMD)]

- Red Flags: Oral Vesicles/Ulcers, PLUS Papules/Vesicles on Hands/Feet (Palms/Soles characteristic), Usually Children <5, Enterovirus Cause (Coxsackie etc)

- Rule: IF Oral Lesions AND Hand/Foot Lesions → Confidence Boost (HFMD) + Suppress (Herpetic Gingivostomatitis, Varicella) - (Same as Exanthems Rule)

- DDx: Herpetic Gingivostomatitis, Varicella, Aphthous Stomatitis, Herpangina

[Condition: Orf (Contagious Ecthyma)]

- Red Flags: Solitary Lesion on Hand/Finger, Evolves through Papule -> Targetoid Nodule/Bulla -> Crusted -> Granulomatous Stages (~6 wks), History of Sheep/Goat Contact

- Rule: IF Hand Lesion AND Evolves Through Stages AND Sheep/Goat Contact → Confidence Boost (Orf) + Suppress (Milker's Nodule, Pyogenic Granuloma, Infection)

- DDx: Milker's Nodule, Pyogenic Granuloma, Bacterial Infection (Abscess/Furuncle), Atypical Mycobacteria, Deep Fungal Infection

[Condition: Milker's Nodule]

- Red Flags: Reddish/Violaceous Firm Papule(s)/Nodule(s) on Hands, History of Cattle Contact (Udders/Muzzles), Less Inflammatory than Orf, Spontaneous Resolution (~4-6 wks)

- Rule: IF Hand Nodule(s) AND Cattle Contact → Confidence Boost (Milker's Nodule) + Suppress (Orf, Wart)

- DDx: Orf, Verruca Vulgaris, Pyogenic Granuloma, Foreign Body Granuloma

[Condition: Kaposi's Varicelliform Eruption (Eczema Herpeticum)]

- Red Flags: Underlying Eczema (AD), Abrupt Onset Monomorphic Vesicles/Punched-Out Erosions, Clustered in Eczema Areas, ± Fever/Malaise, HSV Cause

- Rule: IF AD History AND Acute Monomorphic Vesicles/Erosions → Confidence Boost (Eczema Herpeticum) + Suppress (AD Flare, Impetigo) - (Same as Bullous/Eczema Rule)

- DDx: Severe Atopic Dermatitis Flare, Bullous Impetigo, Varicella

[Condition: Gianotti-Crosti Syndrome]

- Red Flags: Young Child, Symmetric Monomorphic Papules, Face/Buttocks/Extensor Limbs, Spares Trunk, Often Post-Viral (EBV/HepB etc) or Post-Vaccine, Self-Limiting

- Rule: IF Child AND Symmetric Acral/Facial/Buttock Papules → Confidence Boost (Gianotti-Crosti) + Suppress (Papular Urticaria, Scabies, HFMD)

- DDx: Papular Urticaria, Scabies, Hand Foot and Mouth Disease (Atypical), Lichen Planus (Papular)

[Condition: Epidermodysplasia Verruciformis (EV)]

- Red Flags: Widespread Persistent Flat Warts (Verruca Plana-like / Pityriasis Versicolor-like), Onset Childhood, High Risk of SCC in Sun-Exposed Areas, Inherited Susceptibility (TMC6/8)

- Rule: IF Widespread Flat Warts AND Childhood Onset AND SCC Development → Confidence Boost (EV) + Suppress (Verruca Plana [Severe], Pityriasis Versicolor)

- DDx: Verruca Plana (Severe/Recalcitrant), Pityriasis Versicolor, Acanthosis Nigricans (Papillomatous)

[Condition: Mpox (formerly Monkeypox)]

- Red Flags: Fever/Headache/Lymphadenopathy Prodrome, Followed by Rash (Vesicles -> Pustules -> Crusts), Lesions Often Deep-Seated/Umbilicated, Anogenital Common in Recent Outbreak, PCR Positive

- Rule: IF Fever/Lymphadenopathy AND Vesiculopustular Rash (Umbilicated) → Confidence Boost (Mpox) + Suppress (Varicella, Disseminated HSV/Zoster, Smallpox)

- DDx: Varicella, Disseminated Herpes Simplex/Zoster, Hand Foot and Mouth Disease (Severe), Bacterial Folliculitis/Abscess, Insect Bites



"""


# --- Keyword Mapping (EXPANDED based on NEW detailed questions) ---
# Symptoms - Expanded based on KB details
SYMPTOM_KEYWORDS = {
    "Itching (maybe rate severity?)": [
        "itch", "pruritus", "pruritic", "itchy", "prickly" # Added prickly (Cholinergic Urticaria)
        ],
    "Pain": [
        "pain", "hurt", "painful", # Added painful
        "paroxysmal pain" # Glomus tumor
        ],
    "Tenderness to touch": [
        "tender", "tenderness", "painful" # Added painful as overlap
        ],
    "Burning Sensation": [
        "burn", "burning", "sting", "stinging" # Seems complete
        ],
    "Redness": [
        "red", "reddish", "erythema", "erythematous", # Added reddish
        "violaceous", "purpuric", "purple", # Grouped purple tones
        "flushing", "bright red", "beefy-red", # Specific red types
        "pink", "salmon", # Pink/Salmon tones
        "brownish", # Keep, but less specific (Sarcoid, KS, PIH link)
        "dusky", # Important for ischemia/SJS/Nec Fasc
        "orange", # Specific for PRP
        "ecchymotic", # Bruise-like redness
        # Removed "violaceous" duplicate
        ],
    "Swelling": [
        "swell", "edema", "swollen", "indurated", "thickened", "enlargement",
        "boggy", "puffy", "brawny", # Added puffy (MCTD), brawny (LDS)
        "nodule", "tumor", "mass", "plaque", "hyperplasia" # Added related structural terms implying swelling/thickening
        # 'Indurated' & 'thickened' also relate to Morphology: Thickened Skin
        ],
    "Dryness/Flaking/Scaling": [
        "dry", "xerosis", "asteatotic", "flake", "flaky", "scale", "scaling", "scaly",
        "desquamation", "rough", "sandpaper", "cracked", "craquele", # Added roughness/cracking
        "keratotic", "hyperkeratotic", # Added keratin terms
        "lichenified" # Thickened AND scaly/dry appearance often
        ],
    "Blisters (fluid-filled)": [
        "blister", "bulla", "bullae", "vesicle", "vesicular", "fluid-filled", # Added vesicular
        "flaccid", "tense", # Added types of blisters
        "hemorrhagic bullae" # Specific type
        ],
    "Pus bumps (pimples)": [
        "pimple", "pus", "pustule", "pustular", "follicular pustule", # Added pustular
        "abscess", "suppurative", "fluctuant", # Added fluctuant
        "furuncle", "carbuncle", "boil", # Specific types
        "pyoderma" # Pus in skin
        ],
    "Bleeding": [
        "bleed", "bleeding", "hemorrhage", "hemorrhagic", "friable" # Seems complete
        ],
    "Oozing/Weeping": [
        "ooze", "oozing", "weep", "weeping", "discharge", "exudate", "macerated",
        "drainage", "serous" # Added drainage, serous
        ],
    "Numbness/Tingling": [
        "numb", "numbness", "tingling", "paresthesia", "sensory loss", "prodrome" # Added prodrome
        ],
    "None of the above": []
 }

# Medical Conditions - Expanded and refined
CONDITION_KEYWORDS = {
    "Eczema / Atopic Dermatitis": [
        "eczema", "atopic dermatitis", "ad", "atopy", "dermatitis", # Added dermatitis
        "nummular", "discoid", "asteatotic", "dyshidrotic", "pompholyx", # Types of eczema
        "lichen simplex chronicus", "lsc", "prurigo", "contact dermatitis", # Related itchy conditions
        "stasis dermatitis", "xerosis" # Related conditions often in context
        ],
    "Psoriasis": [
        "psoriasis", "psoriatic", "guttate", "plaque", "inverse", "flexural",
        "pustular psoriasis", "palmoplantar pustulosis", "ppp" # Specific types
        ],
    "Acne (severe or treated)": [
        "acne", "comedone", "comedones", "acne vulgaris", "cystic acne", # Added types
        "acneiform", "chloracne", "favre-racouchot" # Related conditions
        ],
    "Rosacea": [
        "rosacea", "rhinophyma", "periorificial dermatitis", "demodicosis" # Includes variants and related
        ],
    "Skin Cancer History (BCC/SCC/Melanoma)": [
        "skin cancer", "cancer", "malignancy", "malignant", # Added synonyms
        "bcc", "basal cell carcinoma", "scc", "squamous cell carcinoma", # Specific types
        "melanoma", "bowen", "paget", "merkel", "dfsp", "ks", "kaposi", # Other skin cancers from KB
        "angiosarcoma", "metastasis", "lymphoma cutis", "mycosis fungoides", "mf" # Other skin cancers from KB
        ],
    "Pre-cancerous spots (AKs)": [
        "actinic keratosis", "ak", "solar keratosis", "pre-cancer", "dysplasia", # Added synonyms
        "actinic cheilitis", "leukoplakia" # Related pre-malignant
        ],
    "Shingles (Herpes Zoster)": [
        "shingles", "zoster", "herpes zoster", "vzv", "varicella zoster" # Added synonyms
        ],
    "Cold sores (Herpes Simplex)": [
        "cold sore", "herpes", "herpes simplex", "hsv", "whitlow", # Added synonyms
        "eczema herpeticum", "kaposi varicelliform" # HSV complications
        ],
    "Warts": [
        "wart", "verruca", "verruca vulgaris", "verruca plana", "verruca plantaris", # Added specific types
        "hpv", "human papillomavirus", "condyloma", "condyloma acuminatum" # Added HPV and genital warts
        ],
    "Fungal Infections (Tinea/Candida)": [
        "fungus", "fungal", "tinea", "ringworm", "candida", "yeast", "mycosis",
        "dermatophyte", "onychomycosis", "tinea pedis", "tinea cruris", "tinea corporis", # Specific tinea
        "tinea capitis", "tinea versicolor", "pityriasis versicolor", "malassezia", # More specific types
        "pityrosporum", "thrush", "intertrigo", # Candida related
        "sporotrichosis", "chromoblastomycosis", "cryptococcosis" # Deep fungal from KB
        ],
    "Hives (Urticaria)": [
        "hives", "urticaria", "wheal", "wheals", "angioedema", # Added angioedema
        "dermatographism", "cholinergic", "cold urticaria", "pressure urticaria" # Specific types
        ],
    "Significant Sunburns (blistering)": [
        "sunburn", "blistering sunburn", "sun damage", "photodamage", "solar elastosis" # Added related terms
        ],
    "Allergies (Hay fever, Asthma)": [
        "allerg", "hay fever", "asthma", "rhinitis", "atopy", "allergic rhinitis", # Added full term
        "hypersensitivity" # Broader term
        ],
    "Diabetes (Type 1 / Type 2)": [
        "diabete", "insulin resistance", "dm", "iddm", "niddm", # Added abbreviations
        "diabetic dermopathy", "necrobiosis lipoidica" # Specific diabetic skin signs
        ],
    "Thyroid disease (Hyper/Hypo)": [
        "thyroid", "hyperthyroid", "hypothyroid", "graves", "hashimoto", # Added hashimoto
        "pretibial myxedema", "thyroid dermopathy", "thyroid acropachy" # Specific signs
        ],
    "Autoimmune disease (Lupus, RA, IBD etc)": [
        "autoimmune", "lupus", "sle", "dle", "scle", "acle", # Added lupus variants
        "rheumatoid arthritis", "ra", "ibd", "inflammatory bowel disease", "crohn", "ulcerative colitis", # Added specifics
        "sjogren", "scleroderma", "ssc", "systemic sclerosis", "morphoea", # Added specifics
        "pemphigoid", "pemphigus", "dermatomyositis", "dm", # Added DM
        "connective tissue disease", "ctd", "mctd", # Added MCTD
        "vasculitis", "polyarteritis nodosa", "pan", "gpa", "wegener", "mpa", "egpa", "churg-strauss", # Vasculitides
        "behcet", "sarcoidosis", "alopecia areata", "vitiligo", "celiac", # Others from KB review
        "relapsing polychondritis" # Added RP
        ],
    "Immune system issues (HIV, Transplant)": [
        "immune", "immunosuppressed", "immunocompromised", "immunodeficiency", # Added synonym
        "hiv", "aids", "transplant", "chemotherapy", "biologics", "steroid therapy" # Added common causes
        ],
    "None of the above": []
 }

# Duration - Seems good, adding related KB terms
DURATION_KEYWORDS = {
    "Less than 1 week": ["acute", "abrupt", "sudden", "days", "<1 week", "<6 weeks"], # Added <6wks for acute urticaria
    "1-4 weeks": ["acute", "subacute", "weeks", "1-4 weeks", "days-weeks"], # Added from KB timing
    "1-3 months": ["subacute", "months", "1-3 months", "~3 months"], # Added common timeframe for TE
    "3-6 months": ["subacute", "chronic", "persistent", "months", "3-6 months", ">6mo"], # Added >6mo overlap
    "6 months - 1 year": ["chronic", "persistent", "long", "6-12 months", ">6 months"],
    "More than 1 year": ["chronic", "persistent", "long", "years", ">1 year"],
    "Unsure": ["variable", "recurrent", "relapsing"] # Map unsure/variable/recurrent nature here
 }

# Location - Expanded based on KB specificity
LOCATION_KEYWORDS = {
    "Face": [
        "face", "facial", "periorificial", "perioral", "perinasal", "periocular", # Periorificial group
        "malar", "cheek", "forehead", "lip", "vermilion", "chin", "eyelid", "nose", # Specific areas
        "submental", "retroauricular", "periorbital", "glabella", "temples", "mandible", # More specifics
        "central face", "beard area", "nasolabial fold" # Common descriptive areas
        ],
    "Scalp": [
        "scalp", "nuchae", "occipital", "posterior neck", "nape", "hairline", "vertex", "crown", # Added crown
        "frontal hairline", "temporal recession" # AGA patterns
        ],
    "Eyelids": [
        "eyelid", "periocular", "periorbital", "helitrope" # Added heliotrope area
        ],
    "Ears": [
        "ear", "auricular", "retroauricular", "earlobe" # Added earlobe (spared in RP)
        ],
    "Neck": [
        "neck", "nape", "nuchae", "posterior neck" # Seems complete
        ],
    "Chest": [
        "chest", "trunk", "upper trunk", "sternal", "inframammary", # Added inframammary
        "sun-protected", "sun-exposed" # Added exposure status
        ],
    "Back": [
        "back", "trunk", "upper trunk", "interscapular", "sacrum", "lumbar",
        "sun-protected", "sun-exposed" # Added exposure status
        ],
    "Abdomen": [
        "abdomen", "abdominal", "trunk", "umbilical", "periumbilical",
        "sun-protected", "sun-exposed" # Added exposure status
        ],
    "Arms": [
        "arm", "limb", "extremity", "upper limb", "extensor", "flexor", "antecubital", # Added flexor/antecubital
        "forearm", "shoulder", "upper outer arm" # Added shoulder, specific KP site
        ],
    "Hands/Fingers": [
        "hand", "finger", "palm", "palmar", "dorsal hand", "knuckle", "gottron", # Added gottron area
        "acral", "digit", "digital", "periungual", "subungual", "nail fold", "cuticle" # Added nail structures
        ],
    "Legs": [
        "leg", "limb", "extremity", "lower limb", "extensor", "flexor", "popliteal", # Added flexor/popliteal
        "shin", "anterior leg", "pretibial", "calf", "posterior leg", "thigh", "knee" # Added anterior/posterior/pretibial
        ],
    "Feet/Toes": [
        "foot", "feet", "toe", "sole", "plantar", "dorsal foot", "ankle",
        "acral", "digit", "digital", "periungual", "subungual", "nail fold", "cuticle", # Added nail structures
        "interdigital", "web space", "toe web" # Added synonyms
        ],
    "Groin": [
        "groin", "inguinal", "fold", "intertriginous", "sun-protected" # Seems complete
        ],
    "Genitals": [
        "genital", "anogenital", "perianal", "penis", "scrotum", "vulva", "pubic" # Seems complete
        ],
    "Buttocks": [
        "buttock", "gluteal", "fold", "intertriginous", "sacrum", "gluteal cleft", # Added cleft
        "sun-protected" # Seems complete
        ],
    "Underarms (Axillae)": [
        "axilla", "axillae", "underarm", "fold", "intertriginous", "sun-protected" # Seems complete
        ],
    "Skin folds (general)": [
        "fold", "flexural", "intertriginous", "antecubital", "popliteal",
        "inframammary", "gluteal cleft", "sun-protected" # Seems complete
        ],
    "Inside Mouth/Nose": [
        "oral", "mouth", "mucosa", "mucosal", "mucous membrane", # Added synonym
        "buccal", "gingiva", "gingival", "tongue", "palate", "pharyngeal", # Added gingival
        "nasal", "nose", "vermilion" # Added vermilion border
        ],
    "All Over": [
        "widespread", "generalized", "diffuse", "trunk", "limbs", "extremities",
        "body", "systemic", "universal", "scattered", "disseminated", "multifocal" # Added synonyms from patterns
        ],
    "Other: _________": [],
    "None of the above": []
 }

# Morphology - Expanded significantly
MORPHOLOGY_KEYWORDS = {
    "Flat spots (discolored, not raised)": [
        "macule", "patch", "flat", "discolored", "spot", "mark", # Added spot, mark
        "erythema", "purpura", "ecchymotic", "petechiae", "bruise-like", # Color changes flat
        "hypopigmented", "hyperpigmented", "depigmented", "achromic", "white", # Pigment loss flat
        "brown", "blue", "grey", "tan", "yellowish", "cafe-au-lait", "ashy", # Other colors flat
        "lentigo", "ephelid", "freckle", "livedo", # Specific flat lesion types
        "wickham's striae" # Flat white lines in LP
        ],
    "Raised bumps (solid)": [
        "papule", "nodule", "plaque", "raised", "bump", "thickened", # General raised terms
        "indurated", "firm", "hard", "soft", "doughy", "lobulated", # Texture/consistency
        "dome-shaped", "polygonal", "planar", "flat-topped", "exophytic", # Shape
        "fleshy", "pedunculated", "stalked", "fibroma", "neurofibroma", # Specific types
        "vegetation", "papillomatous", "polypoid", # Surface texture related
        "wheal", # Urticaria lesion
        "horn", "keratosis", "hyperkeratotic", # Keratin related bumps
        "xanthoma", "granuloma", "angioma", "hemangioma", # Specific lesion types
        "comedo", "comedone" # Specific acne lesion
        ],
    "Blisters (clear fluid-filled)": [
        "blister", "vesicle", "bulla", "bullae", "fluid-filled", "clear fluid",
        "flaccid", "tense", "vesiculopustule", # Added types and mixed
        "lymphangioma", "frog spawn" # Specific vesicular appearance
        ],
    "Pustules (pus-filled bumps)": [
        "pustule", "pus", "pus-filled", "pimple", "follicular pustule",
        "abscess", "suppurative", "fluctuant", "boil", "furuncle", "carbuncle",
        "pyoderma", "pyogenic", # Pus related terms
        "vesiculopustule", "sterile pustule" # Added mixed/specific types
        ],
    "Thickened/Leathery skin": [
        "thickened", "leathery", "lichenified", "indurated", "plaque",
        "sclerosis", "hardness", "fibrosis", "scar-like", "hyperkeratotic" # Added related terms
        ],
    "Flaky/Scaly skin": [
        "flaky", "scale", "scaling", "scaly", "hyperkeratotic", "keratotic",
        "desquamation", "peeling", # Added peeling
        "eczema-like", "psoriasis-like", "psoriasiform", # Descriptive terms
        "ichthyosis", "ichthyosiform", "xerosis", "dry", # Dry/scaling conditions
        "corn flake scale", "collarette of scale" # Specific scale types
        ],
    "Crusts/Scabs": [
        "crust", "scab", "honey-colored crust", "serous crust", "hemorrhagic crust" # Added types
        ],
    "Ulcer / Open sore": [
        "ulcer", "erosion", "sore", "open sore", "denuded", "excoriation", # Added excoriation
        "punched-out", "crater", "fissure", # Added related breakdown terms
        "eschar", "necrotic", "gangrene", # Necrosis related
        "chancre", "aphthae" # Specific ulcer types
        ],
    "Circular or Ring-shaped": [
        "circular", "ring", "annular", "coin-shaped", "nummular", "discoid", # Added discoid
        "targetoid", "iris lesion", "bulls-eye", # Target shapes
        "arcuate", "polycyclic", "serpiginous", # Other shapes (serpiginous could be linear too)
        "round", "oval" # Simple shapes
        ],
    "Linear (in a line)": [
        "linear", "line", "streak", "band", "striated", # Added striated
        "dermatomal", "zosteriform", "koebner", "blaschko", # Specific patterns
        "serpiginous", "track" # Migrating line
        ],
    "Bruise-like / Purple discoloration": [
        "bruise", "bruise-like", "purple", "violaceous", "purpura", "palpable purpura", # Added palpable
        "ecchymosis", "ecchymotic", "petechiae", "hemorrhagic", # Bleeding related colors
        "dusky", "cyanotic", "livedo", "reticular", # Vascular pattern colors
        "poikiloderma" # Mixed atrophy, pigment, telangiectasia
        ],
    "Wart-like": [
        "wart-like", "verrucous", "papillomatous", "cauliflower", "hyperkeratotic" # Overlap with flaky/scaly & raised bump
        ],
    "Other: _________": [],
    "None of the above": []
 }

# Systemic Symptoms - Enhanced
SYSTEMIC_SYMPTOMS_KEYWORDS = {
    "Fever / Chills": [
        "fever", "febrile", "chill", "pyrexia", "systemic symptom", "malaise",
        "flu-like", "prodrome", "hypothermia" # Added hypothermia (severe sepsis)
        ],
    "Unexplained Weight Loss (>10 lbs)": [
        "weight loss", "b symptom", "cachexia" # Added cachexia
        ],
    "Unusual Fatigue / Tiredness": [
        "tired", "fatigue", "malaise", "systemic symptom", "lassitude", "lethargy" # Added synonyms
        ],
    "Night Sweats": [
        "night sweats", "b symptom" # Seems complete
        ],
    "Joint Pain / Swelling": [
        "joint", "arthralgia", "arthritis", "arthropathy", "polyarthritis", "monoarthritis" # Added types
        ],
    "Muscle Aches": [
        "muscle ache", "myalgia", "muscle weakness", "myopathy", "myositis" # Added weakness/inflammation
        ],
    "Swollen Glands/Lymph Nodes (Neck/Armpits/Groin)": [
        "lump", "swollen", "lymphadenopathy", "adenopathy", "node", "gland", "lymph node",
        "bubo", "hilar lymphadenopathy" # Added hilar for Sarcoid
        ],
    "Sores in mouth or genital area": [
        "sore", "ulcer", "erosion", "oral", "genital", "mucosal", "aphthae", "stomatitis", # Added aphthae/stomatitis
        "gingivitis", "conjunctivitis", "uveitis", "ocular" # Added other mucosal sites
        ],
    "Changes in hair or nails": [
        "hair loss", "alopecia", "shedding", "effluvium", "hirsutism", "hypertrichosis", # Added shedding/excess hair
        "nail change", "onychodystrophy", "pitting", "ridging", "onycholysis", # Added onycholysis
        "clubbing", "pterygium", "splinter hemorrhage", "beau lines" # Added specific nail signs
        ],
    "None": ["asymptomatic"] # Added asymptomatic here
 }

# Triggers - Expanded based on KB examples
TRIGGER_KEYWORDS = {
    "Sunlight Exposure": ["sun", "photo", "light", "actinic", "uv", "sunlight", "phototoxic", "photoallergic"], # Added types
    "Heat / Sweating": ["heat", "sweat", "hot", "exercise", "occlusion"], # Added exercise/occlusion
    "Cold / Dry Air": ["cold", "dry air", "winter", "low humidity"],
    "Stress": ["stress", "emotional"],
    "Scratching / Rubbing": [
        "scratch", "rub", "friction", "koebner", "koebnerization", "excoriation", # Added synonyms
        "trauma", "injury", "pressure", "mechanical", "pathergy" # Added pathergy
        ],
    "Water (bathing, swimming)": ["water", "bathing", "swimming", "wet work", "aquatic", "seawater"], # Added aquatic/seawater
    "New soaps/lotions/detergents/cosmetics": [
        "contact", "allergen", "irritant", "soap", "cosmetic", "lotion", "preservative", # Added preservative
        "fragrance", "detergent", "dye", "product", "topical", "shampoo", "hair dye" # Added specifics
        ],
    "Contact with chemicals/metals": [
        "chemical", "metal", "nickel", "chromate", "rubber", "latex", # Added specifics
        "contact", "allergen", "irritant", "exposure", "halogenated hydrocarbon", # Added specific chem type
        "occupational", "solvent" # Added solvent
        ],
    "Specific Foods: _________": [
        "food", "ingestion", "diet", "gluten", "seafood" # Added examples
        ],
    "Specific Medications: _________": [
        "drug", "medication", "systemic", "topical", # Added routes
        "steroid", "corticosteroid", "antibiotic", "lithium", "egfri", "ace inhibitor", # Specific drug classes/examples from KB
        "anticonvulsant", "thiazide", "vaccine", "chemotherapy", "vancomycin", # More examples
        "nsaid", "protein", "serum" # Other substances
        ],
    "Hormonal changes (e.g., menstrual cycle)": [
        "hormone", "hormonal", "menstrual", "pregnancy", "postpartum", "ocp", "oral contraceptive", # Added synonyms
        "puberty", "postmenopausal", "estrogen" # Added life stages/specific hormone
        ],
    "Nothing specific noticed": ["idiopathic", "spontaneous", "unknown"], # Added related terms
    "Other: _________": [
        "infection", "strep", "viral", "bacterial", # Infections as triggers
        "insect bite", "tick bite", "animal contact", "cat", "sheep", "goat", "cattle", # Bites/Animal contact
        "plant", "poison ivy", "poison oak", "sumac", "furocoumarin", # Plant triggers
        "tattoo", "vaccination" # Procedure triggers
        ],
    "None of the above": []
 }

# Spread Pattern - Seems reasonable, refined based on KB terms
SPREAD_PATTERN_KEYWORDS = {
    "Outward from one spot": [
        "outward", "annular", "expanding", "central clearing", "peripheral", "centrifugal",
        "target", "radial growth" # Added target, radial growth (melanoma)
        ],
    "In a straight line/band": [
        "linear", "line", "band", "streak", "striated", # Added striated
        "dermatomal", "zosteriform", "sporotrichoid", "lymphatic spread", # Added lymphatic
        "koebner", "blaschko" # Patterns following lines
        ],
    "Same on both sides": [
        "symmetric", "bilateral" # Seems complete
        ],
    "Only one side": [
        "unilateral", "asymmetric", "dermatomal", "one side", "segmental" # Added segmental (vitiligo/PWS)
        ],
    "Random spots": [
        "scattered", "random", "multiple", "disseminated", "multifocal", "crops", # Existing seem good
        "irregular", "asymmetric", "grouped", "clustered", "satellite", # Added clustered, satellite
        "moth-eaten" # Specific pattern (syphilis alopecia)
        ],
    "Not spreading / Stable": [
        "stable", "not spreading", "static", "localized", "solitary", "fixed" # Added localized/solitary/fixed (FDE)
        ]
}

# Age mapping - Expanded with KB terms
AGE_KEYWORDS = {
    "Under 10": [
        "child", "infant", "infancy", "juvenile", "pediatric", "neonate", "neonatal",
        "<2 years", "<5", "<6 weeks", "age 3-14", "toddler" # Added toddler
        ],
    "10-18": [
        "adolescent", "teen", "young", "juvenile", "pediatric", "child", "age 3-14", # Seems reasonable
        "puberty" # Added life stage
        ],
    "19-30": ["young adult", "young", "adult"],
    "31-45": ["adult", "middle-aged"],
    "46-65": ["middle-aged", "adult", "older", ">50", "postmenopausal"], # Added postmenopausal overlap
    "65+": ["elderly", "older adult", "age", ">50"],
    "Prefer not to say": []
}

# Gender mapping - Looks good, added pregnancy terms
GENDER_KEYWORDS = {
    "Male": ["male", "man", "men"],
    "Female": ["female", "woman", "women", "postmenopausal", "pregnancy", "pregnant", "postpartum", "gestationis"], # Added pregnant, gestationis
    "Prefer not to say": []
}

# Weights and Specific Bonus Map are kept as adjusted by you.
WEIGHT_SYMPTOM = 1.0
WEIGHT_LOCATION = 2.5
WEIGHT_MORPHOLOGY = 3.5
WEIGHT_SYSTEMIC = 3.5
WEIGHT_TRIGGER = 1.0
WEIGHT_SPREAD_PATTERN = 2.0
WEIGHT_CONDITION = 1.5
WEIGHT_DURATION = 3.0
WEIGHT_AGE = 1.0
WEIGHT_GENDER = 1.0
BONUS_HISTORY_NAME_MATCH = 1.0
BONUS_SPECIFIC_KEYWORD = 4.0

SPECIFIC_KEYWORD_BONUS_MAP = {
    "comedones": ("morphology", "Pustules (pus-filled bumps)", BONUS_SPECIFIC_KEYWORD), # Note: Comedones aren't pustules, maybe map to 'Raised bumps'? Revisit this mapping logic.
    "honey-colored crust": ("morphology", "Crusts/Scabs", BONUS_SPECIFIC_KEYWORD),
    "pearly": ("morphology", "Raised bumps (solid)", BONUS_SPECIFIC_KEYWORD),
    "telangiectasias": ("morphology", "Bruise-like / Purple discoloration", BONUS_SPECIFIC_KEYWORD * 0.5), # Telangiectasias are dilated vessels, not really bruises. Maybe map to 'Redness'? Revisit.
    "sandpaper": ("morphology", "Flaky/Scaly skin", BONUS_SPECIFIC_KEYWORD),
    "burrow": ("morphology", "Linear (in a line)", BONUS_SPECIFIC_KEYWORD*1.5),
    "targetoid": ("morphology", "Circular or Ring-shaped", BONUS_SPECIFIC_KEYWORD),
    "annular scaly border": ("morphology", "Circular or Ring-shaped", BONUS_SPECIFIC_KEYWORD), # Maybe better as "annular" AND "scaly"? Requires more complex logic.
    "satellite lesions": ("morphology", "Pustules (pus-filled bumps)", BONUS_SPECIFIC_KEYWORD), # Lesions could be papules too
    "satellite papules": ("morphology", "Raised bumps (solid)", BONUS_SPECIFIC_KEYWORD),
    "umbilicated": ("morphology", "Raised bumps (solid)", BONUS_SPECIFIC_KEYWORD*1.5),
    "dermatomal": ("spread_pattern", "In a straight line/band", BONUS_SPECIFIC_KEYWORD),
    "koplik spots": ("location", "Inside Mouth/Nose", BONUS_SPECIFIC_KEYWORD*2.0),
    "wickham's striae": ("morphology", "Flat spots (discolored, not raised)", BONUS_SPECIFIC_KEYWORD*1.5),
    "apple jelly": ("morphology", "Raised bumps (solid)", BONUS_SPECIFIC_KEYWORD*1.5),
    "heliotrope": ("location", "Eyelids", BONUS_SPECIFIC_KEYWORD*1.5), # Could also be morphology 'Bruise-like/Purple discoloration'
    "gottron": ("location", "Hands/Fingers", BONUS_SPECIFIC_KEYWORD*1.5), # Could also be morphology 'Raised bumps' or 'Purple discoloration'
    "sun-protected": ("location", "Chest", 3.0),
    "sun-protected": ("location", "Back", 3.0),
    "sun-protected": ("location", "Abdomen", 3.0),
    "sun-protected": ("location", "Buttocks", 3.0),
    "poikiloderma": ("morphology", "Bruise-like / Purple discoloration", 2.5),
    "chronic": ("duration", "More than 1 year", 1.5),
    "persistent": ("duration", "More than 1 year", 1.5),
    "lymphadenopathy": ("systemic_symptoms", "Swollen Glands/Lymph Nodes (Neck/Armpits/Groin)", 2.0),
    "weight loss": ("systemic_symptoms", "Unexplained Weight Loss (>10 lbs)", 2.0),

    # --- SUGGESTIONS FOR REVISITING SPECIFIC KEYWORD BONUS MAP ---
    # "comedones": Consider mapping to 'Raised bumps' or creating a specific 'Acne Lesions' category if needed. It's not a pustule.
    # "telangiectasias": Map to 'Redness' might be more accurate than 'Bruise-like'. Bonus weight seems low if it's a key feature (e.g., Rosacea ETR, BCC).
    # "annular scaly border": This needs AND logic ideally. As is, matching 'Circular or Ring-shaped' is okay but loses the 'scaly border' info which is key for Tinea.
    # "satellite lesions": This is vague. Could be papules or pustules. Need separate entries or map to a general 'spots' morphology?
    # "heliotrope"/"gottron": These are location *and* morphology. Current mapping is okay but maybe add morphology links too?
}

# --- Functions (parse_knowledge_base, get_user_input, calculate_scores) ---
# PASTE THE FUNCTIONS FROM THE PREVIOUS VERSION HERE - they don't need internal changes
# based on these weight/keyword adjustments. Ensure the calculate_scores uses the new weights.
def parse_knowledge_base(text):
    """Parses the raw text into a list of condition dictionaries."""
    # (Code is identical to the previous version)
    conditions = []
    pattern = re.compile(r"\[Condition:\s*(.*?)\]\n(.*?)(?=\n\s*\[Condition:|\Z)", re.DOTALL | re.IGNORECASE)
    category_pattern = re.compile(r"^\s*(\d+)\.\s+(.*?)\s*$", re.MULTILINE)

    categories = {match.group(1): match.group(2).strip() for match in category_pattern.finditer(text)}
    category_positions = {match.start(): match.group(1) for match in category_pattern.finditer(text)}
    sorted_cat_positions = sorted(category_positions.keys())

    current_category_num = None

    for match in pattern.finditer(text):
        condition_name = match.group(1).strip()
        details_text = match.group(2).strip()
        condition_start_pos = match.start()

        # Determine category based on position
        determined_category = "Unknown" # Default
        for i, pos in enumerate(sorted_cat_positions):
            next_pos_index = i + 1
            next_pos = sorted_cat_positions[next_pos_index] if next_pos_index < len(sorted_cat_positions) else float('inf')
            if pos <= condition_start_pos < next_pos:
                determined_category_num = category_positions[pos]
                determined_category = categories.get(determined_category_num, "Unknown")
                break


        red_flags = []
        rule = ""
        ddx = []
        flags_raw_text = ""

        lines = details_text.split('\n')
        in_flags_section = False
        flags_buffer = "" # Buffer to collect flag text across lines

        for line in lines:
            stripped_line = line.strip()
            line_lower = stripped_line.lower()

            if line_lower.startswith("- red flags:"):
                in_flags_section = True
                # Start collecting flags, handle text after colon on the same line
                try:
                    flags_buffer += line.split(":", 1)[1].strip() + " "
                except IndexError:
                    pass # No text after colon on this line
                continue # Move to the next line

            # Check for end markers BEFORE processing potential flag lines
            if line_lower.startswith("- rule:") or line_lower.startswith("- ddx:"):
                in_flags_section = False # Stop collecting flags
                # Process rule or ddx AFTER flags section ends
                if line_lower.startswith("- rule:"):
                     try:
                         rule = stripped_line.split(":", 1)[1].strip()
                     except IndexError:
                         rule = "" # Handle empty rule
                elif line_lower.startswith("- ddx:"):
                     try:
                         ddx_str = stripped_line.split(":", 1)[1].strip()
                         ddx = [d.strip() for d in ddx_str.split(',') if d.strip()]
                     except IndexError:
                         ddx_str = ""
                         ddx = []
                continue # Move to next line after processing rule/ddx start

            # If we are still in the flags section, append the line content
            if in_flags_section and stripped_line:
                 # Append the content, remove leading hyphens if present
                 flag_content = stripped_line[1:].strip() if stripped_line.startswith('-') else stripped_line
                 flags_buffer += flag_content + " "

        # Assign the collected buffer to flags_raw_text after the loop
        flags_raw_text = flags_buffer.strip()

        # Process flags_raw_text into a list
        potential_flags = re.split(r'[,\n|]', flags_raw_text) # Split by comma, newline, or pipe
        processed_flags = set()
        for flag in potential_flags:
             cleaned_flag = flag.strip()
             # Basic cleanup of leading/trailing brackets/parentheses etc.
             cleaned_flag = re.sub(r"^[\[\(']*(.*?)[\]\)']*\s*$", r"\1", cleaned_flag).strip()
             if cleaned_flag:
                 processed_flags.add(cleaned_flag)


        conditions.append({
            "name": condition_name,
            "category": determined_category, # Use determined category
            "red_flags_list": list(processed_flags),
            "red_flags_text": " | ".join(processed_flags).lower(), # Join with pipes for text matching
            "num_flags": len(processed_flags),
            "rule": rule,
            "ddx": ddx
        })

    if not conditions:
         print("Warning: No conditions parsed. Check knowledge base format and content.")

    return conditions

 
# Removed get_user_input function as input will come from API request
def calculate_scores(patient_input, conditions_db):
    """Calculates scores using adjusted weights and general specific keyword bonuses."""
    print("\n--- [calculate_scores] START ---") # Log start
    print(f"Received patient_input: {patient_input}") # Log the full input

    scores = collections.defaultdict(float)
    debug_scores = collections.defaultdict(lambda: collections.defaultdict(float)) # For debugging

    # --- Prepare keyword sets (Handle single vs multiple choice inputs) ---
    def get_keywords(input_key, keyword_dict, is_multiple, exclusive_options):
        # (Keep the inner workings of get_keywords the same for now)
        # ... existing get_keywords code ...
        kws = set() # Placeholder - Replace with your actual get_keywords logic return
        user_data = patient_input.get(input_key)
        if not user_data: return kws

        options_to_process = []
        if is_multiple:
            if isinstance(user_data, list): options_to_process = user_data
            else: return kws # Error or unexpected type
        else:
            if isinstance(user_data, str): options_to_process = [user_data]
            else: return kws # Error or unexpected type

        is_exclusive_selected = False
        # Simplified exclusive check for logging demo
        for opt in options_to_process:
             if any(ex_phrase in opt.lower() for ex_phrase in exclusive_options if ex_phrase != "other:") or \
                ("other:" in exclusive_options and opt.lower().startswith("other:")) :
                 is_exclusive_selected = True
                 break

        if not is_exclusive_selected:
            for option in options_to_process:
                option_lower = option.lower()
                matched_key = None
                for key_option in keyword_dict.keys():
                    # Use lower() for case-insensitive key matching
                    if key_option.lower() == option_lower:
                        matched_key = key_option
                        break
                if matched_key:
                    kws.update(keyword_dict[matched_key])
                # else: # Optional: Log if an option wasn't found in the dictionary
                #     print(f"--- DEBUG: Option '{option}' for key '{input_key}' not found in keyword_dict keys.")
        return kws


    # Define common exclusive phrases based on updated options
    exclusive_phrases = {"none of the above", "nothing specific", "prefer not to say", "not sure", "not spreading", "unsure", "other:", "none"}

    # --- CORRECTED KEYS based on QuestionSet.js ---
    symptom_kws = get_keywords("symptoms", SYMPTOM_KEYWORDS, True, exclusive_phrases)
    location_kws = get_keywords("location", LOCATION_KEYWORDS, True, exclusive_phrases)
    morphology_kws = get_keywords("appearance", MORPHOLOGY_KEYWORDS, True, exclusive_phrases) # Use 'appearance'
    systemic_kws = get_keywords("general_symptoms", SYSTEMIC_SYMPTOMS_KEYWORDS, True, exclusive_phrases) # Use 'general_symptoms'
    trigger_kws = get_keywords("triggers", TRIGGER_KEYWORDS, True, exclusive_phrases)
    med_cond_kws = get_keywords("past_diagnoses", CONDITION_KEYWORDS, True, exclusive_phrases) # Use 'past_diagnoses'

    spread_pattern_kws = get_keywords("spread_arrangement", SPREAD_PATTERN_KEYWORDS, False, exclusive_phrases) # Use 'spread_arrangement'
    duration_kws = get_keywords("condition_duration", DURATION_KEYWORDS, False, exclusive_phrases) # Use 'condition_duration'
    age_kws = get_keywords("age_range", AGE_KEYWORDS, False, exclusive_phrases)
    gender_kws = get_keywords("gender", GENDER_KEYWORDS, False, exclusive_phrases)

    # --- Log Extracted Keywords ---
    print(f"\n--- DEBUG: Extracted Keyword Sets ---")
    print(f"Symptoms ({len(symptom_kws)}): {symptom_kws}")
    print(f"Location ({len(location_kws)}): {location_kws}")
    print(f"Morphology ({len(morphology_kws)}): {morphology_kws}")
    print(f"Systemic ({len(systemic_kws)}): {systemic_kws}")
    print(f"Trigger ({len(trigger_kws)}): {trigger_kws}")
    print(f"Med Cond ({len(med_cond_kws)}): {med_cond_kws}")
    print(f"Spread Pattern ({len(spread_pattern_kws)}): {spread_pattern_kws}")
    print(f"Duration ({len(duration_kws)}): {duration_kws}")
    print(f"Age ({len(age_kws)}): {age_kws}")
    print(f"Gender ({len(gender_kws)}): {gender_kws}")
    print("-" * 30)


    # Special handling for medical condition names for bonus (Corrected Key)
    patient_med_cond_names = set()
    med_cond_input = patient_input.get("past_diagnoses") # Use 'past_diagnoses'
    if isinstance(med_cond_input, list):
         is_exclusive_selected = False
         for mc in med_cond_input:
              mc_lower = mc.lower()
              for exclusive_phrase in exclusive_phrases:
                   if (exclusive_phrase == "other:" and mc_lower.startswith(exclusive_phrase)) or \
                      (exclusive_phrase != "other:" and exclusive_phrase in mc_lower):
                        is_exclusive_selected = True
                        break
              if is_exclusive_selected: break
         if not is_exclusive_selected:
              for cond_name in med_cond_input:
                   patient_med_cond_names.add(cond_name.lower()) # Add the full name as reported
    print(f"--- DEBUG: Patient Reported Med Cond Names: {patient_med_cond_names}")


    # --- Score each condition ---
    print(f"\n--- DEBUG: Scoring Conditions ({len(conditions_db)} total) ---")
    for condition in conditions_db: # Limit logging to first 10 conditions for brevity
        name = condition["name"]
        flags_text = condition["red_flags_text"]
        current_score = 0.0
        matched_keywords_details = []

        # --- Standard Keyword Scoring ---
        keyword_sets_and_weights = [
            (symptom_kws, WEIGHT_SYMPTOM, "Symptom"),
            (location_kws, WEIGHT_LOCATION, "Location"),
            (morphology_kws, WEIGHT_MORPHOLOGY, "Morphology"),
            (systemic_kws, WEIGHT_SYSTEMIC, "Systemic"),
            (trigger_kws, WEIGHT_TRIGGER, "Trigger"),
            (spread_pattern_kws, WEIGHT_SPREAD_PATTERN, "Spread"),
            (med_cond_kws, WEIGHT_CONDITION, "MedCond"),
            (duration_kws, WEIGHT_DURATION, "Duration"),
            (age_kws, WEIGHT_AGE, "Age"),
            (gender_kws, WEIGHT_GENDER, "Gender")
        ]

        print(f"\n--- DEBUG: Scoring Condition: {name} ---")
        # print(f"Flags Text (Snippet): {flags_text[:150]}...") # Optional: uncomment to see flags text

        for kw_set, weight, category_tag in keyword_sets_and_weights:
             category_score = 0
             if kw_set:
                 for kw in kw_set:
                     pattern = r'\b' + re.escape(kw) + r'\b'
                     if re.search(pattern, flags_text, re.IGNORECASE):
                         # --- Log successful match ---
                         print(f"    MATCH! Keyword: '{kw}' (Category: {category_tag}, Weight: +{weight:.1f})")
                         score_increase = weight
                         current_score += score_increase
                         category_score += score_increase
                         matched_keywords_details.append(f"+{score_increase:.1f} ({category_tag}: {kw})")

             if category_score > 0:
                  debug_scores[name][category_tag] += category_score


        # --- Apply Bonuses ---
        # (Keep bonus logic, add logging if needed later)
        # ... existing bonus code ...
        history_bonus_applied = False
        if patient_med_cond_names:
            condition_name_lower = name.lower()
            for reported_cond_name in patient_med_cond_names:
                 # Use 'in' for substring matching, might need refinement
                 if reported_cond_name in condition_name_lower or condition_name_lower in reported_cond_name:
                       print(f"    BONUS! History Match: +{BONUS_HISTORY_NAME_MATCH:.1f} for '{reported_cond_name}'")
                       current_score += BONUS_HISTORY_NAME_MATCH
                       debug_scores[name]["Bonus_History"] += BONUS_HISTORY_NAME_MATCH
                       matched_keywords_details.append(f"+{BONUS_HISTORY_NAME_MATCH:.1f} (Bonus_History: {reported_cond_name})")
                       history_bonus_applied = True
                       break # Apply bonus once

        bonus_score = 0.0
        for specific_kw, (input_cat_key, req_input_opt, bonus_val) in SPECIFIC_KEYWORD_BONUS_MAP.items():
             pattern = r'\b' + re.escape(specific_kw) + r'\b'
             if re.search(pattern, flags_text, re.IGNORECASE):
                user_category_input = patient_input.get(input_cat_key) # Use correct key here
                user_selected_relevant_option = False
                if isinstance(user_category_input, list):
                    if any(req_input_opt.lower() == user_opt.lower() for user_opt in user_category_input):
                        user_selected_relevant_option = True
                elif isinstance(user_category_input, str):
                    if req_input_opt.lower() == user_category_input.lower():
                        user_selected_relevant_option = True

                if user_selected_relevant_option:
                    print(f"    BONUS! Specific Keyword: +{bonus_val:.1f} for '{specific_kw}' matching '{req_input_opt}'")
                    bonus_score += bonus_val
                    debug_scores[name][f"Bonus_{specific_kw}"] += bonus_val
                    matched_keywords_details.append(f"+{bonus_val:.1f} (Bonus_{specific_kw} for {req_input_opt})")


        final_score = current_score + bonus_score

        if final_score > 0:
             scores[name] = final_score
             print(f"--- DEBUG: Final Score for {name}: {final_score:.1f} ---")
        # else: # Optional log for zero scores
        #      print(f"--- DEBUG: Zero score for {name} ---")

    print("\n--- [calculate_scores] END ---") # Log end

    # Sort by score descending
    sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return sorted_scores
# --- Main Execution ---

# --- Flask App Setup ---
app = Flask(__name__)
# Enable CORS for all routes and all origins
CORS(app, resources={r"/*": {"origins": "*"}})

# --- Load Knowledge Base Once ---
conditions_database = []
def load_knowledge():
    global conditions_database
    print("\nParsing Knowledge Base...")
    if not knowledge_base_text or len(knowledge_base_text) < 500:
        print("\nError: 'knowledge_base_text' appears to be empty or incomplete.")
        # In a real app, might raise an exception or handle differently
        return False
    conditions_database = parse_knowledge_base(knowledge_base_text)
    if not conditions_database:
         print("\nError: Could not load or parse condition data.")
         return False
    else:
        print(f"Successfully parsed {len(conditions_database)} conditions.")
        return True

knowledge_loaded = load_knowledge()

# --- API Endpoints ---
@app.route('/suggest_conditions', methods=['POST'])
def suggest_conditions():
    if not knowledge_loaded:
        return jsonify({"error": "Knowledge base not loaded. Check server logs."}), 500

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    patient_answers = request.get_json()
    if not patient_answers:
        return jsonify({"error": "No patient answers provided in JSON body"}), 400

    print(f"Received patient answers: {patient_answers}") # Log received data

    try:
        results = calculate_scores(patient_answers, conditions_database)

        response_data = []
        for condition_name, score in results:
             condition_entry = next((c for c in conditions_database if c['name'] == condition_name), None)
             category = condition_entry['category'] if condition_entry else "Unknown"
             response_data.append({
                 "condition": condition_name,
                 "score": round(score, 1),
                 "category": category
             })

        print(f"Sending results: {response_data[:5]}...") # Log first few results
        return jsonify({"suggestions": response_data})

    except Exception as e:
        print(f"Error during score calculation: {e}")
        # Consider more specific error logging/handling
        return jsonify({"error": f"An internal error occurred: {str(e)}"}), 500

@app.route('/health_kb', methods=['GET'])
def health_check_kb():
    """Simple endpoint to check if the KB server is running and KB is loaded"""
    status = "ok" if knowledge_loaded else "knowledge base not loaded"
    return jsonify({
        "status": status,
        "conditions_loaded": len(conditions_database) if knowledge_loaded else 0
    })


# --- Main Execution (for Flask Server) --- # (You can rename the comment)
if __name__ == "__main__":
    if not knowledge_loaded:
        print("CRITICAL ERROR: Knowledge base failed to load. Server cannot start properly.")
        # sys.exit(1) # Optional: uncomment to stop server if KB fails
    print("Starting Flask KB Suggestion API server...")
    # Run on port 5002
    app.run(debug=True, host='0.0.0.0', port=5002)