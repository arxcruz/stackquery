'use strict';

function TeamCtrl($scope, $modal, teamApi, userApi) {
    $scope.errorMessage = '';
    $scope.successMessage = '';
    $scope.model = {};
    $scope.users = [];
    $scope.currentPageUsers = 1;
    $scope.loadedUsers = [];
    $scope.usersPageSize = 10;
    $scope.usersCurrentPage = 1;
    $scope.loading = false;

    $scope.createTeam = createTeam;
    $scope.removeUser = removeUser;
    $scope.refreshUser = refreshUser;
    $scope.userContains = userContains;
    $scope.addUser = addUser;
    $scope.removeUser = removeUser;

    refreshUser();

    function createTeam() {
        $scope.$broadcast('show-errors-check-validity');

        if ($scope.teamForm.$invalid) { 
            return; 
        }

        var team = {
            name: $scope.model.teamName,
            users: $scope.users,
        };

        teamApi.addTeam(team)
            .success(
                function (data) {
                    reset();
                    $scope.successMessage = 'Team added successfully';
                })
            .error(
                function (errorInfo, status) {
                    $scope.errorMessage = 'An error ocurred: ' + errorInfo.message;
                });  
    }

    function refreshUser() {
        if($scope.loadedUsers.length === 0) {
            $scope.loading = true;
            userApi.getUsers()
                .success(
                    function(data) {
                        $scope.loadedUsers = data;
                    })
                .error(
                    function(errorInfo, status) {

                    })
                .finally(function() {
                    $scope.loading = false;
                });
        }
    }

    function userContains(user) {
        for(var i = 0; i < $scope.users.length; i++) {
            var usr = $scope.users[i];
            if(usr.id === user.id) {
                return i;
            }
        }
        return -1;
    }

    function addUser(user) {
        $scope.users.push(user);
    }

    function removeUser(user) {
        var idx = userContains(user);
        if(idx < 0) {
            return;
        }
        $scope.users.splice(idx, 1);
    }

    function reset() {
        $scope.model = {};
        $scope.users = [];
        $scope.projects = [];
    }
}

export default {
    name: 'teamCtrl',
    fn: TeamCtrl
};
