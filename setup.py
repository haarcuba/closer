from setuptools import setup, find_packages

README = 'monitor and close remote SSH processes automatically'

requires = [ 'psutil',
             'flask',
             'requests',
             'pimped_subprocess>=2.2.0', ]
tests_require = [
        'pytest',
        ]

setup(name='closer',
      version='4.0.5',
      description=README,
      long_description=README,
      url='https://haarcuba.github.io/closer',
      classifiers=[
          "Programming Language :: Python",
          "Operating System :: POSIX :: Linux",
      ],
      author='Yoav Kleinberger',
      author_email='haarcuba@gmail.com',
      keywords='subprocess',
      packages=find_packages('source'),
      package_dir={'': 'source'},
      include_package_data=True,
      zip_safe=False,
      extras_require={
          'testing': tests_require,
      },
      install_requires=requires,
      entry_points={
          'console_scripts': [ 'closer3 = closer.closer3:main' ]
      },
      )
