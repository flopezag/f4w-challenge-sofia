const config = {
    mongodb: 'mongodb://localhost:27017/iotagent-csv',
    contextBroker: {
        host: 'orion',
        port: '1026',
        jsonLdContext: 'http://csv-agent:3100/data-models/ngsi-context.jsonld'
    },
    replace: {
        'Time': 'dateObserved',
        '%u0421%u0442%u043E%u0439%u043D%u043E%u0441%u0442': 'value',  // 'Cтойност': 'level'
        '%u0421%u0442%u0430%u0442%u0443%u0441': 'status',  // 'Cтатус': 'status'
        '%u041A%u0430%u0447%u0435%u0441%u0442%u0432%u043E': 'deviceState',  // 'Kачество': 'quality'
        'Нормално ниво': 'Normal Level',
        'Добро': 'Good',
        'Date Time, GMT+02:00': 'dateObserved',
        'Temp, °C (LGR S/N: 10078375, SEN S/N: 10078375)': 'value'
    },
    ignoreColLab: [
        'причина', 'статус', 'Suppression Type', 'Coupler Attached (LGR S/N: 10078375)',
        'Host Connected (LGR S/N: 10078375)', 'End Of File (LGR S/N: 10078375)', '#'
    ],
    ignore: ['', '----', 'ND', '>14.0'],
    mean: {},
    unitCode: {
        "level": "MTR"
    },
    datetime: ['dateObserved'],
    maximumUpsert: 400,
    relationship: [],
    scope: 5  // Time in min between two measurements notification to Orion
};

module.exports = config;



