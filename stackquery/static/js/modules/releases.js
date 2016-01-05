angular.module('releases', [])
    .factory('releaseApi', releaseApi)
    .constant('releaseApiUrl', '/api/v1.0/releases');

function releaseApi($http, restApi, releaseApiUrl) {
    return {
        getReleases: function() {
            return restApi.get(null, releaseApiUrl);
        }
    }
}