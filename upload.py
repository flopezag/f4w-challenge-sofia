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
from config.settings import LOGLEVEL, FILES
from processor.multi_thread import ThreadMgmt
from concurrent.futures import ThreadPoolExecutor


if __name__ == '__main__':
    '''
    Main: Load file(s) and upload content to Context Broker
    '''
    thread = ThreadMgmt(loglevel=LOGLEVEL)

    sensors_data = [(FILES[0], 0), (FILES[1], 0), (FILES[2], 1), (FILES[3], 2)]

    # Multithread code to send at the same time measurements from 2 temp sensors (0, 1) type 0,
    # 1 rain gauge (2) type 1, and 1 level meter (3) type 2
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(thread.thread_function, sensors_data)
