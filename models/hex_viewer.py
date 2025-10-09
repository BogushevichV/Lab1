from .binary_file import BinaryFile
from typing import Generator, Tuple


class HexViewer:
    """Hex-просмотрщик файлов."""

    def __init__(self, file: BinaryFile, bytes_per_line: int = 16):
        self.file = file
        self.bytes_per_line = bytes_per_line

    @staticmethod
    def byte_to_hex(byte: int) -> str:
        """Преобразование байта в hex-строку."""
        return f"{byte:02X}"

    @staticmethod
    def byte_to_ascii(byte: int) -> str:
        """Преобразование байта в ASCII-символ."""
        if 32 <= byte <= 126:
            return chr(byte)
        return '.'

    def format_hex_line(self, offset: int, data: bytes) -> str:
        """Форматирование одной строки hex-просмотра."""
        # Смещение
        line = f"{offset:08X}  "

        # Hex-представление
        hex_parts = []
        for i in range(self.bytes_per_line):
            if i < len(data):
                hex_parts.append(self.byte_to_hex(data[i]))
            else:
                hex_parts.append("  ")

            # Добавляем разделитель после 8 байт
            if i == 7:
                hex_parts.append(" ")

        line += " ".join(hex_parts)
        line += "  "

        # ASCII-представление
        ascii_repr = ''.join(self.byte_to_ascii(b) for b in data)
        line += f"|{ascii_repr}|"

        return line

    def view_range(self, start_offset: int = 0, lines: int = 16) -> Generator[str, None, None]:
        """Просмотр диапазона файла."""
        if not self.file.exists():
            yield "Файл не найден"
            return

        bytes_to_read = lines * self.bytes_per_line
        data = self.file.read_bytes(start_offset, bytes_to_read)

        offset = start_offset
        for i in range(0, len(data), self.bytes_per_line):
            chunk = data[i:i + self.bytes_per_line]
            yield self.format_hex_line(offset, chunk)
            offset += self.bytes_per_line

    def view_all_paged(self, lines_per_page: int = 16) -> Generator[Tuple[int, list], None, None]:
        """Постраничный просмотр всего файла."""
        if not self.file.exists():
            yield (0, ["Файл не найден"])
            return

        offset = 0
        page_lines = []

        for chunk_offset, chunk in self.file.read_chunks(self.bytes_per_line):
            line = self.format_hex_line(chunk_offset, chunk)
            page_lines.append(line)

            if len(page_lines) >= lines_per_page:
                yield (offset, page_lines)
                offset = chunk_offset + len(chunk)
                page_lines = []

        if page_lines:
            yield (offset, page_lines)

    def search_and_highlight(self, pattern: bytes, context_lines: int = 2) -> list:
        """Поиск паттерна и отображение с контекстом."""
        offsets = self.file.find_bytes(pattern, max_results=50)
        results = []

        for offset in offsets:
            start_line_offset = (offset // self.bytes_per_line) * self.bytes_per_line
            start_offset = max(0, start_line_offset - context_lines * self.bytes_per_line)

            lines_to_show = context_lines * 2 + 1
            data = self.file.read_bytes(start_offset, lines_to_show * self.bytes_per_line)

            result_lines = []
            current_offset = start_offset
            for i in range(0, len(data), self.bytes_per_line):
                chunk = data[i:i + self.bytes_per_line]
                line = self.format_hex_line(current_offset, chunk)

                # Помечаем строку с найденным паттерном
                if start_line_offset <= current_offset <= start_line_offset + self.bytes_per_line:
                    line = ">>> " + line
                else:
                    line = "    " + line

                result_lines.append(line)
                current_offset += self.bytes_per_line

            results.append({
                'offset': offset,
                'lines': result_lines
            })

        return results

    def get_file_info(self) -> dict:
        """Получение информации о файле."""
        if not self.file.exists():
            return {'error': 'Файл не найден'}

        size = self.file.get_size()
        signature = self.file.get_file_signature()

        return {
            'path': self.file.path,
            'size': size,
            'size_formatted': self._format_size(size),
            'signature': ' '.join(self.byte_to_hex(b) for b in signature),
            'md5': self.file.calculate_checksum('md5'),
            'sha1': self.file.calculate_checksum('sha1'),
            'sha256': self.file.calculate_checksum('sha256')
        }

    @staticmethod
    def _format_size(size: int) -> str:
        """Форматирование размера файла."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"