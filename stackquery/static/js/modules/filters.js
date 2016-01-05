angular.module('filters', [])
    .factory('filterApi', filterApi)
    .constant('filterApiUrl', '/api/v1.0/filterscenario')
    .controller('filtersCtrl', FiltersCtrl);

function filterApi($http, restApi, filterApiUrl) {
    return {
        addFilter: function(filter) {
            return restApi.post(filter, filterApiUrl);
        },
        getFilter: function() {
            return restApi.get(null, filterApiUrl);
        },
        delFilter: function(filter) {
            return restApi.del(null, filter.uri);
        }
    }
}

function FiltersCtrl($scope, $modalInstance, filterApi) {
    $scope.loadedFilters = [];
    $scope.errorMessage = '';
    $scope.successMessage = '';
    $scope.currentPage = 1;
    $scope.pageSize = 10;
    $scope.loading = false;
    $scope.model = {};

    $scope.hasError = hasError;
    $scope.hasSuccess = hasSuccess;
    $scope.createFilter = createFilter;
    $scope.removeFilter = removeFilter;
    $scope.refreshFilter = refreshFilter;
    $scope.ok = ok;
    $scope.cancel = cancel;

    refreshFilter();

    function hasError() {
        return $scope.errorMessage != '';
    }

    function hasSuccess() {
        return $scope.successMessage != '';
    }

    function createFilter() {
        filterApi.addFilter($scope.model)
            .success(function(data) {
                $scope.successMessage = 'Filter added successfully';
                $scope.model = {};
                dismissMessages();
            })
            .error(function(errorInfo, status) {
                $scope.errorMessage = 'An error ocurred: ' + errorInfo.message;
            });
    }

    function removeFilter(filter) {
        filterApi.delFilter(filter)
            .success(function(data) {
                var idx = $scope.loadedFilters.indexOf(filter);
                if(idx > 0) {
                    $scope.loadedFilters.splice(idx, 1);
                }
                dismissMessages();
            })
            .error(function(errorInfo, status) {
                console.log('An error ocurred: ' + errorInfo.message);
            });
    }

    function refreshFilter() {
        $scope.loading = true;
        filterApi.getFilter()
            .success(function(data) {
                $scope.loadedFilters = data;
            })
            .finally(function() {
                $scope.loading = false;
            });
    }

    function ok() {
        $modalInstance.close($scope.loadedFilters);
    }

    function cancel() {
        $modalInstance.dismiss('cancel');
    }

    function dismissMessages() {
        setTimeout(function() {
            $scope.successMessage = '';
            $scope.errorMessage = '';
            $scope.$apply();
        }, 4000);
    }
}