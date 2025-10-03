import os
from typing import Generator, Optional, Tuple
import tempfile


class FileExistsErrorCustom(Exception):
    """Исключение для случая, когда файл уже существует."""
    pass


class TextFile:
    """
    Класс для работы с текстовым файлом.
    """

    def __init__(self, path: str):
        self.path = path

    def exists(self) -> bool:
        return os.path.isfile(self.path)

    def create(self, initial_text: Optional[str] = None, encoding: str = 'utf-8', overwrite: bool = False) -> None:
        if self.exists() and not overwrite:
            raise FileExistsErrorCustom(f"Файл '{self.path}' уже существует.")
        with open(self.path, 'w', encoding=encoding, newline='') as f:
            if initial_text:
                f.write(initial_text)

    def append(self, text: str, encoding: str = 'utf-8') -> None:
        with open(self.path, 'a', encoding=encoding, newline='') as f:
            f.write(text)

    def clear(self, encoding: str = 'utf-8') -> None:
        with open(self.path, 'w', encoding=encoding) as f:
            pass

    def read_lines(self, encoding: str = 'utf-8', errors: str = 'strict') -> Generator[str, None, None]:
        with open(self.path, 'r', encoding=encoding, errors=errors) as f:
            for line in f:
                yield line.rstrip('\n')

    def read_paged(self, lines_per_page: int = 25, encoding: str = 'utf-8', errors: str = 'strict') -> Generator[Tuple[int, list], None, None]:
        page = []
        start_line = 1
        idx = 0
        for line in self.read_lines(encoding=encoding, errors=errors):
            idx += 1
            page.append(line)
            if len(page) >= lines_per_page:
                yield (start_line, page)
                start_line = idx + 1
                page = []
        if page:
            yield (start_line, page)

    def search_and_replace(self, find_text: str, replace_text: str, encoding: str = 'utf-8', case_sensitive: bool = True) -> int:
        """
        Поиск и замена текста.
        Теперь безопасно работает на разных дисках (Windows).
        """
        replacements = 0

        # создаём временный файл в той же папке, что и исходный файл
        dir_name = os.path.dirname(os.path.abspath(self.path))
        with tempfile.NamedTemporaryFile('w', delete=False, encoding=encoding, newline='', dir=dir_name) as tmp:
            tmppath = tmp.name
            for line in self.read_lines(encoding=encoding):
                original = line
                if case_sensitive:
                    new_line = original.replace(find_text, replace_text)
                    count = original.count(find_text)
                else:
                    lowered = original.lower()
                    target = find_text.lower()
                    count = lowered.count(target)
                    parts = []
                    i = 0
                    lo = original.lower()
                    while True:
                        idx = lo.find(target, i)
                        if idx == -1:
                            parts.append(original[i:])
                            break
                        parts.append(original[i:idx])
                        parts.append(replace_text)
                        i = idx + len(target)
                    new_line = ''.join(parts)
                replacements += count
                tmp.write(new_line + '\n')

        # безопасная замена файла
        os.replace(tmppath, self.path)
        return replacements
