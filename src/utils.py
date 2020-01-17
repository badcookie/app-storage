from zipfile import ZipFile
from functools import reduce


def get_package_size_bytes(package: 'ZipFile') -> int:
    files = package.filelist
    return reduce(
        lambda acc, file: acc + file.file_size,
        files, 0
    )


def mb_to_bytes(mb: int) -> int:
    return mb * 1024 * 1024
