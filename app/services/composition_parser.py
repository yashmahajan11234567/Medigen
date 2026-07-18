from app.schemas.generic_finder import CanonicalComposition
from app.core.enums import MedicineType
from app.core.exceptions import AppException
import re


class CompositionParser:
    def parse(self, raw_text: str) -> CanonicalComposition:
        """Transform OCR output into a CanonicalComposition.

        Args:
            raw_text: Text returned by OCRService.

        Returns:
            CanonicalComposition validated by Pydantic.

        Raises:
            ValueError: If the text cannot be parsed into a valid composition.
            AppException: For domain-specific validation failures (e.g., combination medicine).
        """
        if not raw_text or not raw_text.strip():
            raise ValueError("Empty or whitespace-only input")

        text = raw_text.strip()

        # Check for combination medicine indicators early
        if self._is_combination_medicine(text):
            raise AppException(
                message="Combination medicines are not supported in Version 1.",
                status_code=422,
                code="unsupported_combination_medicine",
            )

        # Find first digit position
        first_digit_match = re.search(r"\d", text)
        if first_digit_match:
            # Digits found - character-by-character parsing
            number_start = first_digit_match.start()

            # Consume consecutive digits and decimal points into strength candidate
            pos = number_start
            strength_chars = []
            while pos < len(text) and (text[pos].isdigit() or text[pos] == '.'):
                strength_chars.append(text[pos])
                pos += 1
            strength_str = ''.join(strength_chars)
            number_end = pos

            # Handle percentage: % sign immediately after the number is part of the strength
            # and the % sign itself is the unit
            is_percentage = False
            if pos < len(text) and text[pos] == '%':
                strength_str += '%'
                number_end = pos + 1
                is_percentage = True

            # Extract ingredient (everything before the number)
            ingredient = text[:number_start].strip()
            if not ingredient:
                raise ValueError("Unable to parse composition")

            # Extract unit:
            if is_percentage:
                # Percentage case: unit is just the % sign
                unit_str = '%'
                unit_end = number_end
            else:
                # Non-percentage case: take consecutive non-whitespace after the number
                pos = number_end
                while pos < len(text) and text[pos].isspace():
                    pos += 1
                start = pos
                while pos < len(text) and not text[pos].isspace():
                    pos += 1
                end = pos
                unit_str = text[start:end].strip()
                unit_end = end

            if not unit_str:
                raise ValueError("Unable to parse composition")

            # Extract everything after the unit
            remaining_text = text[unit_end:].strip()
            if not remaining_text:
                raise ValueError("Unable to parse composition")

            # Parse remaining text to extract dosage form and route
            dosage_form, route = self._parse_dosage_form_and_route(remaining_text)
        else:
            # No digits found - fall back to token-based approach
            # for cases like "Paracetamol abc mg tablet oral"
            tokens = text.split()
            if len(tokens) < 5:
                raise ValueError("Unable to parse composition")

            ingredient = tokens[0].strip()
            strength_str = tokens[1].strip()
            unit_str = tokens[2].strip()
            dosage_form = tokens[3].strip()
            route = " ".join(tokens[4:]).strip() if len(tokens) > 4 else "oral"

            if not ingredient:
                raise ValueError("Unable to parse composition")
            if not unit_str:
                raise ValueError("Unable to parse composition")
            if not dosage_form:
                raise ValueError("Unable to parse composition")

        # Validate and process each component

        # Ingredient: just basic validation
        if not ingredient:
            raise ValueError("Ingredient cannot be empty")

        # Strength: validate and normalize
        if not strength_str:
            raise ValueError("Strength cannot be empty")

        # Handle percentage
        if strength_str.endswith('%'):
            strength = strength_str
            numeric_part = strength_str[:-1]
        else:
            strength = strength_str
            numeric_part = strength_str

        # Check for multiple decimal points
        if numeric_part.count('.') > 1:
            raise ValueError("Invalid strength format")

        # Validate numeric part and normalize
        try:
            val = float(numeric_part)
            if '.' in numeric_part:
                strength_numeric = str(val).rstrip('0').rstrip('.')
            else:
                strength_numeric = str(int(val))

            if strength_str.endswith('%'):
                strength = strength_numeric + '%'
            else:
                strength = strength_numeric
        except ValueError:
            raise ValueError(f"Invalid strength format: '{strength_str}'")

        # Unit: basic validation and normalization
        unit = unit_str.lower().strip()
        if not unit:
            raise ValueError("Unit cannot be empty")

        # Dosage form: validate and map to enum
        if not dosage_form:
            raise ValueError("Dosage form cannot be empty")

        dosage_form_lower = dosage_form.lower().rstrip('s')

        dose_form_map = {
            'tablet': MedicineType.TABLET,
            'tab': MedicineType.TABLET,
            'capsule': MedicineType.CAPSULE,
            'cap': MedicineType.CAPSULE,
            'syrup': MedicineType.SYRUP,
            'cream': MedicineType.CREAM,
            'ointment': MedicineType.OINTMENT,
            'oint': MedicineType.OINTMENT,
            'injection': MedicineType.INJECTION,
            'inj': MedicineType.INJECTION,
            'injectable': MedicineType.INJECTION,
            'drops': MedicineType.DROPS,
            'drop': MedicineType.DROPS,
            'eye drops': MedicineType.DROPS,
            'ear drops': MedicineType.DROPS,
            'nasal drops': MedicineType.DROPS,
            'nasal spray': MedicineType.OTHER,
            'inhaler': MedicineType.INHALER,
            'inh': MedicineType.INHALER,
            'inhalation': MedicineType.INHALER,
            'suppository': MedicineType.OTHER,
            'pessary': MedicineType.OTHER,
            'gel': MedicineType.OTHER,
            'solution': MedicineType.OTHER,
            'infusion': MedicineType.OTHER
        }

        if dosage_form_lower in dose_form_map:
            dosage_form_enum = dose_form_map[dosage_form_lower]
        else:
            found = False
            for key, value in dose_form_map.items():
                if key in dosage_form_lower or dosage_form_lower in key:
                    dosage_form_enum = value
                    found = True
                    break
            if not found:
                dosage_form_enum = MedicineType.OTHER

        # Route: basic validation
        if not route:
            raise ValueError("Route cannot be empty")

        return CanonicalComposition(
            ingredient=ingredient,
            strength=strength,
            unit=unit,
            dosage_form=dosage_form_enum,
            route=route
        )

    def _is_combination_medicine(self, text: str) -> bool:
        """Check if the text indicates a combination medicine."""
        combination_patterns = [
            r'[A-Za-z]\s*\+\s*[A-Za-z]',
            r'[A-Za-z]\s*&\s*[A-Za-z]',
            r'[A-Za-z]\s*,\s*[A-Za-z]',
        ]

        for pattern in combination_patterns:
            matches = list(re.finditer(pattern, text))
            for match in matches:
                start = max(0, match.start() - 10)
                end = min(len(text), match.end() + 10)
                context = text[start:end]

                separator = match.group()
                sep_char = ''.join(c for c in separator if not c.isalpha() and not c.isspace())

                parts = re.split(r'\s*[' + re.escape(sep_char) + r']\s*', context, maxsplit=2)
                if len(parts) >= 2:
                    left_part = parts[0].strip()
                    right_part = parts[1].strip() if len(parts) > 1 else ""

                    unit_pattern = r'^\s*\d+(?:\.\d+)?\s*[a-zA-Z]*(?:\s*/\s*\d+(?:\.\d+)?\s*[a-zA-Z]*)?\s*$'
                    if left_part and right_part and re.match(unit_pattern, left_part) and re.match(unit_pattern, right_part):
                        continue
                    else:
                        return True

        slash_matches = list(re.finditer(r'[A-Za-z]\s*/\s*[A-Za-z]', text))
        for match in slash_matches:
            def get_word_containing_pos(pos):
                if pos < 0 or pos >= len(text):
                    return ""
                start = pos
                while start > 0 and (text[start - 1].isalnum() or text[start - 1] in '-_'):
                    start -= 1
                end = pos
                while end < len(text) and (text[end].isalnum() or text[end] in '-_'):
                    end += 1
                return text[start:end]

            left_token = get_word_containing_pos(match.start())
            right_token = get_word_containing_pos(match.end() - 1)

            if not left_token or not right_token:
                continue

            def looks_like_unit_component(token):
                if not token:
                    return False
                if re.search(r'\d', token):
                    return True
                unit_abbreviations = {'mg', 'ml', 'g', 'kg', 'l', 'dl', 'ul',
                                    'iu', 'international unit', 'units',
                                    'meq', 'meql', 'mmol', 'mol', 'mEq',
                                    '%', 'percent', 'mcg', 'ug'}
                if token.lower().strip() in unit_abbreviations:
                    return True
                return False

            left_is_unit = looks_like_unit_component(left_token)
            right_is_unit = looks_like_unit_component(right_token)

            if left_is_unit and right_is_unit:
                continue
            else:
                return True

        return False

    def _parse_dosage_form_and_route(self, text: str) -> tuple[str, str]:
        """Parse dosage form and route from the text following the unit."""
        if not text:
            return "", "oral"

        route_terms = {
            'iv', 'im', 'sc', 'sl',
            'po', 'pr',
            'oral', 'topical', 'nasal', 'buccal', 'vaginal', 'rectal',
            'ophthalmic', 'otic',
            'intraarterial', 'intrathecal', 'intraocular',
            'intranasal',
            'ip', 'subcut', 'id', 'ih'
        }

        dosage_forms = {
            'tablet', 'cap', 'capsule', 'syrup', 'cream', 'ointment',
            'injection', 'drops', 'inhaler', 'suppository',
            'eye drops', 'ear drops', 'nasal drops', 'nasal spray',
            'inhalation', 'solution', 'gel', 'infusion', 'pessary'
        }

        noise_words = {'ml', 'mg'}

        words = text.split()
        if not words:
            return "", "oral"

        route = "oral"
        lower_words = [w.lower() for w in words]

        if len(words) >= 1 and lower_words[-1] in route_terms:
            route = lower_words[-1]
        elif len(words) >= 1 and lower_words[0] in {'iv', 'im', 'sc', 'sl', 'po', 'pr'}:
            route = lower_words[0]

        words_for_dose = words.copy()

        if len(words) >= 1 and lower_words[-1] in route_terms and lower_words[-1] not in dosage_forms:
            words_for_dose = words[:-1]
        elif len(words) >= 1 and lower_words[0] in {'iv', 'im', 'sc', 'sl', 'po', 'pr'} and \
             lower_words[0] not in dosage_forms:
            words_for_dose = words[1:]

        words_for_dose = [w for w in words_for_dose if w.lower() not in noise_words]

        dosage_form = self._extract_dosage_form_from_words(words_for_dose, dosage_forms)

        if not dosage_form:
            dosage_form = self._extract_dosage_form_from_text(text, dosage_forms)

        if not dosage_form:
            dosage_form = self._find_any_dosage_form(text, dosage_forms)

        return dosage_form, route

    def _extract_dosage_form_from_words(self, words: list[str], dosage_forms: set[str]) -> str:
        """Try to extract a dosage form from a list of words."""
        if not words:
            return ""

        for word in words:
            if word.lower() in dosage_forms:
                return word

        if len(words) >= 2:
            for i in range(len(words) - 1):
                bigram = f"{words[i]} {words[i+1]}"
                if bigram.lower() in dosage_forms:
                    return bigram

        if len(words) >= 3:
            for i in range(len(words) - 2):
                trigram = f"{words[i]} {words[i+1]} {words[i+2]}"
                if trigram.lower() in dosage_forms:
                    return trigram

        return ""

    def _extract_dosage_form_from_text(self, text: str, dosage_forms: set[str]) -> str:
        """Try to extract dosage form by looking for substrings in the text."""
        lower_text = text.lower()
        for df in sorted(dosage_forms, key=len, reverse=True):
            if df in lower_text:
                start = lower_text.find(df)
                return text[start:start + len(df)]
        return ""

    def _find_any_dosage_form(self, text: str, dosage_forms: set[str]) -> str:
        """Last resort: find any dosage form substring in the text."""
        return self._extract_dosage_form_from_text(text, dosage_forms)