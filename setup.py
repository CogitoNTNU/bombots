from setuptools import setup

setup(
    name='bombots',
    version='1.0',
    description='Bombots environment',
    author='Jonathan Jorgensen',
    author_email='jonathan.jorgensen@cogito-ntnu.no',
    packages=['bombots'],
    package_data={'bombots': ['res/bb_sprites.png']},
    include_package_data=True,
    install_requires=['numpy', 'pygame', 'gym'],
)