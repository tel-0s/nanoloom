from nanoloom.backends.base import Backend, Completion, CompletionChoice, Logprobs, Usage
from openai import OpenAI
from typing import List, Dict, Any, Optional
from nanoloom.utils import to_dict
import os

class OpenAIBackend(Backend):
    """An OpenAI backend for nanoloom"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.organization = os.getenv('OPENAI_ORGANIZATION')
        self.client = OpenAI(api_key=self.api_key, organization=self.organization)

    def get_models(self) -> List[Dict[str, Any]]:
        return [to_dict(model) for model in self.client.models.list()]
    
    def complete(self, prompt: str, **kwargs) -> List[Completion]:
        response = self.client.completions.create(
            model=kwargs.get('model'),
            prompt=prompt,
            temperature=kwargs.get('temperature'),
            max_tokens=kwargs.get('max_tokens'),
            n=kwargs.get('num_samples'),
            stop=kwargs.get('stop'),
            # top_k=kwargs.get('top_k'),
            top_p=kwargs.get('top_p'),
            presence_penalty=kwargs.get('presence_penalty'),
            frequency_penalty=kwargs.get('frequency_penalty')
        )

        completion = Completion(
            id = response.id,
            created = response.created,
            model = response.model,
            choices = [CompletionChoice(
                text = choice.text,
                index = choice.index,
                finish_reason = choice.finish_reason,
                logprobs = Logprobs(
                    token_logprobs = choice.logprobs.token_logprobs,
                    top_logprobs = choice.logprobs.top_logprobs,
                    text_offset = choice.logprobs.text_offset,
                    tokens = choice.logprobs.tokens
                ) if 'logprobs' in choice else None
            ) for choice in response.choices],
            usage = Usage(
                prompt_tokens = response.usage.prompt_tokens,
                completion_tokens = response.usage.completion_tokens,
                total_tokens = response.usage.total_tokens
            )
        )

        return completion