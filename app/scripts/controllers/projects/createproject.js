'use strict';

function ProjectCtrl($scope, projectApi) {
    $scope.errorMessage = '';
    $scope.successMessage = '';
    $scope.model = {gerritServer: 'https://review.openstack.org'};
    $scope.users = [];
    $scope.projects = [];

    $scope.createProject = createProject;

    reset();

    function reset() {
        $scope.model = {gerritServer: 'https://review.openstack.org'};
    }

    function createProject() {
        $scope.$broadcast('show-errors-check-validity');

        if ($scope.projectForm.$invalid) { 
            return; 
        }

        var project = {
            name: $scope.model.projectName,
            git_url: $scope.model.projectUrl,
            gerrit_server: $scope.model.gerritServer
        };

        projectApi.addProject(project)
            .success(
                function (data) {
                    reset();
                    $scope.successMessage = 'Project added successfully';
                })
            .error(
                function (errorInfo, status) {
                    $scope.errorMessage = 'An error ocurred: ' + errorInfo.message;
                });  
    }
}

export default {
    name: 'projectCtrl',
    fn: ProjectCtrl
};