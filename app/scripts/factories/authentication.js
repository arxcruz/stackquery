'use strict';

var angular = require('angular');
var factoriesModule = require('./_index.js');

function AuthenticationService($http, $cookies, $rootScope) {
    return {
        Login: function(username, password, callback) {
            $http.post('/api/v1.0/login', {username: username, password: password})
                .success(function(response) {
                    callback(response);
                });
        },
        setCredentials: function(username, password) {
            var authdata = btoa(username + ':' + password);
            $rootScope.globals = {
                currentUser: {
                    username: username,
                    authdata: authdata
                }
            };

            $http.defaults.headers.common.Authorization = 'Basic ' + authdata;
            var expireDate = new Date();
            expireDate.setDate(expireDate.getDate() + 1);
            $cookies.putObject('globals', $rootScope.globals, {'expires': expireDate});
        },
        clearCredentials: function() {
            $rootScope.globals = {};
            $cookies.remove('globals');
            $http.defaults.headers.common.Authorization = 'Basic ';
        }
    };
}

factoriesModule.factory('AuthenticationService', AuthenticationService);