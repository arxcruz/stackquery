angular.module('stackalitics', ['angularUtils.directives.dirPagination'])
    .factory('stackApi', stackApi)
    .constant('stackApiUrl', 'http://stackalytics.com/api/1.0/stats/engineers')
    .controller('stackCtrl', StackCtrl);


function stackApi($http, restApi, stackApiUrl) {
    return {
        getUsersByCompany(company) {
            return restApi.get('?release=all&company=' + company, stackApiUrl);
        },
        getMetrics(metrics) {
            return restApi.post(metrics, '/api/v1.0/stackalytics');
        }
    }
}

function StackCtrl($scope, stackApi, userApi) {

    $scope.users = [];
    $scope.selected = [];
    $scope.errorMessage = '';
    $scope.successMessage = '';
    $scope.selectAll = false;
    $scope.currentPage = 1;
    $scope.pageSize = 10;
    $scope.loading = false;

    $scope.getUsers = getUsers;
    $scope.toggleSelection = toggleSelection;
    $scope.search = search;
    $scope.selectAll = selectAll;
    $scope.addUser = addUser;
    $scope.addSelectedUsers = addSelectedUsers;

    function getUsers(company) {
        $scope.loading = true;
        stackApi.getUsersByCompany(company)
            .success(
                function(data) {
                    $scope.users = data.stats;
                })
            .error(
                function(errorInfo, status) {
                    $scope.users = [];
                    $scope.errorMessage = 'An error occurred: ' + errorInfo.message;
                })
            .finally(function() {
                $scope.loading = false;
            });
    }

    function toggleSelection(user) {
        var idx = $scope.selected.indexOf(user);
        if(idx > -1) {
            $scope.selected.splice(idx, 1);
        } else {
            $scope.selected.push(user);
        }
    }

    function search() {
        getUsers($scope.company);
    }

    function selectAll() {
        if($scope.selected.length == $scope.users.length) {
            $scope.selected = [];
        } else {
            $scope.selected = [];
            for(var i = 0; i < $scope.users.length; i++) {
                var user = $scope.users[i];
                $scope.selected.push(user);
            }
        }
    }

    function addUser(user) {
        return addUserBackend(user);
        //dismissMessages();
    }

    function addSelectedUsers() {
        for(var i = 0; i < $scope.selected.length; i++) {
            var user = $scope.selected[i];
            addUserBackend(user);
        }
    }

    function addUserBackend(user) {
        userApi.addUser({
            name: user.name,
            user_id: user.id
        })
        .success(
            function(data) {
                $scope.successMessage = 'User ' + user.name + ' added successfully';
                var idx = $scope.users.indexOf(user);
                if(idx > -1) {
                    $scope.users.splice(idx, 1);
                }
                idx = $scope.selected.indexOf(user);
                if(idx > -1) {
                    $scope.selected.splice(idx, 1);
                }
            })
        .error(
            function(errorInfo, status) {
                $scope.errorMessage = 'An error ocurred: ' + errorInfo.message;
            })
    }   
}