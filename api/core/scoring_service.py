import re
import collections
from .config import Config
from .keywords import KeywordMappings

# --- Functions (parse_knowledge_base, get_user_input, calculate_scores) ---
# PASTE THE FUNCTIONS FROM THE PREVIOUS VERSION HERE - they don't need internal changes
# based on these weight/keyword adjustments. Ensure the calculate_scores uses the new weights.


class ScoringEngine:
    config: Config
    keyword_map: KeywordMappings

    def __init__(self, config, keyword_map):
        self.config = config
        self.keyword_map = keyword_map

    # Removed get_user_input function as input will come from API request
    def calculate_scores(self, patient_input, conditions_db):
        """Calculates scores using adjusted weights and general specific keyword bonuses."""
        print("\n--- [calculate_scores] START ---")  # Log start
        print(f"Received patient_input: {patient_input}")  # Log the full input

        scores = collections.defaultdict(float)
        debug_scores = collections.defaultdict(
            lambda: collections.defaultdict(float)
        )  # For debugging

        # --- Prepare keyword sets (Handle single vs multiple choice inputs) ---
        def get_keywords(input_key, keyword_dict, is_multiple, exclusive_options):
            # (Keep the inner workings of get_keywords the same for now)
            # ... existing get_keywords code ...
            kws = (
                set()
            )  # Placeholder - Replace with your actual get_keywords logic return
            user_data = patient_input.get(input_key)
            if not user_data:
                return kws

            options_to_process = []
            if is_multiple:
                if isinstance(user_data, list):
                    options_to_process = user_data
                else:
                    return kws  # Error or unexpected type
            else:
                if isinstance(user_data, str):
                    options_to_process = [user_data]
                else:
                    return kws  # Error or unexpected type

            is_exclusive_selected = False
            # Simplified exclusive check for logging demo
            for opt in options_to_process:
                if any(
                    ex_phrase in opt.lower()
                    for ex_phrase in exclusive_options
                    if ex_phrase != "other:"
                ) or (
                    "other:" in exclusive_options and opt.lower().startswith("other:")
                ):
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
        exclusive_phrases = {
            "none of the above",
            "nothing specific",
            "prefer not to say",
            "not sure",
            "not spreading",
            "unsure",
            "other:",
            "none",
        }

        # --- CORRECTED KEYS based on QuestionSet.js ---
        symptom_kws = get_keywords(
            "symptoms", self.keyword_map.symptom_keywords, True, exclusive_phrases
        )
        location_kws = get_keywords(
            "location", self.keyword_map.location_keywords, True, exclusive_phrases
        )
        morphology_kws = get_keywords(
            "appearance", self.keyword_map.morphology_keywords, True, exclusive_phrases
        )  # Use 'appearance'
        systemic_kws = get_keywords(
            "general_symptoms",
            self.keyword_map.systemic_symptons_keywords,
            True,
            exclusive_phrases,
        )  # Use 'general_symptoms'
        trigger_kws = get_keywords(
            "triggers", self.keyword_map.trigger_keywords, True, exclusive_phrases
        )
        med_cond_kws = get_keywords(
            "past_diagnoses",
            self.keyword_map.condition_keywords,
            True,
            exclusive_phrases,
        )  # Use 'past_diagnoses'

        spread_pattern_kws = get_keywords(
            "spread_arrangement",
            self.keyword_map.spread_pattern_keywords,
            False,
            exclusive_phrases,
        )  # Use 'spread_arrangement'
        duration_kws = get_keywords(
            "condition_duration",
            self.keyword_map.duration_keywords,
            False,
            exclusive_phrases,
        )  # Use 'condition_duration'
        age_kws = get_keywords(
            "age_range", self.keyword_map.age_keywords, False, exclusive_phrases
        )
        gender_kws = get_keywords(
            "gender", self.keyword_map.gender_keywords, False, exclusive_phrases
        )

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
        med_cond_input = patient_input.get("past_diagnoses")  # Use 'past_diagnoses'
        if isinstance(med_cond_input, list):
            is_exclusive_selected = False
            for mc in med_cond_input:
                mc_lower = mc.lower()
                for exclusive_phrase in exclusive_phrases:
                    if (
                        exclusive_phrase == "other:"
                        and mc_lower.startswith(exclusive_phrase)
                    ) or (
                        exclusive_phrase != "other:" and exclusive_phrase in mc_lower
                    ):
                        is_exclusive_selected = True
                        break
                if is_exclusive_selected:
                    break
            if not is_exclusive_selected:
                for cond_name in med_cond_input:
                    patient_med_cond_names.add(
                        cond_name.lower()
                    )  # Add the full name as reported
        print(f"--- DEBUG: Patient Reported Med Cond Names: {patient_med_cond_names}")

        # --- Score each condition ---
        print(f"\n--- DEBUG: Scoring Conditions ({len(conditions_db)} total) ---")
        for (
            condition
        ) in conditions_db:  # Limit logging to first 10 conditions for brevity
            print("1")
            print(condition)
            name = condition["name"]
            print("2")
            flags_text = condition["red_flags_text"]
            current_score = 0.0
            matched_keywords_details = []

            print("3")
            # --- Standard Keyword Scoring ---
            keyword_sets_and_weights = [
                (symptom_kws, self.config.WEIGHT_SYMPTOM, "Symptom"),
                (location_kws, self.config.WEIGHT_LOCATION, "Location"),
                (morphology_kws, self.config.WEIGHT_MORPHOLOGY, "Morphology"),
                (systemic_kws, self.config.WEIGHT_SYSTEMIC, "Systemic"),
                (trigger_kws, self.config.WEIGHT_TRIGGER, "Trigger"),
                (spread_pattern_kws, self.config.WEIGHT_SPREAD_PATTERN, "Spread"),
                (med_cond_kws, self.config.WEIGHT_CONDITION, "MedCond"),
                (duration_kws, self.config.WEIGHT_DURATION, "Duration"),
                (age_kws, self.config.WEIGHT_AGE, "Age"),
                (gender_kws, self.config.WEIGHT_GENDER, "Gender"),
            ]

            print(f"\n--- DEBUG: Scoring Condition: {name} ---")
            # print(f"Flags Text (Snippet): {flags_text[:150]}...") # Optional: uncomment to see flags text

            for kw_set, weight, category_tag in keyword_sets_and_weights:
                category_score = 0
                if kw_set:
                    for kw in kw_set:
                        pattern = r"\b" + re.escape(kw) + r"\b"
                        if re.search(pattern, flags_text, re.IGNORECASE):
                            # --- Log successful match ---
                            print(
                                f"    MATCH! Keyword: '{kw}' (Category: {category_tag}, Weight: +{weight:.1f})"
                            )
                            score_increase = weight
                            current_score += score_increase
                            category_score += score_increase
                            matched_keywords_details.append(
                                f"+{score_increase:.1f} ({category_tag}: {kw})"
                            )

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
                    if (
                        reported_cond_name in condition_name_lower
                        or condition_name_lower in reported_cond_name
                    ):
                        print(
                            f"    BONUS! History Match: +{self.config.BONUS_HISTORY_NAME_MATCH:.1f} for '{reported_cond_name}'"
                        )
                        current_score += self.config.BONUS_HISTORY_NAME_MATCH
                        debug_scores[name][
                            "Bonus_History"
                        ] += self.config.BONUS_HISTORY_NAME_MATCH
                        matched_keywords_details.append(
                            f"+{self.config.BONUS_HISTORY_NAME_MATCH:.1f} (Bonus_History: {reported_cond_name})"
                        )
                        history_bonus_applied = True
                        break  # Apply bonus once

            bonus_score = 0.0

            for specific_kw, (
                input_cat_key,
                req_input_opt,
                bonus_val,
            ) in self.keyword_map.specific_keyword_bonus_map.items():
                pattern = r"\b" + re.escape(specific_kw) + r"\b"
                if re.search(pattern, flags_text, re.IGNORECASE):
                    user_category_input = patient_input.get(
                        input_cat_key
                    )  # Use correct key here
                    user_selected_relevant_option = False
                    if isinstance(user_category_input, list):
                        if any(
                            req_input_opt.lower() == user_opt.lower()
                            for user_opt in user_category_input
                        ):
                            user_selected_relevant_option = True
                    elif isinstance(user_category_input, str):
                        if req_input_opt.lower() == user_category_input.lower():
                            user_selected_relevant_option = True

                    if user_selected_relevant_option:
                        print(
                            f"    BONUS! Specific Keyword: +{bonus_val:.1f} for '{specific_kw}' matching '{req_input_opt}'"
                        )
                        bonus_score += bonus_val
                        debug_scores[name][f"Bonus_{specific_kw}"] += bonus_val
                        matched_keywords_details.append(
                            f"+{bonus_val:.1f} (Bonus_{specific_kw} for {req_input_opt})"
                        )

            final_score = current_score + bonus_score

            if final_score > 0:
                scores[name] = final_score
                print(f"--- DEBUG: Final Score for {name}: {final_score:.1f} ---")
            # else: # Optional log for zero scores
            #      print(f"--- DEBUG: Zero score for {name} ---")

        print("\n--- [calculate_scores] END ---")  # Log end

        # Sort by score descending
        sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        return sorted_scores
