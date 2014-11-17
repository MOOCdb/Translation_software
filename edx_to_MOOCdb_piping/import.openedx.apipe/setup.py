import multiprocessing
from setuptools import setup, find_packages


test_requirements = ['mongomock>=1.0.1', 'sentinels>=0.0.6', 'nose>=1.0', 'python-dateutil>=2.2']

setup(
    name = "json_to_relation",
    version = "0.4",
    packages = find_packages(),

    # Dependencies on other packages:
    setup_requires   = ['nose>=1.1.2'],
    tests_require    = test_requirements,
    install_requires = ['ijson>=1.0', 
			'pymongo>=2.6.2', 
			#'pymysql3>=0.5', 
			'pymysql_utils>=0.49',
			'configparser>=3.3.0r2', 
			'argparse>=1.2.1', 
			'unidecode>=0.04.14', 
			'boto>=2.16.0',
			'python-daemon>=1.5.5'
			#'online_learning_computations>=0.30'
			] + test_requirements,

    # Unit tests; they are initiated via 'python setup.py test'
    #test_suite       = 'json_to_relation/test',
    test_suite       = 'nose.collector', 

    #data_files = [('pymysql_utils/data', datafiles)],

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
     #   '': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
     #   'hello': ['*.msg'],
    },

    # metadata for upload to PyPI
    author = "Andreas Paepcke",
    author_email = "paepcke@cs.stanford.edu",
    description = "Converts file with multiple JSON objects to one relational table.",
    license = "BSD",
    keywords = "json, relation, OpenEdX",
    url = "https://github.com/paepcke/json_to_relation",   # project home page, if any
)
