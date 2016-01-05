angular.module('reports', ['ui.bootstrap', 'releases', 'ngCookies', 'ui.grid', 'ui.grid.pagination', 'filters'])
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

function StackReportsCtrl($scope, $cookies, $interval, releaseApi, teamApi, stackApi) {
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
    $scope.saveAsDefault = saveAsDefault;
    $scope.isSaveEnabled = isSaveEnabled;

    var stop;

    getReleases();
    getTeams();
    getSaved();
    startSavedResult();


    function getReleases() {
        releaseApi.getReleases()
            .success(function(data) {
                $scope.releases = data;
            })
            .then(function(res) {
                var release = $cookies.get('release');
                if(release) {
                    for(i = 0; i < $scope.releases.length; i++) {
                        if($scope.releases[i].id == release) {
                            $scope.selectedRelease = $scope.releases[i];
                            break;
                        }
                    }
                }
            });
    }

    function getTeams() {
        teamApi.getTeams()
            .success(function(data) {
                $scope.teams = data;
            })
            .then(function(res) {
                var team = $cookies.get('team');
                if(team) {
                    for(i = 0; i < $scope.teams.length; i++) {
                        if($scope.teams[i].id == team) {
                            $scope.selectedTeam = $scope.teams[i];
                            break;
                        }
                    }
                }
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

    function saveAsDefault() {
        $cookies.put('team', $scope.selectedTeam.id);
        $cookies.put('project_type', $scope.selectedProjectType);
        $cookies.put('release', $scope.selectedRelease.id);
        $cookies.put('type', $scope.selectedType);
    }

    function isSaveEnabled() {
        var team = $scope.selectedTeam;
        var release = $scope.selectedRelease;
        var type = $scope.selectedType
        var project_type = $scope.selectedProjectType;

        var _team = $cookies.get('team');
        var _release = $cookies.get('release');
        var _type = $cookies.get('type');
        var _project_type = $cookies.get('project_type');

        return (team && team.id == _team && release && release.id == _release && type == _type && project_type == _project_type);
    }

    function startSavedResult() {
        if(angular.isDefined(stop)) {
            return;
        }

        stop = $interval(function() {
            var team = $scope.selectedTeam;
            var release = $scope.selectedRelease;
            var type = $scope.selectedType
            var project_type = $scope.selectedProjectType;

            if(team && release && type && project_type) {
                getResults();
                stopSavedResult();
            }    
        }, 100);
        
    }

    function getSaved() {
        var project_type = $cookies.get('project_type')
        if(project_type) {
            $scope.selectedProjectType = project_type;
        }

        var type = $cookies.get('type');
        if(type) {
            $scope.selectedType = type;
        }
    }

    function stopSavedResult() {
        if(angular.isDefined(stop)) {
            $interval.cancel(stop);
            stop = undefined;
        }
    }

    
}

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
                    for(i = 0; i < $scope.bugzillaReports.length; i++) {
                        if($scope.bugzillaReports[i].id == report) {
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

    function saveAsDefault() {
        $cookies.put('bz_report', $scope.selectedBugzilla.id);
    }

    function isSaveEnabled() {
        var _bz_report = $cookies.get('bz_report');
        var bz_report = $scope.selectedBugzilla;
        return (bz_report && bz_report.id == _bz_report);
    }
}

function ScenarioCtrl($scope, $modal, $cookies, $interval, teamApi, scenarioApi, filterApi) {
    $scope.loading = false;
    $scope.selectedTeam = null;
    $scope.selectedFilter = null;
    $scope.results = [];
    $scope.filters = [];
    $scope.colSize = "col-sm-2";

    $scope.getResults = getResults;
    $scope.manageFilters = manageFilters;
    $scope.saveAsDefault = saveAsDefault;
    $scope.isSaveEnabled = isSaveEnabled;

    var stop;

    loadTeam();
    loadFilters();
    startSavedResult();

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
            .then(function(res) {
                var team = $cookies.get('scenario_team');
                if(team) {
                    for(i = 0; i < $scope.teams.length; i++) {
                        if($scope.teams[i].id == team) {
                            $scope.selectedTeam = $scope.teams[i];
                            break;
                        }
                    }
                }
            })
    }

    function loadFilters() {
        filterApi.getFilter()
            .success(function(data) {
                $scope.filters = data;
            })
            .then(function(res) {
                var filter = $cookies.get('scenario_filter');
                if(filter) {
                    for(i = 0; i < $scope.filters.length; i++) {
                        if($scope.filters[i].id == filter) {
                            $scope.selectedFilter = $scope.filters[i];
                            break;
                        }
                    }
                }
            });
    }

    function saveAsDefault() {
        $cookies.put('scenario_team', $scope.selectedTeam.id);
        $cookies.put('scenario_filter', $scope.selectedFilter.id);
    }

    function isSaveEnabled() {
        var team = $scope.selectedTeam;
        var filter = $scope.selectedFilter;
        var _team = $cookies.get('scenario_team');
        var _filter = $cookies.get('scenario_filter');

        return (team && team.id == _team && filter && filter.id == _filter);
    }

    function startSavedResult() {
        if(angular.isDefined(stop)) {
            return;
        }

        stop = $interval(function() {
            var team = $scope.selectedTeam;
            var filter = $scope.selectedFilter;

            if(team && filter) {
                getResults();
                stopSavedResult();
            }    
        }, 100);
    }

    function stopSavedResult() {
        if(angular.isDefined(stop)) {
            $interval.cancel(stop);
            stop = undefined;
        }
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

    $scope.createBugzillaReport = createBugzillaReport;

    function createBugzillaReport() {
        $scope.$broadcast('show-errors-check-validity');

        if ($scope.reportForm.$invalid) { 
            return; 
        }

        bugzillaApi.addBugzilla($scope.model)
            .success(function(data) {
                $scope.model = {}
                $scope.successMessage = 'Report added successfully';
            })
            .error(function(errorInfo, status) {
                $scope.errorMessage = 'An error ocurred: ' + errorInfo.message;
            })
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