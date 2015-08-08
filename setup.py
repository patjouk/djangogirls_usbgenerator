from distutils.core import setup
setup(
  name = 'djangogirls_usbgenerator',
  packages = ['djangogirls_usbgenerator'], # this must be the same as the name above
  version = '0.2',
  description = 'USB generator is a script to download everything you need for Django Girls workshop in case there is no Internet.',
  author = 'Lucie Daeye',
  author_email = 'lucie.daeye@gmail.com',
  url = 'https://github.com/patjouk/djangogirls_usbgenerator', # use the URL to the github repo
  keywords = ['Django Girls'], # arbitrary keywords
  classifiers = [],
  entry_points = {
    'console_scripts': ['djangogirls_usbgenerator=djangogirls_usbgenerator.generator:download_steps'],
  },
  install_requires=[
      'requests',
      'clint',
      'pyfiglet',
      'future'
  ],
)
