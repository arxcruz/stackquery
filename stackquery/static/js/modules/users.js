angular.module('users', ['ui.bootstrap'])
    .controller('userCtrl', UserCtrl)
    .controller('bulkUserCtrl', BulkUserCtrl)
    .controller('userListCtrl', UserListCtrl)
    .factory('userApi', userApi)
    .constant('userApiUrl', '/api/v1.0/users');

function userApi($http, restApi, userApiUrl) {
    return {
        addUser: function(user) {
            return restApi.post(user, userApiUrl);
        },
        getUsers: function() {
            return restApi.get(null, userApiUrl);
        },
        updateUser: function(user) {
            return restApi.put(user, user.url);
        },
        delUser: function(user) {
            return restApi.del(null, user.url);
        }
    }
}

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
        var usersSplited = $scope.usersText.trim().split(";");
        for(var i = 0; i < usersSplited.length; i++) {
            var singleUser = usersSplited[i].split(",");
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

function UserListCtrl($scope, userApi) {
    var editFlag = false;

    $scope.users = [];
    $scope.selectedId = -1;
    $scope.currentPage = 1;
    $scope.pageSize = 10;
    $scope.loading = false;
    $scope.errorMessage = '';
    $scope.successMessage = '';

    $scope.refresh = refresh;
    $scope.isInReadMode = isInReadMode;
    $scope.isInEditMode = isInEditMode;
    $scope.startEdit = startEdit;
    $scope.save = save;
    $scope.cancel = reset;
    $scope.removeUser = removeUser;

    refresh();

    function refresh() {
        $scope.loading = true;
        $scope.users = [];
        userApi.getUsers()
            .success(
                function(data) {
                    $scope.users = data;
                })
            .error(
                function(errorInfo, status) {

                })
            .finally(function() {
                $scope.loading = false;
                reset();
            });
    }

    function isInReadMode(id) {
        return selectedId < 0 || selectedId != id;
    }

    function isInEditMode(id) {
        return selectedId == id && editFlag;
    }

    function startEdit(id) {
        reset();
        selectedId = id;
        editFlag = true;
        loading = false;
    }

    function save(user) {
        userApi.updateUser(user)
            .success(function(data) {
                $scope.successMessage = 'User: ' + user.name + ' updated successfully';
            })
            .error(function(errorInfo, status) {
                $scope.errorMessage = 'An error ocurred: ' + errorInfo.message;
            })
            .finally(function() {
                reset();
            });
    }

    function reset() {
        selectedId = -1;
        editFlag = false;
    }

    function removeUser(user) {
        userApi.delUser(user)
            .success(function(data) {
                var idx = $scope.users.indexOf(user);
                if(idx < 0) {
                    return;
                }
                $scope.users.splice(idx, 1);
                $scope.successMessage = 'User ' + user.name + ' deleted successfully';
            })
            .error(function(errorInfo, status) {
                $scope.errorMessage = 'An error ocurred: ' + errorInfo.message;
            })
            .finally(function() {
                reset();
            });
    }

    function hasError() {
        return $scope.errorMessage != '';
    }

    function hasSuccess() {
        return $scope.successMessage != '';
    }
}