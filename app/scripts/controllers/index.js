'use strict';

var angular = require('angular');
var bulk = require('bulk-require');

const controllersModule = angular.module('stackquery.controllers', ['ui.grid']);

const controllers = bulk(__dirname, ['./**/!(*_index|*.spec).js']);

function declare(controllerMap) {
    Object.keys(controllerMap).forEach((key) => {
        if(key === 'index') {
            return;
        }

        let item = controllerMap[key];

        if (!item) {
            return;
        }

        if (item.fn && typeof item.fn === 'function') {
            controllersModule.controller(item.name, item.fn); 
        } else { 
            declare(item);
        }
    });
}

declare(controllers);

export default controllersModule;
