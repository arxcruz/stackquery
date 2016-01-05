angular.module('login', [])
    .controller('loginCtrl', LoginCtrl)

function LoginCtrl($scope, $location, AuthenticationService) {
    $scope.errorMessage = '';
    $scope.login = login;

    (function initController() {
        // reset login status
        AuthenticationService.clearCredentials();
    })();

    function login() {
        AuthenticationService.Login($scope.username, $scope.password, function(response) {
            if(response.success) {
                AuthenticationService.setCredentials($scope.username, $scope.password);
                $location.path('/')
            } else {
                console.log(response);
                $scope.errorMessage = 'Username and/or password is invalid';
            }
        });
    }
}
