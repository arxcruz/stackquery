'use strict';

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
                $scope.model = {};
                $scope.successMessage = 'Report added successfully';
            })
            .error(function(errorInfo, status) {
                $scope.errorMessage = 'An error ocurred: ' + errorInfo.message;
            });
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

    // TODO: Check if still needed
    var selectedId = -1;
    var editFlag = false;
    var loading = false;

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

    function save(report) {
        harvesterApi.updateReport(report)
            .success(function(data) {
                $scope.successMessage = 'Report: ' + report.name + ' updated successfully';
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

function HarvesterReportsCtrl($scope, $cookies, $sce, harvesterApi) {
    $scope.selectedHarvester = null;
    $scope.harvesterReports = [];

    $scope.saveAsDefault = saveAsDefault;
    $scope.isSaveEnabled = isSaveEnabled;

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
            .then(function(res) {
                var report = $cookies.get('hv_report');
                if(report) {
                    for(var i = 0; i < $scope.harvesterReports.length; i++) {
                        if($scope.harvesterReports[i].id === report) {
                            $scope.selectedHarvester = $scope.harvesterReports[i];
                            //trustSrc($scope.selectedHarvester.url);
                            break;
                        }
                    }
                }
            });
    }

    function isSaveEnabled() {
        var _report = $cookies.get('hv_report');
        var report = $scope.selectedHarvester;

        return (report && report.id === _report);
    }

    function saveAsDefault() {
        $cookies.put('hv_report', $scope.selectedHarvester.id);
    }
}

export default [
    {
        name: 'harvesterReportCtrl',
        fn: HarvesterReportCtrl
    },
    {
        name: 'harvesterReportListCtrl',
        fn: HarvesterReportListCtrl
    },
    {
        name: 'harvesterReportsCtrl',
        fn: HarvesterReportsCtrl
    },
    {
        name: 'harvesterCtrl',
        fn: HarvesterCtrl
    }
];
