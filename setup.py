from setuptools import setup, Extension
try:
	from Cython.Build import cythonize
except:
	cythonize=False


import os



setup(name='SchemePy',
      version='1.1.04',
      description='R5RS scheme interpreter, supporting hygenic macros and full call/cc',
      author='Logan Perkins',
      author_email='perkins@flyingjnl.net',
      url='https://github.com/perkinslr/schemepy',
      packages=['scheme'],
      ext_modules = cythonize("scheme/*.pyx") if cythonize else None,
      requires = ['zope.interface'],
      data_files = [[os.path.join('share','schemepy','stdlib'),[os.path.join('stdlib', i) for i in os.listdir('stdlib')]]],
      scripts = ['scripts/schemepy'],
      license = "LGPL",
      keywords = "scheme r5rs define-syntax call/cc",
      long_description=open('README.md').read(),

     )


