from config.settings import AT_CONTEXT, URL_BROKER, PROPERTIES, SCOPE
from config.logging_conf import LoggingConf
from pytz import timezone
from datetime import datetime
from pandas import read_csv
from requests import post
from logging import error, info, debug
from time import sleep

__author__ = 'Fernando López'


class NGSI(LoggingConf):
    def __init__(self, loglevel):
        super(NGSI, self).__init__(loglevel=loglevel, log_file='f4w-challenge-milan.log')

        self.entityId = ""
        self.propertyName = ""

        self.serial_number = ""
        self.placement = ""
        self.name = ""

        self.headersPost = {
            'Content-Type': 'application/ld+json'
        }

        self.url_entities = URL_BROKER + '/ngsi-ld/v1/entities'
        self.url_entities_op = URL_BROKER + '/ngsi-ld/v1/entityOperations/update'

        self.timezone_UTC = timezone('UTC')

    def set_file(self, filename, type):
        """
        Extract the Sensor ID and the property from the filename
        :param filename: The filename
        :return: The Entity Id and the property
        """
        if type == 0:
            # We get the SN, name and placement data from the name
            filename = filename.split("_")
            self.serial_number = filename[0]
            self.name = filename[1]
            self.placement = filename[2].split(".")[0]
        elif type == 1:
            # We get the name from the filename
            filename = filename.split("_")
            self.name = filename[0]

    def process(self, file, type):
        """
        Process the csv and excel files and send the data to the Context Broker
        :param file: Name of the excel or csv file to process
        :param type: Type of sensor data
                    0 -> Temperature sensor data (csv)
                    1 -> Rain Gauge sensor data (csv)
                    2 -> Level meter sensor data (xlsx)
        :return:
        """
        info(f"Starting process of file: {file[0]}")

        # Set the filename to extract EntityId and Property name
        self.set_file(filename=file[0], type=type)

        if type == 0:
            self.process_temp_csv(file=file[1])
        elif type == 1:
            self.process_rg_csv(file=file[1])
        elif type == 2:
            self.process_level_excel(file=file[1])

    def process_rg_csv(self, file):
        print("TBD")

    def process_level_excel(self, file):
        print("TBD")

    def process_temp_csv(self, file):
        # Read content of the file
        df = read_csv(filepath_or_buffer=file, sep=',', skiprows=1, usecols=[0, 1, 2])

        # Rename the columns name
        df.columns = ['#', 'DateTime', "Measure"]

        # Sort the data by DateTime
        df = df.sort_values(by=['DateTime'])

        # First record of a measure will be uploaded as a CREATE,
        # then other records will be uploaded as a UPDATE
        row_1 = df[:1]
        self.create(date_observed=row_1['DateTime'].values[0], measure=row_1['Measure'].values[0])

        # Get the last values of the csv file: UPDATE
        last = df.tail(len(df.index) - 1)

        # Iterating over two columns, use `zip`
        try:
            [self.update(date_observed=x, measure=y) for x, y in zip(last['DateTime'], last['Measure'])]
        except ValueError as e:
            error("There was a problem parsing the csv data")

    def __get_values__(self, date_observed, measure):
        # measure = float(measure.strip().replace(",", "."))
        date_observed = datetime.strptime(date_observed, '%d.%m.%y %I:%M:%S %p')
        date_observed = self.timezone_UTC.localize(date_observed).isoformat()

        return date_observed, measure

    def create(self, date_observed, measure):
        date_observed, measure = self.__get_values__(date_observed=date_observed, measure=measure)

        _, data = self.__temp_data__(date_observed=date_observed, measure=measure)

        debug(f"Create: Data to be uploaded:\n {data}\n")

        # CREATE
        info('Creating ...')
        # r = post(self.url_entities, json=data, headers=self.headersPost)
        info(f'Create Status: [{r.status_code}]')

        # Wait some time to proceed with the following
        sleep(SCOPE)

    def update(self, date_observed, measure):
        # it is not working...
        date_observed, measure = self.__get_values__(date_observed=date_observed, measure=measure)

        entity_id, data = self.__data__(date_observed=date_observed, measure=measure)

        debug(f"Update: Data to be uploaded:\n {data}\n")

        # PATCH
        info('Updating ...')
        # r = post(self.url_entities_op, json=[data], headers=self.headersPost)
        info(f'Update Status: [{r.status_code}]')

        # Wait some seconds to proceed with the following request
        sleep(SCOPE)

    def __temp_data__(self, date_observed, measure):
        date_observed = {
            "type": "Property",
            "value": {
                "@type": "DateTime",
                "@value": date_observed
            }
        }

        value = {
            "type": "Property",
            "value": measure,
            "unitCode": "CEL"
        }

        entity_id = "urn:ngsi-ld:Device:{}".format(self.serial_number)

        entity_type = "Device"

        category = {
            "type": "Property",
            "value": [
                "sensor"
            ]
        }

        controlledProperty = {
            "type": "Property",
            "value": [
                "temperature"
            ]
        }

        serialNumber = {
            "type": "Property",
            "value": self.serial_number
        }

        placement = {
            "type": "object",
            "properties": {
                "relativePosition": {
                    "type": "string",
                    "value": self.placement
                }
            }
        }

        name = {
            "type": "Property",
            "value": self.name
        }

        data = {
            "id": entity_id,
            "type": entity_type,
            "dateObserved": date_observed,
            "category": category,
            "controlledProperty": controlledProperty,
            "dateObserved": date_observed,
            "serialNumber": serialNumber,
            "value": value,
            "placement": placement,
            "name": name,
            "@context": AT_CONTEXT
        }

        return entity_id, data
