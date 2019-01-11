from setuptools import setup, find_packages

setup(
    name = 'wsearch',
    version = '0.0.1.1',
    keywords='search engine, crawler',
    description = 'a search engine crwaler based on python, can be easily configed',
    license = 'Apache Licence 2.0',
    url = 'https://github.com/wvinzh/WutongSearch',
    author = 'wvinzh',
    author_email = 'wvinzh@qq.com',
    packages = find_packages(),
    include_package_data = True,
    platforms = 'any',
    install_requires = [
        'setuptools',
        'selenium',
        'pyyaml',
    ],
)