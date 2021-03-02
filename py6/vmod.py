"""
Python 3.7.3 (v3.7.3:ef4ec6ed12, Mar 25 2019, 22:22:05) [MSC v.1916 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.

>>> import vmod
>>> vmod.Woof
Getting Woof...
<class 'vmod.Woof'>

>>> vmod.Woof
Getting Woof...
<class 'vmod.Woof'>

>>> from vmod import Woof
Getting __spec__...
Getting __path__...
Getting Woof...

>>> from vmod import Woof
Getting __spec__...
Getting __path__...
Getting Woof...

>>> Woof
<class 'vmod.Woof'>

>>> vmod.Woof
Getting Woof...
<class 'vmod.Woof'>
"""
import sys
from types import ModuleType

class VerboseModule(ModuleType):
    def __repr__(self):
        return f'Verbose {self.__name__}'

    def __setattr__(self, attr, value):
        print(f'Setting {attr}...')
        super().__setattr__(attr, value)

    # def __getattr__(self, attr):

    def __getattribute__(self, attr):
        print(f'Getting {attr}...')
        if attr == 'Woof':
            return Woof
        return super().__getattribute__(attr)

class Woof(object):
    pass

sys.modules[__name__].__class__ = VerboseModule
