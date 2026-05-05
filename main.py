import sys
from pathlib import Path

from config import load_config
from ai_providers import ProviderAI
from search import search_obsidian_notes, print_results


def get_query_interactively() -> str:
    """Запрашивает поисковый запрос"""

    print("Поиск по хранилищам Obsidian")
    print("="*50)
    
    while True:
        try:
            query = input(
                "\nВведите поисковый запрос или 'exit' для выхода: ").strip()
            
            if query.lower() == 'exit':
                sys.exit(0)
            
            if query:
                return query
            else:
                print("Запрос не может быть пустым.")
        except KeyboardInterrupt:
            print("\nВыход из программы.")
            sys.exit(0)
        except EOFError:
            print("\nВыход из программы.")
            sys.exit(0)


def main():

    query = get_query_interactively()
    config = load_config()
    
    # Значения конфигурации
    if 'vaults_path' not in config:
        print(
            "Ошибка: 'vaults_path' не найден в конфигурационном файле",
            file=sys.stderr)
        sys.exit(1)
    
    vaults_path = Path(config['vaults_path'])
    
    # Создаем провайдер по конфигурации
    ai_provider = ProviderAI.from_config(config)
    
    try:
        # Поиск
        results = search_obsidian_notes(
            query=query,
            vaults_path=vaults_path,
            ai_provider=ai_provider
        )
        
        print_results(results)
        sys.exit(0 if results else 1)
        
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()