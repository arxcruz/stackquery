'use strict';

var angular = require('angular');
var factoriesModule = require('./_index.js');

function restApi($http) {

    function request(verb, param, apiUrl, data) {
        var req = {
            method: verb,
            url: url(param, apiUrl),
            data: data,
        };

        return $http(req);
    }

    function url(param, apiUrl) {
        if (param === null || !angular.isDefined(param)) {
            param = '';
        }
        return apiUrl + param;
    }

    return {
        get: function get(param, apiUrl) {
            return request('GET', param, apiUrl);
        },
        post: function post(data, apiUrl) {
            return request('POST', null, apiUrl, data);
        },
        put: function put(data, apiUrl) {
            return request('PUT', null, apiUrl, data);
        },
        del: function del(param, apiUrl) {
            return request('DELETE', param, apiUrl);
        },
    };
}

// Bugzilla

function bugzillaApi($http, restApi, AppSettings) {
    return {
        addBugzilla: function(bugzilla) {
            return restApi.post(bugzilla, AppSettings.bugzillaApiUrl);
        },
        getBugzilla: function() {
            return restApi.get(null, AppSettings.bugzillaApiUrl);
        },
        updateBugzilla: function(bugzilla) {
            return restApi.put(bugzilla, bugzilla.uri);
        },
        delBugzilla: function(bugzilla) {
            return restApi.del(null, bugzilla.uri);
        },
        getRHBugzillaReport: function(bugzilla) {
            var url = AppSettings.bugzillaApiUrl + '/show';
            return restApi.post(bugzilla, url);
        }
    };
}

// Scenario
function scenarioApi($http, restApi, AppSettings) {
    return {
        getScenarios: function(scenario) {
            return restApi.post(scenario, AppSettings.scenarioApiUrl);
        }
    };
}

// Havester

function harvesterApi($http, restApi, AppSettings) {
    return {
        addReport: function(report) {
            return restApi.post(report, AppSettings.harvesterApiUrl);
        },
        getReport: function() {
            return restApi.get(null, AppSettings.harvesterApiUrl);
        },
        delReport: function(report) {
            return restApi.del(null, report.uri);
        },
        updateReport: function(report) {
            return restApi.put(report, report.uri);
        }
    };
}

// Releases

function releaseApi($http, restApi, AppSettings) {
    return {
        getReleases: function() {
            return restApi.get(null, AppSettings.releaseApiUrl);
        }
    };
}

// Teams

function teamApi($http, restApi, AppSettings) {
    return {
        addTeam: function(team) {
            return restApi.post(team, AppSettings.teamApiUrl);
        },
        getTeams: function() {
            return restApi.get(null, AppSettings.teamApiUrl);
        },
        updateTeam: function(team) {
            return restApi.put(team, team.uri);
        },
        delTeam: function(team) {
            return restApi.del(null, team.uri);
        }
    };
}

// Users

function userApi($http, restApi, AppSettings) {
    return {
        addUser: function(user) {
            return restApi.post(user, AppSettings.userApiUrl);
        },
        getUsers: function() {
            return restApi.get(null, AppSettings.userApiUrl);
        },
        updateUser: function(user) {
            return restApi.put(user, user.url);
        },
        delUser: function(user) {
            return restApi.del(null, user.url);
        }
    };
}

// Stackalytics

function stackApi($http, restApi, AppSettings) {
    return {
        getUsersByCompany(company) {
            return restApi.get('?release=all&company=' + company, AppSettings.stackApiUrl);
        },
        getMetrics(metrics) {
            return restApi.post(metrics, '/api/v1.0/stackalytics');
        }
    };
}

// Filters

function filterApi($http, restApi, AppSettings) {
    return {
        addFilter: function(filter) {
            return restApi.post(filter, AppSettings.filterApiUrl);
        },
        getFilter: function() {
            return restApi.get(null, AppSettings.filterApiUrl);
        },
        delFilter: function(filter) {
            return restApi.del(null, filter.uri);
        }
    };
}

// Projects

function projectApi($http, restApi, AppSettings) {
    return {
        addProject: function(project) {
            return restApi.post(project, AppSettings.projectApiUrl);
        },
        getProjects: function() {
            return restApi.get(null, AppSettings.projectApiUrl);
        },
        updateProject: function(project) {
            return restApi.put(project, project.uri);
        },
        delProject: function(project) {
            return restApi.del(null, project.uri);
        }
    };
}

factoriesModule.factory('restApi', restApi)
               .factory('bugzillaApi', bugzillaApi)
               .factory('scenarioApi', scenarioApi)
               .factory('harvesterApi', harvesterApi)
               .factory('releaseApi', releaseApi)
               .factory('teamApi', teamApi)
               .factory('userApi', userApi)
               .factory('stackApi', stackApi)
               .factory('filterApi', filterApi)
               .factory('projectApi', projectApi);
