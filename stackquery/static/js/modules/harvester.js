angular.module('harvester', [])
    .factory('harvesterApi', harvesterApi)
    .constant('harvesterApiUrl', '/api/v1.0/harvester')
    .controller('harvesterReportCtrl', HarvesterReportCtrl)
    .controller('harvesterReportListCtrl', HarvesterReportListCtrl)
    .controller('harvesterReportsCtrl', HarvesterReportsCtrl)
    .controller('harvesterCtrl', HarvesterCtrl)

function harvesterApi($http, restApi, harvesterApiUrl) {
    return {
        addReport: function(report) {
            return restApi.post(report, harvesterApiUrl);
        },
        getReport: function() {
            return restApi.get(null, harvesterApiUrl);
        },
        delReport: function(report) {
            return restApi.del(null, report.uri);
        },
        updateReport: function(report) {
            return restApi.put(report, report.uri);
        }
    }
}

function HarvesterReportCtrl($scope, harvesterApi) {
    $scope.model = {};
    $scope.errorMessage = '';
    $scope.successMessage = '';

    $scope.createHarvesterReport = createHarvesterReport;

    function createHarvesterReport() {
        $scope.$broadcast('show-errors-check-validity');

        if ($scope.reportForm.$invalid) { 
            return; 
        }

        harvesterApi.addReport($scope.model)
            .success(function(data) {
                $scope.model = {}
                $scope.successMessage = 'Report added successfully';
            })
            .error(function(errorInfo, status) {
                $scope.errorMessage = 'An error ocurred: ' + errorInfo.message;
            })
    }
}

function HarvesterReportListCtrl($scope, harvesterApi) {
    $scope.harvesterReports = [];
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
    $scope.removeReport = removeReport;

    refresh();

    function refresh() {
        $scope.loading = true;
        $scope.harvesterReports = [];
        harvesterApi.getReport()
            .success(function(data) {
                $scope.harvesterReports = data;
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

    function save(report) {
        harvesterApi.updateReport(report)
            .success(function(data) {
                $scope.successMessage = 'Report: ' + report.name + ' updated successfully';
                dismissMessages();
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

    function removeReport(report) {
        harvesterApi.delReport(report)
            .success(function(data) {
                var idx = $scope.harvesterReports.indexOf(report);
                if(idx < 0) {
                    return;
                }
                $scope.harvesterReports.splice(idx, 1);
                $scope.successMessage = 'Report ' + report.name + ' deleted successfully';
            })
            .error(function(errorInfo, status) {
                $scope.errorMessage = 'An error ocurred: ' + errorInfo.message;
            })
            .finally(function() {
                reset();
            });
    }
}

function HarvesterCtrl($scope, harvesterApi) {
    $scope.selectedReport = null;
    $scope.loading = false;
    $scope.harvesterReports = [];
    $scope.show = false;

    $scope.loadReports = loadReports;
    $scope.loadReportInPage = loadReportInPage;

    loadReports();

    function loadReports() {
        harvesterApi.getReport()
            .success(function(data) {
                $scope.harvesterReports = data;
            });
    }

    function loadReportInPage() {
        $scope.show = true;
    }
}

function HarvesterReportsCtrl($scope, $sce, harvesterApi) {
    $scope.selectedHarvester = null;
    $scope.harvesterReports = [];

    $scope.getResults = getResults;

    $scope.trustSrc = trustSrc;

    loadReports();

    function trustSrc(src) {
        return $sce.trustAsResourceUrl(src);
    }

    function loadReports() {
        harvesterApi.getReport()
            .success(function(data) {
                $scope.harvesterReports = data;
            })
    }

    function getResults() {

    }
}