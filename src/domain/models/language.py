from dataclasses import dataclass

@dataclass
class Language:
    lang_code:str
    lang_name:str

    def build_from_code(lang_code:str):
        match lang_code.lower():
            case "en":
                return Language(lang_code, "English")
            case "es":
                return Language(lang_code, "Spanish")
            case "fr":
                return Language(lang_code, "French")
            case "it":
                return Language(lang_code, "Italian")
            case "de":
                return Language(lang_code, "German")
            case _:
                raise ValueError(f"Language not supported ({lang_code})")