from pybuilder.core import use_plugin, init

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.pylint")
use_plugin("python.distutils")
use_plugin("python.pydev")
use_plugin('copy_resources')
use_plugin("python.coverage")

name = 'python-icinga2jira-plugin'
version = '0.1.0'
summary = 'Icinga plugin for sending alarming tickets to Jira'

default_task = ["analyze", "publish"]


@init
def set_properties(project):
    project.build_depends_on("pylint")
    project.build_depends_on("mock")
    project.build_depends_on("docopt")
    project.build_depends_on("jira-python")
    project.build_depends_on("jinja2")
    project.set_property('copy_resources_target', '$dir_dist')
    project.get_property('copy_resources_glob').extend(['setup.cfg'])
    project.install_file('/usr/lib64/icinga/plugins', 'icinga2jira.py')


@init(environments='teamcity')
def set_properties_for_teamcity_builds(project):
    import os
    project.version = '%s-%s' % (project.version, os.environ.get('BUILD_NUMBER', 0))
    project.default_task = ['install_dependencies', 'publish']
