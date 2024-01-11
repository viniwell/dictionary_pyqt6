from distutils.core import setup
import py2exe

setup(
    windows=['dictionary.py'],
    options={
        'py2exe': {
            'bundle_files': 1, # отключение отображения всех используемых файлов
            'compressed': True, # упаковка в ZIP-архив
        }
    },
    zipfile=None, # создание ZIP-архива с исполняемыми файлами
)