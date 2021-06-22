from pybuilder.core import Author, init, use_plugin


use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.coverage")
use_plugin("python.install_dependencies")
use_plugin("python.distutils")
use_plugin("python.flake8")
use_plugin("python.pylint")
use_plugin("python.sphinx")
use_plugin('pypi:pybuilder_header_plugin')

url = 'https://github.com/shantanubhadoria/python-printer-escpos'
description = 'Please visit {0} for more information!'.format(url)

authors = [Author('Shantanu Bhadoria', 'shantanu@cpan.org')]
license = 'Apache License, Version 2.0'
summary = 'Python interface for ESCPOS Printers'
version = '0.0.4'

default_task = ['analyze', 'publish']

@init
def set_dependencies(project):
    # Build dependencies
    project.build_depends_on('mockito')

    # Runtime dependencies
    project.depends_on("pyusb")
    project.depends_on("pyserial")
    project.depends_on("Pillow")
    project.depends_on("qrcode")

@init
def set_properties(project):
    project.set_property('coverage_exceptions',['escpos.connections','escpos.commandset.generic'])
    project.set_property('pybuilder_header_plugin_break_build', True)

    project.set_property('flake8_verbose_output', True)
    project.set_property('flake8_break_build', True)
    project.set_property('flake8_include_test_sources', True)


    project.set_property("sphinx_doc_author", "Shantanu Bhadoria")
    project.set_property("sphinx_doc_builder", "html")
    project.set_property("sphinx_project_name", project.name)
    project.set_property("sphinx_project_version", project.version)
    project.set_property("sphinx_source_dir", "docs")
    #project.set_property('pybuilder_header_plugin_expected_header', '#asda')
    #project.set_property('pybuilder_header_plugin_expected_header', open('header.py').read())
