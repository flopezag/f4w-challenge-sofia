# -*- coding: utf-8 -*-
##
# Copyright 2021 FIWARE Foundation, e.V.
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
from os.path import join, isfile
from os import listdir


class Files:
    def __init__(self, pwd, folders):
        self.pwd = pwd
        self.folders = folders

    def get_files(self):
        # Each folder has 3 different files:
        # <Sensor ID>_CSO_Occurrence.xlsx, occurrences of overflow data, type = 3
        # <Sensor ID>_SelectedVariables_temperature.xlsx, temperature data in the crest, type = 0
        # <Rain Gauge>_01_01_2021_to_01_05_2021.csv rain gauge measurement, type = 1
        sensors = list(map(lambda x: (x, join(self.pwd, x)), self.folders))

        files = [item for sublist in list(map(lambda x: self.check_file(x), sensors)) for item in sublist]

        return files

    @staticmethod
    def get_type(file):
        result = -1

        if "CSO_Occurrence" in file:
            result = 3
        elif "SelectedVariables_temperature" in file:
            result = 0
        elif "RG" in file:
            result = 1
        else:
            raise NameError('Filename not expected {}'.format(file))

        return result

    def check_file(self, file):
        out = [f for f in listdir(file[1]) if isfile(join(file[1], f))]

        # We need to check that these three files are contained or we produce an error
        out = [[f, self.get_type(f)] for f in out]

        # put the complete path to the files
        out = [[join(file[1], f[0]), f[1]] for f in out]

        return out
