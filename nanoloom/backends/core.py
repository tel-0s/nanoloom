import importlib.util
import os

from nanoloom.backends.base import Backend

MODULE_ALIASES = {
    'openai': 'openai',
    'anthropic': 'anthropic',
    'replicate': 'replicate',
    'huggingface': 'transformers',
    'pytorch': 'torch'
}

BACKEND_CLASSES = {
    'openai': 'OpenAIBackend',
    'anthropic': 'AnthropicBackend',
    'replicate': 'ReplicateBackend',
    'huggingface': 'HuggingFaceBackend',
    'pytorch': 'PyTorchBackend'
}

def is_available(backend: str) -> bool:
    return importlib.util.find_spec(MODULE_ALIASES[backend]) is not None

def load_backend(backend: str) -> Backend:
    if not is_available(backend):
        raise ValueError(f'Backend {backend} is not available')
    backend_cls = importlib.import_module(f'nanoloom.backends.{backend}').__getattribute__(BACKEND_CLASSES[backend])

    return backend_cls()