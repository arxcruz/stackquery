angular.module('reports', ['ui.bootstrap', 'releases', 'ngCookies', 'ui.grid', 'ui.grid.pagination', 'ui.grid.resizeColumns', 'filters'])
    .controller('reportMainCtrl', ReportMainCtrl)
    .controller('stackReportsCtrl', StackReportsCtrl)
    .controller('bugzillaReportsCtrl', BugzillaReportsCtrl)
    .controller('scenarioCtrl', ScenarioCtrl)
    .controller('redHatBugzillaReportCtrl', RedHatBugzillaReportCtrl)
    .controller('redHatBugzillaReportListCtrl', RedHatBugzillaReportListCtrl)
    .controller('passwordCtrl', PasswordCtrl)
    .factory('bugzillaApi', bugzillaApi)
    .factory('scenarioApi', scenarioApi)
    .constant('bugzillaApiUrl', '/api/v1.0/reports')
    .constant('scenarioApiUrl', '/api/v1.0/scenarios')

function bugzillaApi($http, restApi, bugzillaApiUrl) {
    return {
        addBugzilla: function(bugzilla) {
            return restApi.post(bugzilla, bugzillaApiUrl);
        },
        getBugzilla: function() {
            return restApi.get(null, bugzillaApiUrl);
        },
        updateBugzilla: function(bugzilla) {
            return restApi.put(bugzilla, bugzilla.uri);
        },
        delBugzilla: function(bugzilla) {
            return restApi.del(null, bugzilla.uri);
        },
        getRHBugzillaReport: function(bugzilla) {
            var url = bugzillaApiUrl + '/show';
            return restApi.post(bugzilla, url);
        }
    }
}

function scenarioApi($http, restApi, scenarioApiUrl) {
    return {
        getScenarios: function(scenario) {
            return restApi.post(scenario, scenarioApiUrl);
        }
    }
}

function ReportMainCtrl($scope, $routeParams) {
    $scope.tabs = [{active: true}, {active: false}, {active: false}, {active: false}]
    var activeTab = parseInt($routeParams.tabId);

    setActive(activeTab);

    function setActive(tab) {
        if(tab) {
            $scope.tabs[tab].active = true;
        }
    }
}

function StackReportsCtrl($scope, releaseApi, teamApi, stackApi) {
    $scope.releases = [];
    $scope.teams = []
    $scope.selectedRelease = null;
    $scope.selectedTeam = null;
    $scope.selectedProjectType = null;
    $scope.selectedType = null;
    $scope.results = null;
    $scope.loading = false;

    $scope.getReleases = getReleases;
    $scope.getTeams = getTeams;
    $scope.getResults = getResults;

    getReleases();
    getTeams();

    function getReleases() {
        releaseApi.getReleases()
            .success(function(data) {
                $scope.releases = data;
            });
    }

    function getTeams() {
        teamApi.getTeams()
            .success(function(data) {
                $scope.teams = data;
            })
    }

    function getResults() {
        $scope.$broadcast('show-errors-check-validity');

        if ($scope.stackForm.$invalid) { 
            return; 
        }

        $scope.results = {};
        $scope.loading = true;
        var query = {
            users: $scope.selectedTeam.users,
            project_type: $scope.selectedProjectType.toLowerCase(),
            release: $scope.selectedRelease.name.toLowerCase(),
            type: $scope.selectedType
        };

        stackApi.getMetrics(query)
            .success(function(data) {
                $scope.results = data;
            })
            .finally(function() {
                $scope.loading = false;
            });
    }
}

