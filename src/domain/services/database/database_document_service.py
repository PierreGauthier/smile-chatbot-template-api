from abc import ABC, abstractmethod

from domain.models import RagDocument
class DatabaseDocumentService:
    """Interface for retrieving pre-indexed RAG documents from the database layer."""

    @abstractmethod
    def get_document(self, doc_type:str, document_id:str) -> RagDocument:
        """Fetch a document by type and identifier.

        Args:
            doc_type: High-level grouping used to partition documents.
            document_id: Unique identifier for the document within `doc_type`.

        Returns:
            RagDocument: Materialized document ready for downstream consumers.
        """
        pass
