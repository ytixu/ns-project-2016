#!/usr/bin/env python

from distutils.core import setup

setup(
	name='hermes',
	version='0.1',
	description='',
	author='Yi Tian Xu',
	author_email='yi.t.xu@mail.mcgill.ca',
	url='',
	install_requires = ['networkx'],
	packages=['hermes', 'test'],
)