function BugzillaReportsCtrl($scope, $cookies, $modal, bugzillaApi) {
    $scope.selectedBugzilla = null;
    $scope.bugzillaReports = [];
    $scope.loading = false;
    $scope.result = null;
    
    $scope.loadBugzilla = loadBugzilla;
    $scope.getResults = getResults;

    //$cookies.remove('username');
    //$cookies.remove('password');

    loadBugzilla();

    function loadBugzilla() {
        bugzillaApi.getBugzilla()
            .success(function(data) {
                $scope.bugzillaReports = data;
            });
    }

    function getResults() {
        // TODO: Find a better way to manage authentication
        if(!$scope.selectedBugzilla.require_authentication && !$cookies.get('username') && !$cookies.get('password')) {
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
        } else {
            $scope.loading = true;
            
            bugzillaApi.getRHBugzillaReport({report: $scope.selectedBugzilla})
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
    }
}

function ScenarioCtrl($scope, $modal, teamApi, scenarioApi, filterApi) {
    $scope.loading = false;
    $scope.selectedTeam = null;
    $scope.selectedFilter = null;
    $scope.results = [];
    $scope.filters = [];
    $scope.colSize = "col-sm-2";

    $scope.getResults = getResults;
    $scope.manageFilters = manageFilters;

    loadTeam();
    loadFilters();

    function getResults() {
        
        var scenario = {
            filters: $scope.selectedFilter.filter_desc,
            team: $scope.selectedTeam.id
        };

        $scope.loading = true;
        scenarioApi.getScenarios(scenario)
            .success(function(data) {
                $scope.results = data;
                if($scope.results.headers.length > 4) {
                    $scope.colSize = "col-sm-1";
                } else {
                    $scope.colSize = "col-sm-2";
                }
            })
            .error(function(errorInfo, status) {
                $scope.results = [];
            })
            .finally(function() {
                $scope.loading = false;
            })
    }

    function manageFilters() {
        var modalInstance = $modal.open({
            animation: true,
            templateUrl: 'manage_filters.html',
            controller: 'filtersCtrl',
            windowClass: 'app-modal-window',
            size: 'lg',
            resolve: {
                filters: function() {
                    return $scope.filters;
                }
            }
        });

        modalInstance.result.then(function(filters) {
            loadFilters();
        }, function() {
            loadFilters();
        });
    }

    function loadTeam() {
        teamApi.getTeams()
            .success(function(data) {
                $scope.teams = data;
            })
    }

    function loadFilters() {
        filterApi.getFilter()
            .success(function(data) {
                $scope.filters = data;
            })
    }
}


function PasswordCtrl($scope, $modalInstance) {
    $scope.model = {};
    $scope.ok = ok;
    $scope.cancel = cancel;

    function ok() {
        $modalInstance.close($scope.model);
    }

    function cancel() {
        $modalInstance.dismiss('cancel');
    }
}

/* Red Hat Bugzilla Reports Controllers */

function RedHatBugzillaReportCtrl($scope, bugzillaApi) {
    $scope.model = {};
    $scope.errorMessage = '';
    $scope.successMessage = '';

    $scope.hasError = hasError;
    $scope.hasSuccess = hasSuccess;
    $scope.createBugzillaReport = createBugzillaReport;

    function hasError() {
        return $scope.errorMessage != '';
    }

    function hasSuccess() {
        return $scope.successMessage != '';
    }

    function createBugzillaReport() {
        $scope.$broadcast('show-errors-check-validity');

        if ($scope.reportForm.$invalid) { 
            return; 
        }

        bugzillaApi.addBugzilla($scope.model)
            .success(function(data) {
                $scope.model = {}
                $scope.successMessage = 'Report added successfully';
                dismissMessages();
            })
            .error(function(errorInfo, status) {
                $scope.errorMessage = 'An error ocurred: ' + errorInfo.message;
            })
    }

    function dismissMessages() {
        setTimeout(function() {
            $scope.successMessage = '';
            $scope.errorMessage = '';
            $scope.$apply();
        }, 4000);
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

    $scope.hasError = hasError;
    $scope.hasSuccess = hasSuccess;
    $scope.refresh = refresh;
    $scope.isInReadMode = isInReadMode;
    $scope.isInEditMode = isInEditMode;
    $scope.startEdit = startEdit;
    $scope.save = save;
    $scope.cancel = reset;
    $scope.removeReport = removeReport;

    refresh();

    function hasError() {
        return $scope.errorMessage != '';
    }

    function hasSuccess() {
        return $scope.successMessage != '';
    }

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
        bugzillaApi.updateBugzilla(report)
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
        bugzillaApi.delBugzilla(report)
            .success(function(data) {
                var idx = $scope.bugzillaReports.indexOf(report);
                if(idx < 0) {
                    return;
                }
                $scope.bugzillaReports.splice(idx, 1);
                $scope.successMessage = 'Report ' + report.name + ' deleted successfully';
                dismissMessages();
            })
            .error(function(errorInfo, status) {
                $scope.errorMessage = 'An error ocurred: ' + errorInfo.message;
            })
            .finally(function() {
                reset();
            });
    }

    function dismissMessages() {
        setTimeout(function() {
            $scope.successMessage = '';
            $scope.errorMessage = '';
            $scope.$apply();
        }, 4000);
    }
}