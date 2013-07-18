from distutils.core import setup
setup(
     name='SalesMan',
     version=open('VERSION.txt').read().strip(),
     packages=['salesman','salesman.lib','salesman.lib.gui',
                                'salesman.lib.gui.autogen'],
     license='LICENSE.txt',
     scripts=['bin/salesman'],
     url='https://github.com/miheerdew/SalesMan/',
     long_desctiption=open('README.txt').read(),
     author='Miheer Dewaskar',
     author_email='miheerdew@gmail.com',
     description='Sales Manager',
     install_requires=[
         "wx == 2.8",
         "sqlalchemy >= 0.8",
     ],
     
)
