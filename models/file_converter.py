import codecs


class FileConverter:
    """Класс для конвертации файлов между кодировками."""

    @staticmethod
    def convert_encoding(src_path: str, dst_path: str, src_encoding: str = 'cp1251', dst_encoding: str = 'utf-8', errors: str = 'strict') -> None:
        with codecs.open(src_path, 'r', encoding=src_encoding, errors=errors) as src:
            with codecs.open(dst_path, 'w', encoding=dst_encoding, errors=errors) as dst:
                for line in src:
                    dst.write(line)
