// const readXlsxFile = require('read-excel-file/node');
const excel = require("fast-xlsx-reader");
const Measure = require('../lib/measure');
const config = require('../config');
const debug = require('debug')('server:excel');
const fs = require('fs');
const _ = require('underscore');
const Device = require('../lib/Device');
const replacements = Object.keys(config.replace);
const meanValues = Object.keys(config.mean);
const unitCode = Object.keys(config.unitCode);
const Status = require('http-status-codes');
const { getJsDateFromExcel } = require("excel-date-to-js");

/**
 * The UnitCode is held in the static data, but need to be sent as
 * meta data with each measurement.
 */
function storeDeviceUnitCode(id, unitCode) {
    const data = { unitCode };
    debug(data);
    try {
        Device.model.findOneAndUpdate({ id }, data, { upsert: true }, function (err) {
            if (err) {
                debug(err.message);
            }
        });
    } catch (err) {
        debug(err.message);
    }
}

/*
 * Delete the temporary file
 */
function removeXlsxFile(path) {
    fs.unlink(path, (err) => {
        if (err) {
            throw err;
        }
    });
}


/*
 * Read the XLS data from the temporary file.
 * This returns an in memory representation of the raw CSV file
 */
function readXlsFile(inputFile) {
    return new Promise((resolve, reject) => {
        const reader = excel.createReader({
            input: inputFile
        });

        const rows = reader.readMany(reader.startRow, reader.rowCount);

        // clean up
        reader.destroy();

        resolve(rows);
    })
}

/*
 * Capitalise each word in a string
 */
function titleCase(str) {
    const splitStr = str.toLowerCase().split(' ');

    for (var i = 1; i < splitStr.length; i++) {
        // You do not need to check if i is larger than splitStr length, as your for does that for you
        // Assign it back to the array
        splitStr[i] = splitStr[i].charAt(0).toUpperCase() + splitStr[i].substring(1);
    }

    // Directly return the joined string without spaces
    return splitStr.join('');
}

/*
 * Manipulate the Excel data to create a series of entities
 */
function createEntitiesFromXlsx(rows) {
    const entities = [];
    const indexes = [];
    const collator = new Intl.Collator('bg');

    // We need to discard the columns not needed
    _.map(config.ignoreColLab, (column) => {
            const index = rows[0].findIndex(element => collator.compare(element, column) === 0);
            if (index !== -1)
                indexes.push(index)
        }
    )

    const filteredRows = []

    // delete all columns (index) in all arrays
    _.map(rows, (row) => {
            filteredRows.push(
                row.filter(function(value, index, arr){ return !indexes.includes(index);})
            )
        }
    )

    rows = filteredRows

    const headerFields = _.map(rows[0], (header) => {
        const esc_header = escape(header);
        return replacements.includes(esc_header) ? config.replace[esc_header] : titleCase(header);
    });

    // skip header
    rows.shift();

    rows.forEach((row) => {
        const entity = {};

        headerFields.forEach((header, index) => {
            let value = row[index];
            if (!config.ignore.includes(value)) {
                value = replacements.includes(value) ? config.replace[value] : value;
                if(unitCode.includes(header)) {
                    const unitCode = config.unitCode[header];
                    entity[header] = {
                        type: 'Property',
                        value,
                        unitCode
                    };
                } else {
                    entity[header] = {
                        type: 'Property',
                        value
                    };
                }
            }
        });

        entity.location = {
            "type": "Address",
            "value": {
                "type": "areaServed",
                "value": entity.id.value
            }
        };

        entity.type = 'WaterQualityObserved';
        entity.id = 'urn:ngsi-ld:WaterQualityObserved:waterqualityobserved:WWTP:' + entity.id.value;

        config.datetime.forEach((datetime) => {
            if (entity[datetime]) {
                try {
                    entity[datetime].value = {
                        '@type': 'DateTime',
                        '@value': getJsDateFromExcel(entity[datetime].value).toISOString()
                    };
                } catch (e) {
                    debug(e);
                }
            }
        });

        entity['@context'] = [
            'https://schema.lab.fiware.org/ld/context',
            'https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld'
        ]

        entities.push(entity);

    });

    return entities;
}

const upload = (req, res) => {
    if (req.file === undefined) {
        return res.status(Status.UNSUPPORTED_MEDIA_TYPE).send('Please upload an excel file!');
    }

    const path = __basedir + '/resources/static/assets/uploads/' + req.file.filename;

    return readXlsFile(path)
        .then((rows) => {
            const entities = createEntitiesFromXlsx(rows);
            removeXlsxFile(path);
            return entities;
        })
        .then(async (entities) => {
            const cbResponse = await Measure.sendAsHTTP(entities);
            return res.status(cbResponse ? cbResponse.statusCode : 204).send();
        })
        .catch((err) => {
            return res.status(Status.INTERNAL_SERVER_ERROR).send(err);
        });
};

module.exports = {
    upload
};
