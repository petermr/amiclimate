welcome @Kruthi rao try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# with open('requirements.txt') as f:
#    required = f.read().splitlines()

with open('README.md') as readme_file:
   readme = readme_file.read()

long_desc = """
climate  is a commandline/GUI-based tool for analysing documants on climate
in XML, TXT or PDF. It splits them into semantic sections which are searchable, transformable and can
be further processed by standard Python and other tools. 
"""

requirements = [

]

setup(
    name='climate',
    url='https://github.com/petermr/amiclimate',
    version='0.0.1a2',
    description='processes UN/IPCC and UNFCCC documents',
    long_description_content_type='text/markdown',
    long_description=readme,
    author="Peter Murray-Rust",
    author_email='petermurrayrust@googlemail.com',
    license='Apache2',
    install_requires=requirements,
    include_package_data=True,
    zip_safe=False,
    keywords='text and data mining',
    packages=[
        'climate'
    ],
    package_dir={'climate': 'climate'},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.8',
    ],
    entry_points={
        'console_scripts': [
            'climate=climate.amix:main',
        ],
    },
    python_requires='>=3.7',
)