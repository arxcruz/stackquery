'use strict';

var angular = require('angular');

// Angular modules

require('angular-ui-bootstrap');
require('angular-route');
require('angular-utils-pagination');
require('angular-cookies');

// jQuery and Bootstrap
global.jQuery = require('jquery');
require('bootstrap');

// Stackquery modules
require('./controllers');
//require('./controllers/teams/_index');
//require('./controllers/users/_index');
require('./directives/_index');
require('./factories/_index');
require('./filters/_index');
require('./ui-grid');

var requires = [
    'ngRoute',
    'ngCookies',
    'ui.bootstrap',
    'ui.grid',
    'angularUtils.directives.dirPagination',
    'stackquery.controllers',
    'stackquery.directives',
    'stackquery.factories',
    'stackquery.filters'
];

angular.module('stackquery', requires);

var onConfig = require('./on_config');
angular.module('stackquery').config(onConfig);

var onRun = require('./on_run');
angular.module('stackquery').run(onRun);

angular.module('stackquery').constant('AppSettings', require('./constants'));

angular.bootstrap(document, ['stackquery']);

