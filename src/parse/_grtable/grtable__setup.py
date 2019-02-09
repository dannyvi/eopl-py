from distutils.core import setup, Extension

setup(name='grtable',
      version='1.0',
      ext_modules=[Extension('grtable', ['grtable.c',
                                         'symbol.c',
                                         'grammar.c',
                                         'closure.c',
                                         'collection.c',
                                         'firstsets.c',
                                         'statemap.c',
                                         ])]
      )
