angular.module('reports', ['ui.bootstrap', 'releases'])
    .controller('reportMainCtrl', ReportMainCtrl)
    .controller('stackReportsCtrl', StackReportsCtrl)

function ReportMainCtrl($scope, $routeParams) {
    $scope.tabs = [{active: true}, {active: false}, {active: false}]
    var activeTab = $routeParams.tab;

    setActive(activeTab)

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