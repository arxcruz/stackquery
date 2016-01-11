'use strict';

function UserCtrl($scope, userApi) {

    $scope.errorMessage = '';
    $scope.successMessage = '';
    $scope.model = {};
    $scope.createUser = createUser;

    reset();

    function createUser() {
        $scope.$broadcast('show-errors-check-validity');

        if ($scope.userForm.$invalid) { 
            return; 
        }

        var user = {
            name: $scope.model.userName,
            user_id: $scope.model.userId,
            email: $scope.model.userEmail
        };

        userApi.addUser(user)
            .success(
                function (data) {
                    reset();
                    $scope.successMessage = 'User added successfully';
                })
            .error(
                function (errorInfo, status) {
                    $scope.errorMessage = 'An error ocurred: ' + errorInfo.message;
                });        
    }

    function reset() {
        $scope.model = {};
    }
}

export default {
    name: 'userCtrl',
    fn: UserCtrl
};
