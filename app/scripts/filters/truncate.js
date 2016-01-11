'use strict';

var filtersModule = require('./_index.js');

function truncate() {
    return function (text, length, end) {
        if (text !== undefined) {
            if (isNaN(length)){
                length = 10;
            }

            end = end || '...';

            if (text.length <= length || text.length - end.length <= length) {
                return text;
            } else {
                return String(text).substring(0, length - end.length) + end;
            }
        }
    };
}

filtersModule.filter('truncate', truncate);