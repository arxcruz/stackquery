angular.module('projects', [])
    .controller('projectCtrl', ProjectCtrl)
    .controller('projectListCtrl', ProjectListCtrl)
    .factory('projectApi', projectApi)
    .constant('projectApiUrl', '/api/v1.0/projects');

function projectApi($http, restApi, projectApiUrl) {
    return {
        addProject: function(project) {
            return restApi.post(project, projectApiUrl);
        },
        getProjects: function() {
            return restApi.get(null, projectApiUrl);
        },
        updateProject: function(project) {
            return restApi.put(project, project.uri);
        },
        delProject: function(project) {
            return restApi.del(null, project.uri);
        }
    }
}

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

function ProjectListCtrl($scope, projectApi) {
    var editFlag = false;

    $scope.projects = [];
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
    $scope.removeProject = removeProject;
    $scope.cancel = reset;

    refresh();

    function refresh() {
        $scope.loading = true;
        $scope.projects = [];
        projectApi.getProjects()
            .success(
                function(data) {
                    $scope.projects = data;
                })
            .error(
                function(errorInfo, status) {

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

    function save(project) {
        projectApi.updateProject(project)
            .success(function(data) {
                $scope.successMessage = 'Project: ' + project.name + ' updated successfully';
            })
            .error(function(errorInfo, status) {
                $scope.errorMessage = 'An error ocurred: ' + errorInfo.message;
            })
            .finally(function() {
                reset();
            });
    }

    function removeProject(project) {
        projectApi.delProject(project)
            .success(function(data) {
                var idx = $scope.projects.indexOf(project);
                if(idx < 0) {
                    return;
                }
                $scope.projects.splice(idx, 1);
                $scope.successMessage = 'Project ' + project.name + ' deleted successfully';
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
}