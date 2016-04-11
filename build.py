from pybuilder.core import init, use_plugin


use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.coverage")
use_plugin("python.install_dependencies")
use_plugin("python.distutils")


default_task = "publish"


@init
def set_dependencies(project):
    # Build dependencies
    project.build_depends_on('mockito')

    # Runtime dependencies
    project.depends_on("pyusb")
    project.depends_on("Pillow")
    project.depends_on("qrcode")

@init
def set_properties(project):
    project.set_property('coverage_exceptions',['escpos.USB'])
