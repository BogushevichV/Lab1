from .text_file import TextFile


class TextAnalyzer:
    """Анализатор текста (символы, слова, строки)."""

    def __init__(self, file: TextFile):
        self.file = file

    @staticmethod
    def _count_words_in_line(line: str) -> int:
        return len(line.strip().split())

    def analyze(self, encoding: str = 'utf-8', errors: str = 'strict') -> dict:
        char_count = 0
        word_count = 0
        line_count = 0
        for line in self.file.read_lines(encoding=encoding, errors=errors):
            line_count += 1
            char_count += len(line)
            word_count += self._count_words_in_line(line)
        return {
            'characters': char_count,
            'words': word_count,
            'lines': line_count
        }

    def write_report(self, report_path: str, encoding: str = 'utf-8') -> None:
        results = self.analyze(encoding=encoding)
        with open(report_path, mode='w', encoding=encoding) as report:
            report.write(f"Анализ файла: {self.file.path}\n")
            report.write(f"Символов: {results['characters']}\n")
            report.write(f"Слов: {results['words']}\n")
            report.write(f"Строк: {results['lines']}\n")
