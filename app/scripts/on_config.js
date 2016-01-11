'use strict';

function OnConfig($routeProvider) {
    $routeProvider.when('/users', {
        templateUrl: '/views/users.html'
    });
    $routeProvider.when('/projects', {
        templateUrl: '/views/projects.html'
    });
    $routeProvider.when('/teams', {
        templateUrl: '/views/teams.html'
    });
    $routeProvider.when('/reports/:tabId', {
        templateUrl: '/views/reports.html'
    });
    $routeProvider.when('/bugzilla', {
        templateUrl: '/views/bugzilla.html'
    });
    $routeProvider.when('/harvester', {
        templateUrl: '/views/harvester.html'
    });
    $routeProvider.when('/login', {
        templateUrl: '/views/login.html'
    });
    $routeProvider.otherwise({
        templateUrl: '/views/reports.html'
    });
}

module.exports = OnConfig;