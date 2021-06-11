"""
kastle
~~~~~~

A web framework for Python that prioritizes simplicity.

:copyright: (c) 2021-present kyomi
:license: MIT, see LICENSE for more details
"""

__title__ = 'kastle'
__author__ = 'kyomi'
__license__ = 'MIT'
__copyright__ = 'Copyright 2021-present kyomi'
__version__ = '0.1.0a'


from collections import namedtuple

from .core import create_app
from .router import Router


VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')
version_info = VersionInfo(major=0, minor=1, micro=0, releaselevel='alpha', serial=0)