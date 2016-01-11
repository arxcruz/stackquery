'use strict';

var filtersModule = require('./_index.js');

function sumByKey() {
    return function(data, key) {
        if (typeof(data) === 'undefined' || typeof(key) === 'undefined' || data === null) {
            return 0;
        }

        var sum = 0;
        for (var i = data.length - 1; i >= 0; i--) {
            sum += parseInt(data[i][key]);
        }
        return sum;
    };
}

filtersModule.filter('sumByKey', sumByKey);