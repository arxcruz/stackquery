'use strict';

function TeamProjectAndUsersCtrl($scope, $modalInstance, users, teamName, userApi) {
    $scope.loadedProjects = [];
    $scope.users = users;
    $scope.loadedUsers = [];
    $scope.usersPageSize = 10;
    $scope.usersCurrentPage = 1;

    $scope.teamName = teamName;

    $scope.addUser = addUser;
    $scope.removeUser = removeUser;
    $scope.refreshUser = refreshUser;
    $scope.userContains = userContains;

    $scope.ok = ok;
    $scope.cancel = cancel;

    refreshUser();

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

    function ok() {
        var result = {projects: $scope.projects, users: $scope.users};
        if($scope.teamName) {
            result.teamName = $scope.teamName;
        }
        $modalInstance.close(result);
    }

    function cancel() {
        $modalInstance.dismiss('cancel');
    }
}

export default {
    name: 'teamProjectAndUsersCtrl',
    fn: TeamProjectAndUsersCtrl
};
