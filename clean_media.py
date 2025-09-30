import os
import shutil
from pathlib import Path


def clean_media():
    """Очищает папку media и создает правильную структуру"""
    media_root = Path('media')

    if media_root.exists():
        # Удаляем только содержимое, но сохраняем структуру
        for item in media_root.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
        print("✅ Media папка очищена")

    # Создаем правильную структуру
    folders = [
        'products/main',
        'products/gallery',
        'shops',
        'users'
    ]

    for folder in folders:
        path = media_root / folder
        path.mkdir(parents=True, exist_ok=True)
        (path / '.gitkeep').touch()  # Создаем пустой файл чтобы папки попали в git

    print("✅ Структура media папки создана")


if __name__ == "__main__":
    clean_media()