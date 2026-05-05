import sys
from pathlib import Path
from typing import List, Optional
from models import SearchResult
from ai_providers import ProviderAI


def find_obsidian_vaults(base_path: Path) -> List[Path]:
    """Находит все хранилища Obsidian в базовом пути рекурсивно"""

    vaults = []
    if not base_path.exists():
        return vaults
    
    for obsidian_dir in base_path.rglob(".obsidian"):
        vault_path = obsidian_dir.parent
        if vault_path.is_dir() and vault_path not in vaults:
            vaults.append(vault_path)
    
    return vaults


def search_notes_in_vault(vault_path: Path, query: str) -> List[SearchResult]:
    """Ищет заметки в хранилище"""

    results = []
    
    for file_path in vault_path.rglob("*.md"):
        # Пропускаем папку .obsidian
        if ".obsidian" in str(file_path):
            continue
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Простой текстовый поиск
            if query.lower() in content.lower():
                relative_path = file_path.relative_to(vault_path)
                path_parts = relative_path.parts
                
                folder = (
                    "/".join(path_parts[:-1]) if len(path_parts) > 1 else "")
                filename = path_parts[-1]
                title = filename.replace(".md", "")
                
                results.append(SearchResult(
                    title=title,
                    vault=vault_path.name,
                    folder=folder,
                    filename=filename,
                    content=content
                ))
        except Exception as e:
            print(
                f"Предупреждение: Не удалось прочитать файл {file_path}: {e}",
                file=sys.stderr)
            continue
    
    return results


def search_obsidian_notes(
        query: str, vaults_path: Path,
        ai_provider: Optional[ProviderAI] = None) -> List[SearchResult]:
    """
    Основная функция поиска заметок во всех хранилищах Obsidian
    """

    if not query.strip():
        raise ValueError("Поисковый запрос не может быть пустым")
    
    all_results = []
    
    vaults = find_obsidian_vaults(vaults_path)
    
    if not vaults:
        print(
            f"Предупреждение: Хранилища не найдены "
            f"в {vaults_path}", file=sys.stderr)
        return []
    
    for vault in vaults:
        notes = search_notes_in_vault(vault, query)
        all_results.extend(notes)
    
    if ai_provider:
        print(
            f"Обработка {len(all_results)} результат(ов) с AI...",
            file=sys.stderr)
        for note in all_results:
            ai_response = ai_provider.process_content(
                note.content,
                query,
                note.title,
                note.folder,
                note.vault
            )
            note.ai_processed = ai_response
    
    return all_results


def print_results(results: List[SearchResult]):
    """Результаты поиска в текстовом формате"""

    if not results:
        print("Результатов не найдено.")
        return
    
    print(f"\nНайдено {len(results)} результат(ов):\n")
    for i, result in enumerate(results, 1):
        print(f"Результат #{i}:")
        print(result)
        print()
