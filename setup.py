from setuptools import setup, find_packages

setup(
    name='jessilver-django-messages',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True, # IMPORTANTE: Inclui static e templates
    install_requires=['django>=3.2'],
    description='Sistema de mensagens modais globais via sessão para Django.',
    author='Jessé',
)