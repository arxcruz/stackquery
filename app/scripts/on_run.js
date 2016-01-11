'use strict';

function OnRun($rootScope, $location, $cookies, $http) {
    // $rootScope, $location, $cookies, $http
    // $rootScope.globals = $cookies.getObject('globals') || {};
    // if($rootScope.globals.currentUser) {
    //     $http.defaults.headers.common['Authorization'] = 'Basic ' + $rootScope.globals.currentUser.authdata;
    // }
    // $rootScope.$on('$locationChangeStart', function(event, next, current) {
    //     var restricted = ['/users', '/projects', '/reports', '/bugzilla', '/harvester'];
    //     var restrictedPage = $.inArray($location.path(), restricted);
    //     var loggedIn = $rootScope.globals.currentUser;

    //     if (restrictedPage && !loggedIn) {
    //         $location.path('/login');
    //     }
    // });
}

module.exports = OnRun;