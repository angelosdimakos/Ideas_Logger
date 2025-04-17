# scripts/ci_analyzer/artifact_base.py

from abc import ABC, abstractmethod

class ArtifactParser(ABC):
    @abstractmethod
    def parse(self, path: str) -> dict:
        """
        Parse artifact file into a standardized format.
        Returns a dictionary with summary metrics and/or issue details.
        """
        pass
