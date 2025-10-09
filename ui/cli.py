from models.text_file import TextFile
from models.file_converter import FileConverter
from models.text_analyzer import TextAnalyzer
from models.binary_file import BinaryFile
from models.hex_viewer import HexViewer
from models.binary_analyzer import BinaryAnalyzer
import os


class CLI:
    """Консольное меню с поддержкой текстовых и бинарных файлов."""

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

    def choose_binary_file(self):
        filename = self.prompt("Введите путь к файлу: ").strip()
        if not filename:
            print("Файл не указан.")
            return None
        return BinaryFile(filename)

    # ===== Текстовые файлы =====

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

    # ===== Бинарные файлы =====

    def create_binary_flow(self):
        bf = self.choose_binary_file()
        if not bf:
            return

        print("Выберите способ создания:")
        print("1) Пустой файл")
        print("2) Случайные байты")
        print("3) Ввести hex-строку")
        choice = self.prompt("Выбор: ").strip()

        data = b''
        if choice == '2':
            size_str = self.prompt("Размер в байтах: ").strip()
            if size_str.isdigit():
                import os as os_random
                data = os_random.urandom(int(size_str))
        elif choice == '3':
            hex_str = self.prompt("Введите hex-строку (например: 48656C6C6F): ").strip()
            try:
                data = bytes.fromhex(hex_str)
            except ValueError:
                print("Ошибка: неверная hex-строка")
                return

        bf.create(data, overwrite=True)
        print(f"Файл '{bf.path}' создан, размер: {len(data)} байт")

    def hex_view_flow(self):
        bf = self.choose_binary_file()
        if not bf or not bf.exists():
            print("Файл не найден.")
            return

        viewer = HexViewer(bf, bytes_per_line=16)

        # Показываем информацию о файле
        info = viewer.get_file_info()
        print(f"\n=== Информация о файле ===")
        print(f"Путь: {info['path']}")
        print(f"Размер: {info['size_formatted']}")
        print(f"Сигнатура: {info['signature']}")
        print(f"MD5: {info['md5']}")
        print(f"SHA1: {info['sha1']}")
        print(f"SHA256: {info['sha256']}\n")

        lines_per_page_str = self.prompt("Строк на страницу (по умолчанию 16): ").strip()
        lines_per_page = int(lines_per_page_str) if lines_per_page_str.isdigit() else 16

        for offset, page in viewer.view_all_paged(lines_per_page):
            for line in page:
                print(line)
            cont = self.prompt("-- Enter для продолжения, 'q' для выхода: ").strip().lower()
            if cont == 'q':
                break

    def binary_search_flow(self):
        bf = self.choose_binary_file()
        if not bf or not bf.exists():
            print("Файл не найден.")
            return

        hex_pattern = self.prompt("Введите паттерн для поиска (hex): ").strip()
        try:
            pattern = bytes.fromhex(hex_pattern)
        except ValueError:
            print("Ошибка: неверная hex-строка")
            return

        offsets = bf.find_bytes(pattern, max_results=100)

        if not offsets:
            print("Паттерн не найден.")
            return

        print(f"Найдено совпадений: {len(offsets)}")
        print("Смещения:")
        for i, offset in enumerate(offsets[:20], 1):
            print(f"  {i}. 0x{offset:08X} ({offset})")

        if len(offsets) > 20:
            print(f"  ... и еще {len(offsets) - 20} совпадений")

        # Показать hex-просмотр с контекстом
        show_context = self.prompt("\nПоказать hex-просмотр? (y/N): ").strip().lower()
        if show_context == 'y':
            viewer = HexViewer(bf)
            results = viewer.search_and_highlight(pattern, context_lines=2)
            for result in results[:5]:
                print(f"\n--- Найдено на offset 0x{result['offset']:08X} ---")
                for line in result['lines']:
                    print(line)

    def xor_encrypt_flow(self):
        bf = self.choose_binary_file()
        if not bf or not bf.exists():
            print("Файл не найден.")
            return

        output = self.prompt("Выходной файл: ").strip()
        if not output:
            print("Выходной файл не указан.")
            return

        key_input = self.prompt("Ключ (hex или текст, начните с 'hex:' для hex): ").strip()

        if key_input.startswith('hex:'):
            try:
                key = bytes.fromhex(key_input[4:])
            except ValueError:
                print("Ошибка: неверная hex-строка")
                return
        else:
            key = key_input.encode('utf-8')

        if not key:
            print("Ключ не может быть пустым.")
            return

        bf.xor_encrypt_decrypt(key, output)
        print(f"XOR шифрование выполнено: {bf.path} → {output}")

    def shift_bytes_flow(self):
        bf = self.choose_binary_file()
        if not bf or not bf.exists():
            print("Файл не найден.")
            return

        output = self.prompt("Выходной файл: ").strip()
        shift_str = self.prompt("Сдвиг (0-255): ").strip()

        if not shift_str.isdigit():
            print("Ошибка: сдвиг должен быть числом")
            return

        shift = int(shift_str) % 256
        bf.shift_bytes(shift, output)
        print(f"Байты сдвинуты на {shift}: {bf.path} → {output}")

    def invert_bytes_flow(self):
        bf = self.choose_binary_file()
        if not bf or not bf.exists():
            print("Файл не найден.")
            return

        output = self.prompt("Выходной файл: ").strip()
        bf.invert_bytes(output)
        print(f"Байты инвертированы: {bf.path} → {output}")

    def copy_file_flow(self):
        src = self.prompt("Исходный файл: ").strip()
        dst = self.prompt("Файл назначения: ").strip()

        if not src or not dst:
            print("Не указаны файлы.")
            return

        bf = BinaryFile(src)
        if not bf.exists():
            print("Исходный файл не найден.")
            return

        def progress_callback(copied, total):
            percent = (copied / total * 100) if total > 0 else 0
            bar_length = 40
            filled = int(bar_length * copied / total) if total > 0 else 0
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f"\r[{bar}] {percent:.1f}% ({copied}/{total} bytes)", end='', flush=True)

        bf.copy_to(dst, callback=progress_callback)
        print(f"\nФайл скопирован: {src} → {dst}")

    def compare_files_flow(self):
        file1 = self.prompt("Первый файл: ").strip()
        file2 = self.prompt("Второй файл: ").strip()

        bf1 = BinaryFile(file1)
        if not bf1.exists():
            print("Первый файл не найден.")
            return

        result = bf1.compare_with(file2)

        if result['equal']:
            print("Файлы идентичны.")
        else:
            print(f"Файлы различаются: {result.get('reason', 'Найдены различия')}")

            if 'size1' in result:
                print(f"  Размер файла 1: {result['size1']} байт")
                print(f"  Размер файла 2: {result['size2']} байт")

            if 'differences' in result and result['differences']:
                print(f"\nПервые различия (показано до 10):")
                for i, diff in enumerate(result['differences'][:10], 1):
                    print(f"  {i}. Offset 0x{diff['offset']:08X}: "
                          f"0x{diff['byte1']:02X} != 0x{diff['byte2']:02X}")

    def analyze_binary_flow(self):
        bf = self.choose_binary_file()
        if not bf or not bf.exists():
            print("Файл не найден.")
            return

        report_path = self.prompt("Путь к отчету (по умолчанию <имя>_binary_report.txt): ").strip()
        if not report_path:
            report_path = bf.path + "_binary_report.txt"

        analyzer = BinaryAnalyzer(bf)

        # Показываем краткую информацию
        print("\nАнализ файла...")
        analysis = analyzer.analyze_structure()

        print(f"Тип файла: {analysis['file_type']}")
        print(f"Размер: {analysis['size']} байт")
        print(f"Уникальных байтов: {analysis['unique_bytes']}/256")
        print(f"Энтропия: {analysis['entropy']:.4f}")

        analyzer.write_report(report_path)
        print(f"\nПолный отчет сохранен в {report_path}")

    def rename_file_flow(self):
        old_path = self.prompt("Текущий путь к файлу: ").strip()
        if not old_path:
            print("Файл не указан.")
            return

        bf = BinaryFile(old_path)
        if not bf.exists():
            print("Файл не найден.")
            return

        new_path = self.prompt("Новый путь к файлу: ").strip()
        if not new_path:
            print("Новый путь не указан.")
            return

        bf.rename(new_path)
        print(f"Файл переименован: {old_path} → {new_path}")

    def delete_file_flow(self):
        path = self.prompt("Путь к файлу для удаления: ").strip()
        if not path:
            print("Файл не указан.")
            return

        bf = BinaryFile(path)
        if not bf.exists():
            print("Файл не найден.")
            return

        # Показываем информацию о файле
        size = bf.get_size()
        print(f"Файл: {path}")
        print(f"Размер: {size} байт")

        confirm = self.prompt("Для удаления введите 'DELETE': ")
        if confirm == 'DELETE':
            bf.delete()
            print("Файл удален.")
        else:
            print("Отменено.")

    def show_menu(self):
        print("\n=== Менеджер файлов (текстовые и бинарные) ===")
        print("\n--- Текстовые файлы ---")
        print("1)  Создать новый файл")
        print("2)  Читать файл (постранично)")
        print("3)  Добавить текст в файл")
        print("4)  Очистить содержимое файла")
        print("5)  Поиск и замена текста")
        print("6)  Анализ файла (символы, слова, строки)")
        print("7)  Конвертация кодировок")
        print("\n--- Бинарные файлы ---")
        print("8)  Создать бинарный файл")
        print("9)  Hex-просмотр файла")
        print("10) Поиск байтовой последовательности")
        print("11) XOR шифрование/дешифрование")
        print("12) Сдвиг байтов")
        print("13) Инвертирование байтов")
        print("14) Копирование файла (с прогресс-баром)")
        print("15) Сравнение двух файлов")
        print("16) Анализ бинарного файла")
        print("\n--- Управление файлами ---")
        print("17) Переименование файла")
        print("18) Удаление файла")
        print("\n0)  Выход")

    def run(self):
        while self.running:
            self.show_menu()
            choice = self.prompt("\nВыберите действие: ").strip()

            # Текстовые файлы
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

            # Бинарные файлы
            elif choice == '8':
                self.create_binary_flow()
            elif choice == '9':
                self.hex_view_flow()
            elif choice == '10':
                self.binary_search_flow()
            elif choice == '11':
                self.xor_encrypt_flow()
            elif choice == '12':
                self.shift_bytes_flow()
            elif choice == '13':
                self.invert_bytes_flow()
            elif choice == '14':
                self.copy_file_flow()
            elif choice == '15':
                self.compare_files_flow()
            elif choice == '16':
                self.analyze_binary_flow()

            # Управление файлами
            elif choice == '17':
                self.rename_file_flow()
            elif choice == '18':
                self.delete_file_flow()

            elif choice == '0':
                print("Выход из программы.")
                self.running = False
            else:
                print("Неверный выбор.")