const got = require('got');
const config = require('../config');

const CONTEXT_BROKER_URL =
    'http://' +
    (process.env.IOTA_HTTP_HOST || config.contextBroker.host) +
    ':' +
    (process.env.IOTA_HTTP_PORT || config.contextBroker.port);

const LINKED_DATA = process.env.IOTA_JSON_LD_CONTEXT || config.contextBroker.jsonLdContext;

function sendData(headers, bodyContent, start, end) {
    const subsetBodyContent = bodyContent(start, end);
    let cbResponse;

    const options = {
        headers,
        searchParams: { options: 'update' },
        json: subsetBodyContent,
        responseType: 'json'
    };

    // We need to check the status code of the response, if this is ok (statusCode: xxx) return statusCode,
    // if there is something different, we need to send back an error and stop the loop.
    // cbResponse = await got.post(url, options);

    return cbResponse
}


// measures sent over HTTP are POST requests with params
async function sendAsHTTP(bodyContent) {
    const url = CONTEXT_BROKER_URL + '/ngsi-ld/v1/entityOperations/upsert';

    const headers = {
        'Content-Type': 'application/json',
        Link: '<' + LINKED_DATA + '>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'
    };

    const steps = (bodyContent.length / config.maximumUpsert) >> 0;  // Calculate the int division
    const rest = bodyContent.length % config.maximumUpsert;
    let cbResponse;

    for(let i=0; i<steps; i=i+1) {
        let start = i * config.maximumUpsert;
        let end = start + config.maximumUpsert - 1;

        cbResponse = sendData(headers, bodyContent, start, end);

        // If there was an error, we stop and return the code error
        if ( cbResponse.statusCode === 400 )
            return cbResponse;
    }

    if ( rest !== 0 ) {
        let start = steps * config.maximumUpsert;
        let end = start + rest - 1;

        cbResponse = sendData(headers, bodyContent, start, end);

        // If there was an error, we stop and return the code error
        if ( cbResponse.statusCode === 400 )
            return cbResponse;
    }

    return cbResponse;
}

module.exports = {
    sendAsHTTP
};
