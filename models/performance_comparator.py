import time

class PerformanceComparator:
    """Сравнение скорости копирования файлов с буферизацией и без."""

    @staticmethod
    def copy_unbuffered(src: str, dst: str, chunk_size: int = 1024):
        """Копирование без буферизации (через обычный open)."""
        start = time.perf_counter()
        with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
            while chunk := fsrc.read(chunk_size):
                fdst.write(chunk)
        end = time.perf_counter()
        return end - start

    @staticmethod
    def copy_buffered(src: str, dst: str, buffer_size: int = 8192):
        """Копирование с буферизацией (BufferedReader / BufferedWriter)."""
        import io
        start = time.perf_counter()
        with open(src, 'rb') as raw_in, open(dst, 'wb') as raw_out:
            with io.BufferedReader(raw_in, buffer_size=buffer_size) as reader, \
                 io.BufferedWriter(raw_out, buffer_size=buffer_size) as writer:
                while chunk := reader.read(buffer_size):
                    writer.write(chunk)
        end = time.perf_counter()
        return end - start

    @staticmethod
    def compare(src: str, unbuffered_dst: str, buffered_dst: str):
        t1 = PerformanceComparator.copy_unbuffered(src, unbuffered_dst)
        t2 = PerformanceComparator.copy_buffered(src, buffered_dst)
        print("\n=== Результаты сравнения ===")
        print(f"Без буферизации: {t1:.4f} сек")
        print(f"С буферизацией : {t2:.4f} сек")
        print(f"Ускорение: {t1/t2:.2f}x быстрее с буферизацией" if t2 > 0 else "")
