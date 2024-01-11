from distutils.core import setup
import os
my_path=os.path.join('dictionary.py')
import py2exe

setup(console=[my_path])