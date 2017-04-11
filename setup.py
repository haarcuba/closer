from setuptools import setup, find_packages

README = 'close remote SSH processes automatically'

requires = [ 'psutil',
             'pimped_subprocess>=1.0.0', ]
tests_require = [
        'pytest',
        ]

setup(name='closer',
      version='1.1.0',
      description=README,
      long_description=README,
      url='https://github.com/haarcuba/closer',
      classifiers=[
          "Programming Language :: Python",
      ],
      author='Yoav Kleinberger',
      author_email='haarcuba@gmail.com',
      keywords='subprocess',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      extras_require={
          'testing': tests_require,
      },
      install_requires=requires,
      entry_points="""\
      [console_scripts]
      closer = closer.closer:main
      """,
      )
