from models import SearchScoringProfile

class IndexFilterResult:
    def __init__(self, index_name:str, scoring_profile:SearchScoringProfile = None):
        self.index_name = index_name
        self.scoring_profile = scoring_profile