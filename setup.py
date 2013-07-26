from distutils.core import setup
setup(
     name='SalesMan',
     version=open('VERSION.txt').read().strip(),
     packages=['salesman','salesman.lib','salesman.lib.gui',
                                'salesman.lib.gui.autogen'],
     package_data = {'salesman':['plugins/*.*']},
     license='GPLv3',
     include_package_data = True,
     scripts=['bin/salesman'],
     url='https://github.com/miheerdew/SalesMan/',
     long_desctiption=open('README.txt').read(),
     author='Miheer Dewaskar',
     author_email='miheerdew@gmail.com',
     description='Sales Manager',
     install_requires=[
         "wxpython == 2.8",
         "sqlalchemy >= 0.8",
     ],

)
