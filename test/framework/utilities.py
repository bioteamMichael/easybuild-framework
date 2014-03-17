##
# Copyright 2012-2014 Ghent University
#
# This file is part of EasyBuild,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
# the Hercules foundation (http://www.herculesstichting.be/in_English)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# http://github.com/hpcugent/easybuild
#
# EasyBuild is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# EasyBuild is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with EasyBuild.  If not, see <http://www.gnu.org/licenses/>.
##
"""
Various test utility functions.

@author: Kenneth Hoste (Ghent University)
"""

import os
import re
import sys
import tempfile
from unittest import TestCase, TestLoader, main
from vsc import fancylogger

import easybuild.tools.options as eboptions
from easybuild.tools import config


class EnhancedTestCase(TestCase):
    """Enhanced test case, provides extra functionality (e.g. an assertErrorRegex method)."""

    def assertErrorRegex(self, error, regex, call, *args, **kwargs):
        """Convenience method to match regex with the expected error message"""
        try:
            call(*args, **kwargs)
            str_kwargs = ', '.join(['='.join([k,str(v)]) for (k,v) in kwargs.items()])
            str_args = ', '.join(map(str, args) + [str_kwargs])
            self.assertTrue(False, "Expected errors with %s(%s) call should occur" % (call.__name__, str_args))
        except error, err:
            if hasattr(err, 'msg'):
                msg = err.msg
            elif hasattr(err, 'message'):
                msg = err.message
            elif hasattr(err, 'args'):  # KeyError in Python 2.4 only provides message via 'args' attribute
                msg = str(err.args[0])
            else:
                msg = str(err)
            self.assertTrue(re.search(regex, msg), "Pattern '%s' is found in '%s'" % (regex, msg))

    def setUp(self):
        """Set up testcase."""
        self.log = fancylogger.getLogger("EasyConfigTest", fname=False)
        self.cwd = os.getcwd()

        self.orig_paths = {}
        for path in ['buildpath', 'installpath', 'sourcepath']:
            self.orig_paths[path] = os.environ.get('EASYBUILD_%s' % path.upper(), None)

        os.environ['EASYBUILD_SOURCEPATH'] = os.path.join(os.path.dirname(__file__), 'easyconfigs')
        os.environ['EASYBUILD_BUILDPATH'] = tempfile.mkdtemp()
        os.environ['EASYBUILD_INSTALLPATH'] = tempfile.mkdtemp()
        init_config()

    def tearDown(self):
        """Clean up after running testcase."""
        os.chdir(self.cwd)

        for path in ['buildpath', 'installpath', 'sourcepath']:
            if self.orig_paths[path] is not None:
                os.environ['EASYBUILD_%s' % path.upper()] = self.orig_paths[path]
            else:
                del os.environ['EASYBUILD_%s' % path.upper()]
        init_config()


def init_config():
    """(re)initialize configuration"""
    # initialize configuration so config.get_modules_tool function works
    eb_go = eboptions.parse_options()
    config.init(eb_go.options, eb_go.get_options_by_section('config'))


def find_full_path(base_path, trim=(lambda x: x)):
    """
    Determine full path for given base path by looking in sys.path and PYTHONPATH.
    trim: a function that takes a path and returns a trimmed version of that path
    """

    full_path = None

    pythonpath = os.getenv('PYTHONPATH')
    if pythonpath:
        pythonpath = pythonpath.split(':')
    else:
        pythonpath = []
    for path in sys.path + pythonpath:
        tmp_path = os.path.join(trim(path), base_path)
        if os.path.exists(tmp_path):
            full_path = tmp_path
            break

    return full_path
