'use strict';

function TeamListCtrl($scope, $modal, teamApi) {
    $scope.errorMessage = '';
    $scope.successMessage = '';
    $scope.teams = [];
    $scope.currentPage = 1;
    $scope.pageSize = 10;

    $scope.refresh = refresh;
    $scope.editTeam = editTeam;
    $scope.removeTeam = removeTeam;

    refresh();

    function editTeam(team) {
        $scope.projects = team.projects;
        $scope.users = team.users;
        $scope.teamName = team.name;
        var modalInstance = $modal.open({
            animation: true,
            templateUrl: 'edit_team.html',
            controller: 'teamProjectAndUsersCtrl',
            windowClass: 'app-modal-window',
            size: 'lg',
            resolve: {
                users: function() {
                    return $scope.users;
                },
                teamName: function() {
                    return $scope.teamName;
                }
            }
        });

        modalInstance.result.then(function (result) {         
            team.users = result.users;
            team.name = result.teamName;

            teamApi.updateTeam(team)
                .success(function(data) {
                    $scope.successMessage = 'Team updated successfully';
                })
                .error(function(errorInfo, status) {
                    $scope.errorMessage = 'An error ocurred: ' + errorInfo.message;
                });
        });
    }

    function removeTeam(team) {
        teamApi.delTeam(team)
            .success(function(data) {
                var idx = $scope.teams.indexOf(team);
                if(idx < 0) {
                    return;
                }
                $scope.teams.splice(idx, 1);
                $scope.successMessage = 'Team ' + team.name + ' deleted successfully';
            })
            .error(function(errorInfo, status) {
                $scope.errorMessage = 'An error ocurred: ' + errorInfo.message;
            });
    }

    function refresh() {
        $scope.loading = true;
        teamApi.getTeams()
            .success(
                function(data) {
                    $scope.teams = data;
                })
            .error(
                function(errorInfo, status) {

                })
            .finally(function() {
                $scope.loading = false;
            });
    }
}

export default {
    name: 'teamListCtrl',
    fn: TeamListCtrl
};
