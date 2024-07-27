# nanoloom backend core data structures and abstract classes

from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

@dataclass
class Logprobs:
    """Log probabilities for a completion"""
    token_logprobs: List[float]
    top_logprobs: List[List[float]]
    text_offset: List[int]
    tokens: List[str]

@dataclass
class CompletionChoice:
    """A completion choice"""
    text: str
    index: int
    finish_reason: str
    logprobs: Optional[Logprobs] = None

@dataclass
class Usage:
    """Usage statistics for a completion"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

@dataclass
class Completion:
    """A completion"""
    id: str
    created: float
    model: str
    choices: List[CompletionChoice]
    usage: Optional[Usage] = None

class Backend(ABC):
    """An abstract backend for nanoloom"""

    @abstractmethod
    def get_models(self) -> List[Dict[str, Any]]:
        """Get a list of available models"""
        pass

    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> Completion:
        """Generate a completion for a prompt"""
        pass