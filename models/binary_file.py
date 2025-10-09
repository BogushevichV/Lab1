import os
import hashlib
from typing import Generator, Optional, Tuple, Dict


class BinaryFile:
    """Класс для работы с бинарными файлами."""

    def __init__(self, path: str):
        self.path = path

    def exists(self) -> bool:
        return os.path.isfile(self.path)

    def create(self, data: bytes = b'', overwrite: bool = False) -> None:
        """Создание бинарного файла."""
        if self.exists() and not overwrite:
            raise FileExistsError(f"Файл '{self.path}' уже существует.")
        with open(self.path, mode='wb') as f:
            f.write(data)

    def read_bytes(self, offset: int = 0, size: Optional[int] = None) -> bytes:
        """Чтение байтов из файла."""
        with open(self.path, mode='rb') as f:
            f.seek(offset)
            if size is None:
                return f.read()
            return f.read(size)

    def write_bytes(self, data: bytes, offset: int = 0) -> None:
        """Запись байтов в файл."""
        with open(self.path, mode='r+b') as f:
            f.seek(offset)
            f.write(data)

    def append_bytes(self, data: bytes) -> None:
        """Добавление байтов в конец файла."""
        with open(self.path, mode='ab') as f:
            f.write(data)

    def get_size(self) -> int:
        """Получение размера файла."""
        return os.path.getsize(self.path)

    def calculate_checksum(self, algorithm: str = 'md5') -> str:
        """Вычисление контрольной суммы файла."""
        hash_obj = hashlib.new(algorithm)
        with open(self.path, mode='rb') as f:
            while chunk := f.read(8192):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()

    def read_chunks(self, chunk_size: int = 16) -> Generator[Tuple[int, bytes], None, None]:
        """Чтение файла по чанкам с указанием смещения."""
        offset = 0
        with open(self.path, mode='rb') as f:
            while chunk := f.read(chunk_size):
                yield (offset, chunk)
                offset += len(chunk)

    def find_bytes(self, pattern: bytes, max_results: int = -1) -> list:
        """Поиск байтовой последовательности в файле."""
        results = []
        data = self.read_bytes()
        start = 0
        while True:
            idx = data.find(pattern, start)
            if idx == -1:
                break
            results.append(idx)
            if max_results > 0 and len(results) >= max_results:
                break
            start = idx + 1
        return results

    def get_file_signature(self) -> bytes:
        """Получение первых байтов файла (сигнатура)."""
        return self.read_bytes(0, 16)

    def get_byte_distribution(self) -> Dict[int, int]:
        """Получение распределения байтов в файле."""
        distribution = {i: 0 for i in range(256)}
        data = self.read_bytes()
        for byte in data:
            distribution[byte] += 1
        return distribution

    def xor_encrypt_decrypt(self, key: bytes, output_path: str) -> None:
        """XOR шифрование/дешифрование."""
        key_len = len(key)
        with open(self.path, mode='rb') as src:
            with open(output_path, mode='wb') as dst:
                idx = 0
                while chunk := src.read(8192):
                    encrypted = bytearray()
                    for byte in chunk:
                        encrypted.append(byte ^ key[idx % key_len])
                        idx += 1
                    dst.write(bytes(encrypted))

    def shift_bytes(self, shift: int, output_path: str) -> None:
        """Сдвиг байтов (Caesar cipher для байтов)."""
        with open(self.path, mode='rb') as src:
            with open(output_path, mode='wb') as dst:
                while chunk := src.read(8192):
                    shifted = bytes([(byte + shift) % 256 for byte in chunk])
                    dst.write(shifted)

    def invert_bytes(self, output_path: str) -> None:
        """Инвертирование всех байтов (NOT operation)."""
        with open(self.path, mode='rb') as src:
            with open(output_path, mode='wb') as dst:
                while chunk := src.read(8192):
                    inverted = bytes([~byte & 0xFF for byte in chunk])
                    dst.write(inverted)

    def copy_to(self, dst_path: str, callback=None) -> None:
        """Побайтовое копирование с возможностью отслеживания прогресса."""
        total_size = self.get_size()
        copied = 0
        chunk_size = 8192

        with open(self.path, mode='rb') as src:
            with open(dst_path, mode='wb') as dst:
                while chunk := src.read(chunk_size):
                    dst.write(chunk)
                    copied += len(chunk)
                    if callback:
                        callback(copied, total_size)

    def compare_with(self, other_path: str) -> Dict:
        """Сравнение двух файлов побайтово."""
        other_file = BinaryFile(other_path)

        if not other_file.exists():
            return {'equal': False, 'reason': 'Второй файл не существует'}

        size1 = self.get_size()
        size2 = other_file.get_size()

        if size1 != size2:
            return {
                'equal': False,
                'reason': 'Разные размеры',
                'size1': size1,
                'size2': size2
            }

        differences = []
        chunk_size = 8192

        with open(self.path, mode='rb') as f1:
            with open(other_path, mode='rb') as f2:
                offset = 0
                while True:
                    chunk1 = f1.read(chunk_size)
                    chunk2 = f2.read(chunk_size)

                    if not chunk1:
                        break

                    for i in range(len(chunk1)):
                        if chunk1[i] != chunk2[i]:
                            differences.append({
                                'offset': offset + i,
                                'byte1': chunk1[i],
                                'byte2': chunk2[i]
                            })
                            if len(differences) >= 100:  # Ограничение
                                break

                    offset += len(chunk1)
                    if len(differences) >= 100:
                        break

        return {
            'equal': len(differences) == 0,
            'differences': differences,
            'total_checked': size1
        }

    def rename(self, new_path: str) -> None:
        """Переименование файла."""
        os.rename(self.path, new_path)
        self.path = new_path

    def delete(self) -> None:
        """Удаление файла."""
        if self.exists():
            os.remove(self.path)