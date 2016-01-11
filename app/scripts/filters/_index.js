'use strict';

var angular = require('angular');
var bulk = require('bulk-require');

module.exports = angular.module('stackquery.filters', []);

bulk(__dirname, ['./**/!(*_index|*.spec).js']);