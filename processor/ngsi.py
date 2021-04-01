from config.settings import URL_BROKER, SCOPE
from config.logging_conf import LoggingConf
from pytz import timezone
from pandas import read_csv, to_datetime, read_excel
from requests import post
from logging import error, info, debug
from time import sleep
from processor.payload import Payload

__author__ = 'Fernando López'


class NGSI(LoggingConf):
    def __init__(self, loglevel):
        super(NGSI, self).__init__(loglevel=loglevel, log_file='f4w-challenge-milan.log')

        self.entityId = ""
        self.propertyName = ""

        self.headersPost = {
            'Content-Type': 'application/ld+json'
        }

        self.url_entities = URL_BROKER + '/ngsi-ld/v1/entities'
        self.url_entities_op = URL_BROKER + '/ngsi-ld/v1/entityOperations/update'

        self.timezone_UTC = timezone('UTC')
        self.file_type = 0
        self.payload = Payload()

    def set_file(self, filename):
        """
        Extract the Sensor ID and the property from the filename
        :param filename: The filename
        :return: The Entity Id and the property
        """
        if self.file_type == 0:
            # We get the SN, name and placement data from the name
            filename = filename.split("_")
            self.payload.fix_temp_data(name=filename[1],
                                       serial_number=filename[0],
                                       placement=filename[2].split(".")[0],
                                       type_class=self.file_type)
        elif self.file_type == 1:
            # We get the name from the filename
            filename = filename.split("_")
            self.payload.fix_temp_data(name=filename[0],
                                       serial_number="",
                                       placement="",
                                       type_class=self.file_type)
        elif self.file_type == 2:
            self.payload.fix_temp_data(name="",
                                       serial_number="",
                                       placement="",
                                       type_class=self.file_type)

    def process(self, file, file_type):
        """
        Process the csv and excel files and send the data to the Context Broker
        :param file: Name of the excel or csv file to process
        :param file_type: Type of sensor data
                    0 -> Temperature sensor data (csv)
                    1 -> Rain Gauge sensor data (csv)
                    2 -> Level meter sensor data (xlsx)
        :return:
        """
        info(f"Starting process of file: {file[0]}")

        self.file_type = file_type

        # Set the filename to extract EntityId and Property name
        self.set_file(filename=file[0])

        if self.file_type == 0:
            self.process_temp_csv(file=file[1])
        elif self.file_type == 1:
            self.process_rg_csv(file=file[1])
        elif self.file_type == 2:
            self.process_level_excel(file=file[1])

    def process_rg_csv(self, file):
        # Read content of the file
        df = read_csv(filepath_or_buffer=file, sep=';')

        # Rename the columns name
        df.columns = ['Date', 'Time', "Measure"]

        # Create a column with Date + Time and transform to datetime
        df['DateTime'] = df['Date'] + " " + df['Time']
        df['DateTime'] = to_datetime(df['DateTime'], format='%m/%d/%y %I:%M:%S %p', dayfirst=True, utc=True)

        # Sort the data by DateTime
        df = df.sort_values(by=['DateTime'])

        # First record of a measure will be uploaded as a CREATE,
        # then other records will be uploaded as a UPDATE
        row_1 = df[:1]
        self.create(date_observed=row_1['DateTime'].values[0], measure=row_1['Measure'].values[0])

        # Get the last values of the csv file: UPDATE
        last = df.tail(len(df.index) - 1)

        # Iterating over the Dataframe
        try:
            [self.update(date_observed=row.DateTime.to_datetime64(), measure=row.Measure)
             for row in last.itertuples()]

        except ValueError as e:
            error("There was a problem parsing the csv data")

    def process_level_excel(self, file):
        # Read content of the file
        df = read_excel(io=file)

        # Rename the columns name:
        # Time -> DateTime
        # Стойност -> Level
        # Статус -> Status
        # Качество -> Quality
        # причина -> a (To be discarded)
        # статус -> b (To be discarded)
        # Suppression Type -> c (to be discarded)
        #
        #     ignoreColLab: [
        #         'причина', 'статус', 'Suppression Type', 'Coupler Attached (LGR S/N: 10078375)',
        #         'Host Connected (LGR S/N: 10078375)', 'End Of File (LGR S/N: 10078375)', '#'
        #     ],
        df.columns = ['DateTime', 'Level', 'Status', 'Quality', 'a', 'b', 'c']

        # Ignore columns 'a', 'b', 'c'
        df = df[['DateTime', 'Level', 'Status', 'Quality']]

        # Need to process the data of each column to have proper values.
        # Datetime:   const d = date.parse(entity.dateObserved.value, "D.M.YYYY г. HH:mm:ss.SSS ч.");
        df['DateTime'] = to_datetime(df['DateTime'], format='%d.%m.%Y г. %H:%M:%S.%f ч.', dayfirst=True, utc=True)

        # Level:      entity.value.value.substring(0, entity.value.value.length - 2).replace(",", ".")
        df['Level'] = df['Level'].str[:4].replace(',', '.', regex=True).astype(float)

        # Status:     'Нормално ниво': 'Normal Level'
        df.loc[df['Status'] == 'Нормално ниво', 'Status'] = 'Normal Level'

        # Quality:    'Добро': 'Good'
        df.loc[df['Quality'] == 'Добро', 'Quality'] = 'Good'

        # Sort the data by DateTime
        df = df.sort_values(by=['DateTime'])

        # First record of a measure will be uploaded as a CREATE,
        # then other records will be uploaded as a UPDATE
        row_1 = df[:1]
        self.create(date_observed=row_1['DateTime'].values[0],
                    measure=row_1['Level'].values[0],
                    status=row_1['Status'].values[0],
                    quality=row_1['Quality'].values[0])

        # Get the last values of the csv file: UPDATE
        last = df.tail(len(df.index) - 1)

        # Iterating over the Dataframe
        try:
            [self.update(date_observed=row.DateTime.to_datetime64(),
                         measure=row.Level,
                         status=row_1['Status'].values[0],
                         quality=row_1['Quality'].values[0])

             for row in last.itertuples()]

        except ValueError as e:
            error("There was a problem parsing the csv data")

    def process_temp_csv(self, file):
        # Read content of the file
        df = read_csv(filepath_or_buffer=file, sep=',', skiprows=1, usecols=[0, 1, 2])

        # Rename the columns name
        df.columns = ['#', 'DateTime', "Measure"]

        # Create a column with Date + Time and transform to datetime
        df['DateTime'] = to_datetime(df['DateTime'], format='%m.%d.%y %I:%M:%S %p', dayfirst=True, utc=True)

        # Sort the data by DateTime OJO THERE IS A PROBLEM HERE... mm-dd-yy
        df = df.sort_values(by=['DateTime'])

        # First record of a measure will be uploaded as a CREATE,
        # then other records will be uploaded as a UPDATE
        row_1 = df[:1]
        self.create(date_observed=row_1.DateTime.values[0], measure=row_1.Measure.values[0])

        # Get the last values of the csv file: UPDATE
        last = df.tail(len(df.index) - 1)

        # Iterating over the Dataframe
        try:
            [self.update(date_observed=row.DateTime.to_datetime64(), measure=row.Measure)
             for row in last.itertuples()]
        except ValueError as e:
            error("There was a problem parsing the csv data")

    def create(self, date_observed, measure, status='', quality=''):
        _, data = self.payload.get_data(date_observed=date_observed, measure=measure, status=status, quality=quality)

        debug(f"Create: Data to be uploaded:\n {data}\n")

        # CREATE
        info('Creating ...')
        r = post(self.url_entities, json=data, headers=self.headersPost)
        info(f'Create Status: [{r.status_code}]')

        # Wait some time to proceed with the following
        sleep(SCOPE)

    def update(self, date_observed, measure, status='', quality=''):
        _, data = self.payload.get_data(date_observed=date_observed, measure=measure, status=status, quality=quality)

        debug(f"Update: Data to be uploaded:\n {data}\n")

        # PATCH
        info('Updating ...')
        r = post(self.url_entities_op, json=[data], headers=self.headersPost)
        info(f'Update Status: [{r.status_code}]')

        # Wait some seconds to proceed with the following request
        sleep(SCOPE)
