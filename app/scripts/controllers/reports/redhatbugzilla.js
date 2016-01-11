'use strict';

function BugzillaReportsCtrl($scope, $cookies, $modal, bugzillaApi) {
    $scope.selectedBugzilla = null;
    $scope.bugzillaReports = [];
    $scope.loading = false;
    $scope.result = null;
    
    $scope.loadBugzilla = loadBugzilla;
    $scope.getResults = getResults;
    $scope.saveAsDefault = saveAsDefault;
    $scope.isSaveEnabled = isSaveEnabled;

    //$cookies.remove('username');
    //$cookies.remove('password');

    loadBugzilla();

    function loadBugzilla() {
        bugzillaApi.getBugzilla()
            .success(function(data) {
                $scope.bugzillaReports = data;
            })
            .then(function(res) {
                var report = $cookies.get('bz_report');
                if(report) {
                    for(var i = 0; i < $scope.bugzillaReports.length; i++) {
                        if($scope.bugzillaReports[i].id ===  report) {
                            $scope.selectedBugzilla = $scope.bugzillaReports[i];
                            if($cookies.get('username') && $cookies.get('password')) {
                                getResults();
                            }
                            break;
                        }
                    }
                }
            });
    }

    function getResults() {
        // TODO: Find a better way to manage authentication
        if(!$cookies.get('username') && !$cookies.get('password')) {
            // Load username and login popup
            var modalInstance = $modal.open({
                animation: true,
                templateUrl: 'password.html',
                controller: 'passwordCtrl',
                windowClass: 'app-modal-window',
            });

            modalInstance.result.then(function(result) {
                var expireDate = new Date();
                expireDate.setDate(expireDate.getDate() + 1);
                $cookies.put('username', result.username, {'expires': expireDate});
                $cookies.put('password', result.password, {'expires': expireDate});
            });
            loadReport();
        } else {
            loadReport();
        }
    }

    function loadReport() {
        $scope.loading = true;
            
        bugzillaApi.getRHBugzillaReport({
                report: $scope.selectedBugzilla,
                username: $cookies.get('username'),
                password: $cookies.get('password')
            })
            .success(function(data) {
                $scope.result = data;
            })
            .error(function(errorInfo, status) {
                $scope.result = null;
            })
            .finally(function() {
                $scope.loading = false;
            });
    }

    function saveAsDefault() {
        $cookies.put('bz_report', $scope.selectedBugzilla.id);
    }

    function isSaveEnabled() {
        var _bz_report = $cookies.get('bz_report');
        var bz_report = $scope.selectedBugzilla;
        return (bz_report && bz_report.id ===  _bz_report);
    }
}

function RedHatBugzillaReportCtrl($scope, bugzillaApi) {
    $scope.model = {};
    $scope.errorMessage = '';
    $scope.successMessage = '';

    $scope.createBugzillaReport = createBugzillaReport;

    function createBugzillaReport() {
        $scope.$broadcast('show-errors-check-validity');

        if ($scope.reportForm.$invalid) { 
            return; 
        }

        bugzillaApi.addBugzilla($scope.model)
            .success(function(data) {
                $scope.model = {};
                $scope.successMessage = 'Report added successfully';
            })
            .error(function(errorInfo, status) {
                $scope.errorMessage = 'An error ocurred: ' + errorInfo.message;
            });
    }
}

function RedHatBugzillaReportListCtrl($scope, bugzillaApi) {

    $scope.bugzillaReports = [];
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

    // TODO: Verify if we still need this variables
    var selectedId = -1;
    var editFlag = false;
    var loading = false;

    refresh();

    function refresh() {
        $scope.loading = true;
        $scope.bugzillaReports = [];
        bugzillaApi.getBugzilla()
            .success(function(data) {
                $scope.bugzillaReports = data;
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
        bugzillaApi.updateBugzilla(report)
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
        bugzillaApi.delBugzilla(report)
            .success(function(data) {
                var idx = $scope.bugzillaReports.indexOf(report);
                if(idx < 0) {
                    return;
                }
                $scope.bugzillaReports.splice(idx, 1);
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

export default [
    {
        name: 'bugzillaReportsCtrl',
        fn: BugzillaReportsCtrl
    },
    {
        name: 'redHatBugzillaReportCtrl',
        fn: RedHatBugzillaReportCtrl
    },
    {
        name: 'redHatBugzillaReportListCtrl',
        fn: RedHatBugzillaReportListCtrl
    }
];
