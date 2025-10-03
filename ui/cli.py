from models.text_file import TextFile
from models.file_converter import FileConverter
from models.text_analyzer import TextAnalyzer


class CLI:
    """Консольное меню."""

    def __init__(self):
        self.running = True

    def prompt(self, text: str) -> str:
        try:
            return input(text)
        except EOFError:
            return ''

    def choose_file(self):
        filename = self.prompt("Введите путь к файлу: ").strip()
        if not filename:
            print("Файл не указан.")
            return None
        return TextFile(filename)

    def create_file_flow(self):
        tf = self.choose_file()
        if not tf:
            return
        encoding = self.prompt("Кодировка (по умолчанию utf-8): ").strip() or 'utf-8'
        print("Введите содержимое (окончание 'end' или пустая строка):")
        lines = []
        while True:
            line = self.prompt('')
            if line.strip().lower() in ('end', '::end') or line == '':
                break
            lines.append(line)
        initial_text = '\n'.join(lines) + ('\n' if lines else '')
        tf.create(initial_text=initial_text, encoding=encoding, overwrite=True)
        print(f"Файл '{tf.path}' создан.")

    def read_file_flow(self):
        tf = self.choose_file()
        if not tf or not tf.exists():
            print("Файл не найден.")
            return
        encoding = self.prompt("Кодировка (по умолчанию utf-8): ").strip() or 'utf-8'
        lines_per_page_str = self.prompt("Строк на страницу (по умолчанию 25): ").strip()
        lines_per_page = int(lines_per_page_str) if lines_per_page_str.isdigit() else 25

        for start_line, page in tf.read_paged(lines_per_page=lines_per_page, encoding=encoding, errors='replace'):
            for i, line in enumerate(page, start=start_line):
                print(f"{i:6}: {line}")
            cont = self.prompt("-- Enter для продолжения, 'q' для выхода: ").strip().lower()
            if cont == 'q':
                break

    def append_flow(self):
        tf = self.choose_file()
        if not tf:
            return
        encoding = self.prompt("Кодировка (по умолчанию utf-8): ").strip() or 'utf-8'
        print("Введите текст (окончание 'end' или пустая строка):")
        lines = []
        while True:
            line = self.prompt('')
            if line.strip().lower() in ('end', '::end') or line == '':
                break
            lines.append(line)
        text = '\n'.join(lines) + ('\n' if lines else '')
        tf.append(text, encoding=encoding)
        print("Текст добавлен.")

    def clear_flow(self):
        tf = self.choose_file()
        if not tf or not tf.exists():
            print("Файл не найден.")
            return
        confirm = self.prompt("Для очистки введите 'CLEAR': ")
        if confirm == 'CLEAR':
            tf.clear()
            print("Файл очищен.")

    def search_replace_flow(self):
        tf = self.choose_file()
        if not tf or not tf.exists():
            print("Файл не найден.")
            return
        find_text = self.prompt("Найти: ")
        replace_text = self.prompt("Заменить на: ")
        encoding = self.prompt("Кодировка (по умолчанию utf-8): ").strip() or 'utf-8'
        cs = self.prompt("Учитывать регистр? (Y/n): ").strip().lower()
        case_sensitive = not (cs == 'n')
        replacements = tf.search_and_replace(find_text, replace_text, encoding=encoding, case_sensitive=case_sensitive)
        print(f"Сделано замен: {replacements}")

    def analyze_flow(self):
        tf = self.choose_file()
        if not tf or not tf.exists():
            print("Файл не найден.")
            return
        encoding = self.prompt("Кодировка (по умолчанию utf-8): ").strip() or 'utf-8'
        report_path = self.prompt("Путь к отчету (по умолчанию <имя>_report.txt): ").strip()
        if not report_path:
            report_path = tf.path + "_report.txt"
        analyzer = TextAnalyzer(tf)
        analyzer.write_report(report_path, encoding=encoding)
        print(f"Анализ сохранен в {report_path}")

    def convert_encoding_flow(self):
        src = self.prompt("Исходный файл: ").strip()
        dst = self.prompt("Файл назначения: ").strip()
        src_enc = self.prompt("Исходная кодировка (по умолчанию cp1251): ").strip() or 'cp1251'
        dst_enc = self.prompt("Целевая кодировка (по умолчанию utf-8): ").strip() or 'utf-8'
        FileConverter.convert_encoding(src, dst, src_encoding=src_enc, dst_encoding=dst_enc, errors='replace')
        print(f"Файл сконвертирован: {src} → {dst}")

    def show_menu(self):
        print("\n=== Менеджер текстовых файлов ===")
        print("1) Создать новый файл")
        print("2) Читать файл (постранично)")
        print("3) Добавить текст в файл")
        print("4) Очистить содержимое файла")
        print("5) Поиск и замена текста")
        print("6) Анализ файла (символы, слова, строки)")
        print("7) Конвертация кодировок")
        print("0) Выход")

    def run(self):
        while self.running:
            self.show_menu()
            choice = self.prompt("Выберите действие: ").strip()
            if choice == '1':
                self.create_file_flow()
            elif choice == '2':
                self.read_file_flow()
            elif choice == '3':
                self.append_flow()
            elif choice == '4':
                self.clear_flow()
            elif choice == '5':
                self.search_replace_flow()
            elif choice == '6':
                self.analyze_flow()
            elif choice == '7':
                self.convert_encoding_flow()
            elif choice == '0':
                print("Выход из программы.")
                self.running = False
            else:
                print("Неверный выбор.")
