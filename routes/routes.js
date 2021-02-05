const express = require('express');
const router = express.Router();
const csvController = require('../controllers/csv');
const excelController = require('../controllers/excel');
const upload = require('../lib/upload');

// Error Handling Helper Function
function asyncHelper(fn) {
    return function (req, res, next) {
        fn(req, res, next).catch(next);
    };
}

// Read and upload the level meter (.xlsx) file
router.post(
    '/level',
    upload.single('file'),
    asyncHelper(async (req, res) => {
        await excelController.upload(req, res);
    })
);


// Read and upload the rain gauge (.csv) file
router.post(
    '/rain',
    upload.single('file'),
    asyncHelper(async (req, res) => {
        await csvController.upload(req, res);
    })
);

// Read and upload the temperature (.csv) file
router.post(
    '/temp',
    upload.single('file'),
    asyncHelper(async (req, res) => {
        await csvController.upload(req, res);
    })
);

module.exports = router;
