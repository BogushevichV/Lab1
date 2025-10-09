from .binary_file import BinaryFile
from typing import Dict, Optional


class BinaryAnalyzer:
    """Анализатор бинарных файлов."""

    # Известные сигнатуры файлов
    FILE_SIGNATURES = {
        b'\xFF\xD8\xFF': 'JPEG Image',
        b'\x89\x50\x4E\x47': 'PNG Image',
        b'\x47\x49\x46\x38': 'GIF Image',
        b'\x42\x4D': 'BMP Image',
        b'\x49\x49\x2A\x00': 'TIFF Image (little-endian)',
        b'\x4D\x4D\x00\x2A': 'TIFF Image (big-endian)',
        b'\x25\x50\x44\x46': 'PDF Document',
        b'\x50\x4B\x03\x04': 'ZIP Archive / DOCX / XLSX',
        b'\x50\x4B\x05\x06': 'ZIP Archive (empty)',
        b'\x50\x4B\x07\x08': 'ZIP Archive (spanned)',
        b'\x52\x61\x72\x21\x1A\x07': 'RAR Archive',
        b'\x1F\x8B\x08': 'GZIP Archive',
        b'\x7F\x45\x4C\x46': 'ELF Executable',
        b'\x4D\x5A': 'DOS/Windows Executable',
        b'\xCA\xFE\xBA\xBE': 'Mach-O Binary (32-bit)',
        b'\xCF\xFA\xED\xFE': 'Mach-O Binary (32-bit reverse)',
        b'\xFE\xED\xFA\xCE': 'Mach-O Binary (32-bit)',
        b'\xFE\xED\xFA\xCF': 'Mach-O Binary (64-bit)',
        b'\x7B\x5C\x72\x74\x66': 'RTF Document',
        b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1': 'Microsoft Office Document (DOC/XLS/PPT)',
        b'\x49\x44\x33': 'MP3 Audio (ID3v2)',
        b'\xFF\xFB': 'MP3 Audio',
        b'\x66\x74\x79\x70': 'MP4 Video (at offset 4)',
        b'\x00\x00\x00\x20\x66\x74\x79\x70': 'MP4 Video',
        b'\x52\x49\x46\x46': 'RIFF (AVI/WAV)',
        b'\x4F\x67\x67\x53': 'OGG Audio',
        b'\x66\x4C\x61\x43': 'FLAC Audio',
        b'\x30\x26\xB2\x75\x8E\x66\xCF\x11': 'WMA/WMV',
    }

    def __init__(self, file: BinaryFile):
        self.file = file

    def detect_file_type(self) -> Optional[str]:
        """Определение типа файла по сигнатуре."""
        if not self.file.exists():
            return None

        signature = self.file.get_file_signature()

        # Проверяем известные сигнатуры
        for sig, file_type in self.FILE_SIGNATURES.items():
            if signature.startswith(sig):
                return file_type

        # Проверяем текстовый файл
        if self._is_text_file(signature):
            return 'Text File'

        return 'Unknown Binary File'

    @staticmethod
    def _is_text_file(data: bytes, sample_size: int = 512) -> bool:
        """Проверка, является ли файл текстовым."""
        if not data:
            return False

        # Проверяем наличие непечатаемых символов
        text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)))
        sample = data[:sample_size]

        non_text = sum(1 for byte in sample if byte not in text_chars)

        return non_text / len(sample) < 0.3 if sample else False

    def analyze_structure(self) -> Dict:
        """Анализ структуры бинарного файла."""
        if not self.file.exists():
            return {'error': 'Файл не найден'}

        size = self.file.get_size()
        distribution = self.file.get_byte_distribution()

        # Подсчет статистики
        total_bytes = sum(distribution.values())
        non_zero_bytes = sum(1 for count in distribution.values() if count > 0)

        # Энтропия (по формуле Шеннона)
        import math
        entropy = 0.0
        if total_bytes > 0:
            for count in distribution.values():
                if count > 0:
                    probability = count / total_bytes
                    entropy -= probability * math.log2(probability)

        # Наиболее частые байты
        most_common = sorted(
            [(byte, count) for byte, count in distribution.items() if count > 0],
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return {
            'file_type': self.detect_file_type(),
            'size': size,
            'total_bytes': total_bytes,
            'unique_bytes': non_zero_bytes,
            'entropy': entropy,
            'most_common_bytes': [
                {
                    'byte': f"0x{byte:02X}",
                    'decimal': byte,
                    'ascii': chr(byte) if 32 <= byte <= 126 else '.',
                    'count': count,
                    'percentage': (count / total_bytes * 100) if total_bytes > 0 else 0
                }
                for byte, count in most_common
            ],
            'null_bytes': distribution[0],
            'null_percentage': (distribution[0] / total_bytes * 100) if total_bytes > 0 else 0
        }

    def find_patterns(self, min_length: int = 4, max_patterns: int = 20) -> list:
        """Поиск повторяющихся паттернов."""
        if not self.file.exists():
            return []

        data = self.file.read_bytes()
        if len(data) < min_length * 2:
            return []

        patterns = {}

        # Поиск паттернов заданной длины
        for length in range(min_length, min(min_length + 4, len(data) // 2)):
            for i in range(len(data) - length + 1):
                pattern = data[i:i + length]

                # Пропускаем паттерны из одинаковых байтов
                if len(set(pattern)) == 1:
                    continue

                pattern_key = pattern.hex()
                if pattern_key not in patterns:
                    patterns[pattern_key] = {
                        'pattern': pattern,
                        'length': length,
                        'offsets': []
                    }

                if len(patterns[pattern_key]['offsets']) < 100:
                    patterns[pattern_key]['offsets'].append(i)

        # Фильтруем паттерны, встречающиеся более одного раза
        repeated = [
            {
                'pattern': p['pattern'].hex(),
                'length': p['length'],
                'count': len(p['offsets']),
                'first_offset': p['offsets'][0],
                'offsets': p['offsets'][:10]  # Показываем первые 10
            }
            for p in patterns.values() if len(p['offsets']) > 1
        ]

        # Сортируем по частоте встречаемости
        repeated.sort(key=lambda x: x['count'], reverse=True)

        return repeated[:max_patterns]

    def write_report(self, report_path: str, encoding: str = 'utf-8') -> None:
        """Запись отчета о бинарном файле."""
        analysis = self.analyze_structure()
        patterns = self.find_patterns()

        with open(report_path, mode='w', encoding=encoding) as report:
            report.write(f"=== Анализ бинарного файла ===\n")
            report.write(f"Файл: {self.file.path}\n\n")

            if 'error' in analysis:
                report.write(f"Ошибка: {analysis['error']}\n")
                return

            report.write(f"Тип файла: {analysis['file_type']}\n")
            report.write(f"Размер: {analysis['size']} байт\n")
            report.write(f"Уникальных байтов: {analysis['unique_bytes']}/256\n")
            report.write(f"Энтропия: {analysis['entropy']:.4f}\n")
            report.write(f"Нулевых байтов: {analysis['null_bytes']} ({analysis['null_percentage']:.2f}%)\n\n")

            report.write("=== Наиболее частые байты ===\n")
            for item in analysis['most_common_bytes']:
                report.write(
                    f"  {item['byte']} ({item['decimal']}) '{item['ascii']}': "
                    f"{item['count']} раз ({item['percentage']:.2f}%)\n"
                )

            if patterns:
                report.write(f"\n=== Повторяющиеся паттерны ===\n")
                for pattern in patterns[:10]:
                    report.write(
                        f"  Паттерн {pattern['pattern']} (длина {pattern['length']}): "
                        f"{pattern['count']} раз, начиная с offset {pattern['first_offset']}\n"
                    )