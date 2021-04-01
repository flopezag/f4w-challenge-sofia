# -*- coding: utf-8 -*-
##
# Copyright 2019 FIWARE Foundation, e.V.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
##
from config.logging_conf import LoggingConf
from config.settings import LOGLEVEL
from logging import info
from processor.ngsi import NGSI

import time


class ThreadMgmt(LoggingConf):
    def __init__(self, loglevel):
        super(ThreadMgmt, self).__init__(loglevel=loglevel, log_file='f4w-challenge-milan.log')
        self.ngsi = NGSI(loglevel=LOGLEVEL)

    def thread_function(self, data):
        info("Thread %s: starting", data[0][0])
        self.ngsi.process(file=data[0], file_type=data[1])
        info("Thread %s: finishing", data[0][0])
