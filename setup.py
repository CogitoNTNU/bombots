from setuptools import setup

setup(
   name='bombots',
   version='1.0',
   description='Bombots environment',
   author='Jonathan Jørgensen',
   author_email='jonathan.jorgensen@cogito-ntnu.no',
   packages=['bombots'],
   install_requires=['numpy', 'pygame', 'gym'],
)