const fs = require('fs');
const csv = require('fast-csv');
const Measure = require('../lib/measure');
const debug = require('debug')('server:csv');
const _ = require('underscore');
const Device = require('../lib/Device');
const Status = require('http-status-codes');
const config = require('../config');
const replacements = Object.keys(config.replace);
const date = require('date-and-time');

/*
 * Delete the temporary file
 */
function removeCsvFile(filename) {
    const path = __basedir + '/resources/static/assets/uploads/' + filename;

    fs.unlink(path, (err) => {
        if (err) {
            throw err;
        }
    });
}

/*
 * Read the CSV data from the temporary file.
 * This returns an in memory representation of the raw CSV file
 */
function readCsvFile(filename) {
    const path = __basedir + '/resources/static/assets/uploads/' + filename;

    var temp = filename.split('-')[1].split('_');

    temp = {
        "plant": temp[0],
        "property": temp[1]
    };

    return new Promise((resolve, reject) => {
        const rows = [];

        rows.push(temp);

        fs.createReadStream(path)
            .pipe(csv.parse({ headers: true, discardUnmappedColumns: true}))
            .on('error', (error) => {
                reject(error.message);
            })
            .on('data', (row) => {
                rows.push(row);
            })
            .on('end', () => {
                resolve(rows);
            });
    });
}

/**
 * Retrieve the unitCode from the static data saved in a database.
 */
async function getDeviceUnitCode(id) {
    let data;
    const queryParams = {
        id: 'urn:ngsi-ld:Device:' + id
    };
    const query = Device.model.findOne(queryParams);

    try {
        data = await query.lean().exec();
    } catch (err) {
        debug('error: ' + err);
    }
    return data ? data.unitCode : undefined;
}

/*
 * Manipulate the CSV data to create a series of measures
 * The data has been extracted based on the headers and other
 * static data such as the unitCode.
 */
async function createMeasuresFromCsv(rows) {
    const headerInfo = [];
    const measures = [];

    measures.push({
        "plantId": rows[0].plant,
        "property": rows[0].property
    })

    rows.shift();

    const key = Object.keys(rows[0]).toString();

    key.split(';').slice(0, 2).forEach((header) => {
            header = replacements.includes(header) ? config.replace[header] : header;
            headerInfo.push(header)
        }
    )

    rows.forEach((row) => {
            const measure = {};
            const value = row[key].toString().split(';');

            // We need to delete the spaces in the value, second element of the array and should be a float
            value[1] = parseFloat(value[1].replace(/\s+/g, ''));

            headerInfo.forEach((header, index) => {
                    measure[header] = value[index]
                }
            )

            measures.push(measure);
        }

    );

    return measures;
}

/*
 * Take the in memory data and format it as NSGI Entities
 *
 */
function createEntitiesFromMeasures(measures) {
    const plantId = measures[0].plantId;
    const property = measures[0].property;
    const entities = [];

    measures.shift();

    measures.forEach((measure) => {
        const entity = {};

        entity.location = {
            "type": "Address",
            "value": {
                "type": "areaServed",
                "value": plantId
            }
        };

        entity.type = 'WaterQualityObserved';
        entity.id = 'urn:ngsi-ld:WaterQualityObserved:waterqualityobserved:WWTP:' + plantId;

        //const d = new Date(measure.dateObserved);
        const d = date.parse(measure.dateObserved, 'DD/MM/YYYY HH:mm:ss');

        entity.dateObserved = {
            "type": "Property",
            "value": {
                "@type": "DateTime",
                "@value": d.toISOString()
            }
        };

        entity[property] = {
            "type": "Property",
            "value": measure.value,
            "unitCode": ""
        }

        entity['@context'] = [
            'https://schema.lab.fiware.org/ld/context',
            'https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld'
        ]


            entities.push(entity);
    });

    return entities;
}

/*
 * Create an array of promises to send data to the context broker.
 * Each insert represents a series of readings at a given timestamp
 */
function createContextRequests(entities) {
    const promises = [];
    entities.forEach((entitiesAtTimeStamp) => {
        promises.push(Measure.sendAsHTTP(entitiesAtTimeStamp));
    });
    return promises;
}

/**
 * Actions when uploading a CSV file. The CSV file holds an array of
 * measurements each at a given timestamp.
 */
const upload = (req, res) => {
    if (req.file === undefined) {
        return res.status(Status.UNSUPPORTED_MEDIA_TYPE).send('Please upload a CSV file!');
    }

    return readCsvFile(req.file.filename)
        .then((rows) => {
            return createMeasuresFromCsv(rows);
        })
        .then((measures) => {
            removeCsvFile(req.file.filename);
            return createEntitiesFromMeasures(measures);
        })
        .then((entities) => {
            return createContextRequests(entities);
        });
        /*
        .then(async (promises) => {
            return await Promise.allSettled(promises);
        })
        .then((results) => {
            const errors = _.where(results, { status: 'rejected' });
            return errors.length ? res.status(Status.BAD_REQUEST).json(errors) : res.status(Status.NO_CONTENT).send();
        })
        .catch((err) => {
            debug(err.message);
            return res.status(Status.INTERNAL_SERVER_ERROR).send(err.message);
        });

         */
};

module.exports = {
    upload
};
