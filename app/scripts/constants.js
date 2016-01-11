'use strict';

var apiUrl = 'http://localhost:5000';

var AppSettings = {
    releaseApiUrl: apiUrl + '/api/v1.0/releases',
    harvesterApiUrl: apiUrl + '/api/v1.0/harvester',
    teamApiUrl: apiUrl + '/api/v1.0/teams',
    bugzillaApiUrl: apiUrl + '/api/v1.0/reports',
    scenarioApiUrl: apiUrl + '/api/v1.0/scenarios',
    userApiUrl: apiUrl + '/api/v1.0/users',
    stackApiUrl: 'http://stackalytics.com/api/1.0/stats/engineers',
    filterApiUrl: apiUrl + '/api/v1.0/filterscenario',
    projectApiUrl: apiUrl + '/api/v1.0/projects'
};

module.exports = AppSettings;