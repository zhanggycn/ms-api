from setuptools import setup, find_packages
setup(
    name="ms-api",
    version="0.1",
    author="zhanggy",
    author_email="zhanggy_cn@gmail.com",
    description="This is an Example for Sanic",
    license="MIT",
    keywords="sanic micro service",
    url="https://github.com/songcser/sanic-ms",   # project home page, if any
    packages=find_packages(),

    install_requires=[
        'sanic>=0.7.0',
        'uvloop>=0.8.0',
        'peewee>=3.0.1',
        'psycopg2>=2.7.1',
        'asyncpg>=0.11.0',
        'aiohttp>=2.0.7',
        'futures==3.1.1',
        'opentracing==1.2.2',
        'basictracer>=2.2.0',
        'pyyaml>=3.12',
    ],
    package_data={
        'ms-api': ['*.py', '*.yml'],
    },
)
