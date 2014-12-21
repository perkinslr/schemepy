from setuptools import setup, Extension
try:
	from Cython.Build import cythonize
except:
	cythonize=False






setup(name='SchemePy',
      version='1.1',
      description='R5RS scheme interpreter, supporting hygenic macros and full call/cc',
      author='Logan Perkins',
      author_email='perkins@flyingjnl.net',
      url='https://github.com/perkinslr/schemepy',
      packages=['scheme'],
      ext_modules = cythonize("scheme/*.pyx") if cythonize else None,
      requires = ['zope.interface'],
      data_files = [['/usr/share/schemepy/stdlib',['scheme/builtins.scm']]],
      scripts = ['scripts/schemepy']
     )


