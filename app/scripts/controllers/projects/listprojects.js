'use strict';

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

    var selectedId = -1;
    var loading = false;

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

export default {
    name: 'projectListCtrl',
    fn: ProjectListCtrl
};