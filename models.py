from typing import Dict, Any, Optional


class SearchResult:
    """Результат поиска"""

    def __init__(self, title: str, vault: str, folder: str, filename: str,
                 content: str, ai_processed: Optional[str] = None):
        self.title = title
        self.vault = vault
        self.folder = folder
        self.filename = filename
        self.content = content
        self.ai_processed = ai_processed
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует для JSON сериализации"""

        return {
            "title": self.title,
            "vault": self.vault,
            "folder": self.folder,
            "filename": self.filename,
            "content": self.content,
            "ai_processed": self.ai_processed
        }
    
    def __str__(self) -> str:
        """Строковое представление для консоли"""

        result = f"Заметка: {self.title}\n"
        result += f"   Хранилище: {self.vault}\n"
        if self.folder:
            result += f"   Папка: {self.folder}\n"
        result += f"   Файл: {self.filename}\n"
        
        content_preview = self.content
        if self.ai_processed:
            content_preview = self.ai_processed

        result += f"   Содержимое: {content_preview}\n"
        result += "-" * 50
        return result
