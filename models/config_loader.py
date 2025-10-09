import io

class ConfigLoader:
    """Загрузка конфигурации из текстового файла в формате key=value."""

    @staticmethod
    def load_config(path: str):
        config = {}

        # Открываем файл в бинарном режиме, чтобы использовать BufferedReader
        with open(path, 'rb') as raw_file:
            with io.BufferedReader(raw_file) as reader:
                for raw_line in reader:
                    # Декодируем байты в строку
                    line = raw_line.decode('utf-8').strip()
                    # Пропускаем пустые строки и комментарии
                    if not line or line.startswith('#'):
                        continue
                    # Разделяем по первому символу '='
                    if '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
        return config
