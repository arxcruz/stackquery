'use strict';

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

    // TODO check if still needed
    var selectedId = -1;
    var loading = false;

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
        return selectedId < 0 || selectedId !== id;
    }

    function isInEditMode(id) {
        return selectedId === id && editFlag;
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
        return $scope.errorMessage !== '';
    }

    function hasSuccess() {
        return $scope.successMessage !== '';
    }
}

export default {
    name: 'userListCtrl',
    fn: UserListCtrl
};
