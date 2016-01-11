'use strict';

var angular = require('angular');
var bulk = require('bulk-require');

module.exports = angular.module('stackquery.factories', []);

bulk(__dirname, ['./**/!(*_index|*.spec).js']);