from setuptools import setup, find_packages

setup(
    name='jessilver-django-messages',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,  # Essencial: lê as regras do MANIFEST.in
    install_requires=[
        'django>=3.2',
    ],
    author='Jessé',
    description='Sistema de mensagens modais sequenciais e seguras para Django',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    python_requires='>=3.8',
)