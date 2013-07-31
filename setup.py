
from setuptools import setup

from salesman import about
setup(
     name='SalesMan',
     version=about.Version,
     packages=['salesman','salesman.lib','salesman.lib.gui',
                'salesman.plugins','salesman.lib.gui.autogen'],
     package_data = {'salesman':['plugins/*.yapsy-plugin']},
     license='GPLv3',
     include_package_data = True,
     scripts=['bin/salesman'],
     url='https://github.com/miheerdew/SalesMan/',
     long_desctiption=open('README.txt').read(),
     author='Miheer Dewaskar',
     author_email='miheerdew@gmail.com',
     description=about.Description,
     install_requires=[
         "wxpython == 2.8",
         "sqlalchemy == 0.8",
         "yapsy == 1.10"
     ],

)
