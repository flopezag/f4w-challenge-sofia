from config.settings import AT_CONTEXT


class Payload:
    def __init__(self):
        self.serial_number = ""
        self.placement = ""
        self.name = ""
        self.type_class = 0

    def fix_temp_data(self, type_class, name="", serial_number="", placement=""):
        self.serial_number = serial_number
        self.placement = placement
        self.name = name
        self.type_class = type_class

    def get_data(self, date_observed, measure):
        if self.type_class == 0:
            return self.__temp_data__(date_observed=date_observed, measure=measure)
        elif self.type_class == 1:
            return self.__rain_data__(date_observed=date_observed, measure=measure)
        elif self.type_class == 2:
            return self.__level_data__(date_observed=date_observed, measure=measure)

    def __temp_data__(self, date_observed, measure):
        date_observed = {
            "type": "Property",
            "value": {
                "@type": "DateTime",
                "@value": date_observed.astype(str)
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

        controlled_property = {
            "type": "Property",
            "value": [
                "temperature"
            ]
        }

        serial_number = {
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
            "controlledProperty": controlled_property,
            "serialNumber": serial_number,
            "value": value,
            "placement": placement,
            "name": name,
            "@context": AT_CONTEXT
        }

        return entity_id, data

    def __rain_data__(self, date_observed, measure):
        entity_id = "urn:ngsi-ld:Device:{}".format(self.name)

        entity_type = "Device"

        category = {
            "type": "Property",
            "value": [
                "sensor"
            ]
        }

        controlled_property = {
            "type": "Property",
            "value": [
                "precipitation"
            ]
        }

        date_observed = {
            "type": "Property",
            "value": {
                "@type": "DateTime",
                "@value": date_observed.astype(str)
            }
        }

        value = {
            "type": "Property",
            "value": measure,
            "unitCode": "H67"
        }

        name = {
            "type": "Property",
            "value": self.name
        }

        data = {
            "id": entity_id,
            "type": entity_type,
            "category": category,
            "controlledProperty": controlled_property,
            "dateObserved": date_observed,
            "value": value,
            "name": name,
            "@context": AT_CONTEXT
        }

        return entity_id, data

    def __level_data__(self, date_observed, measure):
        entity_id = "urn:ngsi-ld:Device:device-001C"

        entity_type = "Device"

        category = {
            "type": "Property",
            "value": [
                "sensor"
            ]
        }

        controlled_property = {
            "type": "Property",
            "value": [
                "fillingLevel"
            ]
        }

        date_observed = {
                "type": "Property",
                "value": {
                    "@type": "DateTime",
                    "@value": date_observed.astype(str)
                }
            }

        deviceState = {
            "type": "Property",
            "value": "Good"
        }

        status = {
            "type": "Property",
            "value": "Normal Level"
        }

        value = {
            "type": "Property",
            "value": 0.6,
            "unitCode": "MTR"
        }

        data = {
            "id": entity_id,
            "type": entity_type,
            "category": category,
            "controlledProperty": controlled_property,
            "dateObserved": date_observed,
            "deviceState": deviceState,
            "status": status,
            "value": value,
            "@context": AT_CONTEXT
        }

        return entity_id, data
