from dataclasses import dataclass

from models import SearchScoringProfile

@dataclass
class IndexFilterResult:
    index_name:str
    scoring_profile:SearchScoringProfile = None