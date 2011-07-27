from setuptools import setup, find_packages
setup(
    name = "py-css",
    version = "0.1",
    packages = ['py_css'],

    # metadata for upload to PyPI
    author = "Wil Asche",
    author_email = "wil@wickedspiral.com",
    description = "CSS stream compressor",
    license = "MIT",
    keywords = "css minify",
    url = "http://github.com/tripadvisor/py-css",
    entry_points = '''
    [console_scripts]
    pycss = py_css:main
    ''',
)
