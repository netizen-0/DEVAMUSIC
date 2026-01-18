import os
from typing import List

import yaml

languages = {}
languages_present = {}


def get_string(lang: str):
    return languages[lang]


# ✅ FIXED: Use dynamic path instead of hardcoded relative path
STRINGS_DIR = os.path.join(os.path.dirname(__file__), "langs")

# ✅ Validate that strings directory exists
if not os.path.exists(STRINGS_DIR):
    raise SystemExit(
        f"[ERROR] Strings directory not found at {STRINGS_DIR}. "
        "Please ensure the 'strings/langs/' directory exists."
    )

# Load all language files
for filename in os.listdir(STRINGS_DIR):
    if filename.endswith(".yml"):
        language_name = filename[:-4]
        filepath = os.path.join(STRINGS_DIR, filename)
        
        try:
            with open(filepath, encoding="utf8") as f:
                languages[language_name] = yaml.safe_load(f)
                
            # For non-English languages, fill missing keys from English
            if language_name != "en" and "en" in languages:
                for item in languages["en"]:
                    if item not in languages[language_name]:
                        languages[language_name][item] = languages["en"][item]
            
            # Get language display name
            if language_name in languages and "name" in languages[language_name]:
                languages_present[language_name] = languages[language_name]["name"]
            else:
                print(f"Warning: Language name not found in {filename}")
                
        except Exception as e:
            print(f"Error loading language file {filename}: {e}")
            if language_name == "en":
                raise  # English is required

# ✅ Validate that at least English is loaded
if "en" not in languages:
    raise SystemExit(
        "[ERROR] English language file (en.yml) not found in strings/langs/. "
        "This is required for the bot to function."
    )
