from typing import Annotated
from fastapi import Depends

from services import FirestoreBase
from config import Settings, get_settings

class FirestoreHistoryDb(FirestoreBase):
    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        super().__init__(
            collection=settings.firestore_history_collection,
            settings=settings
        )