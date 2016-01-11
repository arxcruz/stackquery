'use strict';

var angular = require('angular');

function StackReportsCtrl($scope, $cookies, $interval, releaseApi, teamApi, stackApi) {
    $scope.releases = [];
    $scope.teams = [];
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
                    for(var i = 0; i < $scope.releases.length; i++) {
                        if($scope.releases[i].id ===  release) {
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
                    for(var i = 0; i < $scope.teams.length; i++) {
                        if($scope.teams[i].id ===  team) {
                            $scope.selectedTeam = $scope.teams[i];
                            break;
                        }
                    }
                }
            });
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
        var type = $scope.selectedType;
        var project_type = $scope.selectedProjectType;

        var _team = $cookies.get('team');
        var _release = $cookies.get('release');
        var _type = $cookies.get('type');
        var _project_type = $cookies.get('project_type');

        return (team && team.id ===  _team && release && release.id ===  _release && type ===  _type && project_type ===  _project_type);
    }

    function startSavedResult() {
        if(angular.isDefined(stop)) {
            return;
        }

        stop = $interval(function() {
            var team = $scope.selectedTeam;
            var release = $scope.selectedRelease;
            var type = $scope.selectedType;
            var project_type = $scope.selectedProjectType;

            if(team && release && type && project_type) {
                getResults();
                stopSavedResult();
            }    
        }, 100);
        
    }

    function getSaved() {
        var project_type = $cookies.get('project_type');
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

export default {
    name: 'stackReportsCtrl',
    fn: StackReportsCtrl
};
