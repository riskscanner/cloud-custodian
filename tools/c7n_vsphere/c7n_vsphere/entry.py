# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

import logging
from c7n_vsphere.resources import (
    vm,
)

log = logging.getLogger('custodian.vsphere')

ALL = [
    vm]


def initialize_vsphere():
    """vsphere entry point
    """