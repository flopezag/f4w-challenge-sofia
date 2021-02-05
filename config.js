const config = {
    mongodb: 'mongodb://localhost:27017/iotagent-csv',
    contextBroker: {
        host: 'orion',
        port: '1026',
        jsonLdContext: 'http://csv-agent:3100/data-models/ngsi-context.jsonld'
    },
    replace: {
        'time': 'dateObserved',
        'cтойност': 'level',
        'cтатус': 'status',
        'kачество': 'quality',
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
    relationship: []
};

module.exports = config;



