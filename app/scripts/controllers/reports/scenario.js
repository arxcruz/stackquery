'use strict';

var angular = require('angular');

function ScenarioCtrl($scope, $modal, $cookies, $interval, teamApi, scenarioApi, filterApi) {
    $scope.loading = false;
    $scope.selectedTeam = null;
    $scope.selectedFilter = null;
    $scope.results = [];
    $scope.filters = [];
    $scope.colSize = 'col-sm-2';

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
                    $scope.colSize = 'col-sm-1';
                } else {
                    $scope.colSize = 'col-sm-2';
                }
            })
            .error(function(errorInfo, status) {
                $scope.results = [];
            })
            .finally(function() {
                $scope.loading = false;
            });
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
                    for(var i = 0; i < $scope.teams.length; i++) {
                        if($scope.teams[i].id ===  team) {
                            $scope.selectedTeam = $scope.teams[i];
                            break;
                        }
                    }
                }
            });
    }

    function loadFilters() {
        filterApi.getFilter()
            .success(function(data) {
                $scope.filters = data;
            })
            .then(function(res) {
                var filter = $cookies.get('scenario_filter');
                if(filter) {
                    for(var i = 0; i < $scope.filters.length; i++) {
                        if($scope.filters[i].id ===  filter) {
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

        return (team && team.id ===  _team && filter && filter.id ===  _filter);
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

export default {
    name: 'scenarioCtrl',
    fn: ScenarioCtrl
};
