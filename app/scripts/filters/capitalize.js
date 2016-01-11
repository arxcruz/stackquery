'use strict';

var filtersModule = require('./_index.js');

function capitalize() {
    return function(input) {
        if (input !== null) {
            input = input.toLowerCase();
        }
        return input.substring(0,1).toUpperCase()+input.substring(1);
    };
}

filtersModule.filter('capitalize', capitalize);