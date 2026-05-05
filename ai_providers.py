import requests
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


# Системный промпт
SYSTEM_PROMPT = """You are a helpful assistant that analyzes Obsidian notes and provides clear, beautiful answers in Russian.

Your task is to accurately and completely convey the meaning of the user's notes in response to their query. You must answer in Russian.

Analyze the note content. Identify key ideas, facts, relationships between them, and conclusions that are directly or indirectly relevant to the query.

If the notes contain information relevant to the query:
- Structure your response clearly: use logical sections, bullet or numbered lists, brief summaries
- Do not add information that is not present in the notes, and do not make assumptions unsupported by the note text
- If the meaning of a note is not obvious, quote it or paraphrase it while preserving the original context

If the notes do not contain information that answers the query, clearly state in Russian: "В предоставленных заметках нет информации, отвечающей на этот запрос."
Do not attempt to invent an answer in that case.

Your response should be clear and readable in Russian, prioritizing accuracy over unnecessary embellishment."""


class ProviderAI(ABC):

    @abstractmethod
    def process_content(self, content: str, query: str, title: str, folder: str, vault: str) -> str:
        """Обрабатывает содержимое с помощью AI"""
        pass
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> Optional['AIProvider']:
        """Создает экземпляр провайдера"""

        use_ai = config.get('use_ai', False)
        if not use_ai:
            return None
            
        provider_type = config.get('ai_provider', 'ollama').lower()
        
        if provider_type == 'ollama':
            return OllamaProvider(
                host=config.get('ollama_host', 'localhost'),
                port=config.get('ollama_port', 11434),
                model=config.get('ollama_model', 'llama2')
            )
        elif provider_type == 'openai':
            return OpenAIProvider(
                api_key=config.get('openai_api_key', ''),
                model=config.get('openai_model', 'gpt-3.5-turbo'),
                base_url=config.get(
                    'openai_base_url', 'https://api.openai.com/v1')
            )
        else:
            raise ValueError(f"Неизвестный провайдер AI: {provider_type}")


class OllamaProvider(ProviderAI):
    """Провайдер на основе Ollama"""
    
    def __init__(self, host: str = 'localhost', port: int = 11434, model: str = 'llama2'):
        self.host = host
        self.port = port
        self.model = model
    
    def process_content(self, content: str, query: str, title: str, folder: str, vault: str) -> str:
        """
        Обрабатывает содержимое с помощью Ollama для создания красивого ответа
        """

        try:
            # Собираем промпт из контекстной информации и общей системной инструкции
            prompt = f"""Context Information:
- Vault: {vault}
- Folder: {folder}
- Note Title: {title}

User Query: {query}

Note Content:
{content}

{SYSTEM_PROMPT}
"""

            # Отправляем запрос к Ollama
            response = requests.post(
                f"http://{self.host}:{self.port}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9
                    }
                },
                # Увеличенный таймаут, ставил для себя так как у меня локальные
                # модели работают медленно
                timeout=600
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", content)
            else:
                return (
                    f"Ошибка обработки "
                    f"{response.status_code} - {response.text}")
        except Exception as e:
            return f"Ошибка обработки AI: {str(e)}."


class OpenAIProvider(ProviderAI):
    """Провайдер на основе OpenAI"""
    
    def __init__(self, api_key: str, model: str = 'gpt-3.5-turbo',
                 base_url: str = 'https://api.openai.com/v1'):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
    
    def process_content(self, content: str, query: str, title: str, folder: str, vault: str) -> str:
        """Обрабатывает содержимое с помощью OpenAI"""
        try:
            # Подготавливаем промпт для OpenAI с контекстной информацией
            messages = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": f"""Context Information:
- Vault: {vault}
- Folder: {folder}
- Note Title: {title}

User Query: {query}

Note Content:
{content}

Please analyze this note and provide a clear response in Russian based on the query."""
                }
            ]
            
            # Отправляем запрос к OpenAI
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return (
                    f"Ошибка обработки "
                    f"{response.status_code} - {response.text}")
        except Exception as e:
            return f"Ошибка обработки AI: {str(e)}. "