import copy
import datetime
from datetime import timedelta
import fnmatch
import ipaddress
import logging
import operator
import re
import os
import json

from dateutil.tz import tzutc
from dateutil.parser import parse
from distutils import version
import jmespath

from c7n.element import Element
from c7n.exceptions import PolicyValidationError
from c7n.executor import ThreadPoolExecutor
from c7n.registry import PluginRegistry
from c7n.resolver import ValuesFrom
from c7n.utils import set_annotation, type_schema, parse_cidr
from c7n.manager import iter_filters
from c7n.filters.core import Filter
from c7n.filters.core import OPERATORS
from c7n.filters.core import ValueFilter
from c7n.exceptions import PolicyValidationError, ClientError
from c7n.utils import local_session, chunks
from concurrent.futures import as_completed




