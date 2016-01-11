'use strict';

function BulkUserCtrl($scope, userApi) {

    $scope.users = [];
    $scope.currentPage = 1;
    $scope.pageSize = 10;
    $scope.errorMessage = '';
    $scope.successMessage = '';

    $scope.loadUsersFromText = loadUsersFromText;
    $scope.reset = reset;
    $scope.addBulkUsers = addBulkUsers;

    function loadUsersFromText() {
        var usersSplited = $scope.usersText.trim().split(';');
        for(var i = 0; i < usersSplited.length; i++) {
            var singleUser = usersSplited[i].split(',');
            var user = {
                name: singleUser[0],
                user_id: singleUser[1],
                email: singleUser[2]
            };
            $scope.users.push(user);
        }
    }

    function reset() {
        $scope.users = [];
        //$scope.usersText = '';
    }

    function addBulkUsers() {
        console.log($scope.users.length);
        for(var i = 0; i < $scope.users.length; i++) {
            var user = $scope.users[i];
            if(user) {
                addUserBackend(user);    
            }
        }
        $scope.users = [];
    }

    function addUserBackend(user) {
        userApi.addUser(user)
        .success(
            function(data) {
                $scope.successMessage = 'User ' + user.name + ' added successfully';
            })
        .error(
            function(errorInfo, status) {
                $scope.errorMessage = 'An error ocurred: ' + errorInfo.message;
            });
    }
}

export default {
    name: 'bulkUserCtrl',
    fn: BulkUserCtrl
};
