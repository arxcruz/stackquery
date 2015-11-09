angular.module('teams', ['ui.bootstrap', 'users', 'projects'])
    .controller('teamCtrl', TeamCtrl)
    .controller('teamListCtrl', TeamListCtrl)
    .controller('teamProjectAndUsersCtrl', TeamProjectAndUsersCtrl)
    .factory('teamApi', teamApi)
    .constant('teamApiUrl', '/api/v1.0/teams');

function teamApi($http, restApi, teamApiUrl) {
    return {
        addTeam: function(team) {
            return restApi.post(team, teamApiUrl);
        },
        getTeams: function() {
            return restApi.get(null, teamApiUrl);
        },
        updateTeam: function(team) {
            return restApi.put(team, team.uri);
        },
        delTeam: function(team) {
            return restApi.del(null, team.uri);
        }
    }
}

function TeamListCtrl($scope, $modal, teamApi, teamApiUrl) {
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
        $scope.teamName = team.name
        var modalInstance = $modal.open({
            animation: true,
            templateUrl: 'edit_team.html',
            controller: 'teamProjectAndUsersCtrl',
            windowClass: 'app-modal-window',
            size: 'lg',
            resolve: {
                projects: function() {
                    return $scope.projects;
                },
                users: function() {
                    return $scope.users;
                },
                teamName: function() {
                    return $scope.teamName;
                }
            }
        });

        modalInstance.result.then(function (result) {         
            team.projects = result.projects;
            team.users = result.users;
            team.name = result.teamName;

            console.log(team);
            teamApi.updateTeam(team)
                .success(function(data) {
                    $scope.successMessage = 'Team updated successfully';
                    dismissMessages();
                })
                .error(function(errorInfo, status) {
                    $scope.errorMessage = 'An error ocurred: ' + errorInfo.message;
                })
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
            })
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

function TeamCtrl($scope, $modal, teamApi, teamApiUrl) {
    $scope.errorMessage = '';
    $scope.successMessage = '';
    $scope.model = {};
    $scope.users = [];
    $scope.projects = [];
    $scope.currentPageUsers = 1;
    $scope.currentPageProjects = 1;

    $scope.createTeam = createTeam;
    $scope.assignUsersAndProjects = assignUsersAndProjects;
    $scope.removeUser = removeUser;
    $scope.removeProject = removeProject;

    function createTeam() {
        $scope.$broadcast('show-errors-check-validity');

        if ($scope.teamForm.$invalid) { 
            return; 
        }

        var team = {
            name: $scope.model.teamName,
            users: $scope.users,
            projects: $scope.projects
        };

        teamApi.addTeam(team)
            .success(
                function (data) {
                    reset();
                    $scope.successMessage = 'Team added successfully';
                })
            .error(
                function (errorInfo, status) {
                    $scope.errorMessage = 'An error ocurred: ' + errorInfo.message;
                });  
    }

    function assignUsersAndProjects() {

        var modalInstance = $modal.open({
            animation: true,
            templateUrl: 'edit_team.html',
            controller: 'teamProjectAndUsersCtrl',
            windowClass: 'app-modal-window',
            size: 'lg',
            resolve: {
                projects: function() {
                    return $scope.projects;
                },
                users: function() {
                    return $scope.users;
                },
                teamName: function() {
                    return null;
                }
            }
        });

        modalInstance.result.then(function (result) {
            
            $scope.users = result.users;
            $scope.projects = result.projects;
        });
    }

    function removeUser(user) {
        var idx = $scope.users.indexOf(user);
        if(idx < 0) {
            return;
        }
        $scope.users.splice(idx, 1);
    }

    function removeProject(project) {
        var idx = $scope.projects.indexOf(project);
        if(idx < 0) {
            return;
        }
        $scope.projects.splice(idx, 1);
    }

    function reset() {
        $scope.model = {};
        $scope.users = [];
        $scope.projects = [];
    }
}

function TeamProjectAndUsersCtrl($scope, $modalInstance, projects, users, teamName, userApi, projectApi) {
    $scope.projects = projects;
    $scope.loadedProjects = [];
    $scope.users = users;
    $scope.loadedUsers = [];
    $scope.usersPageSize = 10;
    $scope.usersCurrentPage = 1;
    $scope.projectsPageSize = 10;
    $scope.projectsCurrentPage = 1;

    $scope.teamName = teamName;

    $scope.addUser = addUser;
    $scope.removeUser = removeUser;
    $scope.refreshUser = refreshUser;

    $scope.addProject = addProject;
    $scope.removeProject = removeProject;
    $scope.projectContains = projectContains;
    $scope.userContains = userContains;

    $scope.ok = ok;
    $scope.cancel = cancel;
    $scope.refreshProject = refreshProject;


    refreshProject();
    refreshUser();

    function userContains(user) {
        for(var i = 0; i < $scope.users.length; i++) {
            var usr = $scope.users[i];
            if(usr.id == user.id) {
                return i;
            }
        }
        return -1;
    }

    function projectContains(project) {
        for(var i = 0; i < $scope.projects.length; i++) {
            var prj = $scope.projects[i];
            if(prj.id == project.id) {
                return i;
            }
        }
        return -1;
    }

    function addProject(project) {
        $scope.projects.push(project);
    }

    function removeProject(project) {
        var idx = projectContains(project);
        if(idx < 0) {
            return;
        }
        $scope.projects.splice(idx, 1);
    }

    function refreshProject() {
        if($scope.loadedProjects.length == 0) {
            $scope.loading = true;
            projectApi.getProjects()
                .success(
                    function(data) {
                        $scope.loadedProjects = data;
                    })
                .error(
                    function(errorInfo, status) {

                    })
                .finally(function() {
                    $scope.loading = false;
                });
        }
    }

    function addUser(user) {
        $scope.users.push(user);
    }

    function removeUser(user) {
        var idx = userContains(user);
        if(idx < 0) {
            return;
        }
        $scope.users.splice(idx, 1);
    }

    function refreshUser() {
        if($scope.loadedUsers.length == 0) {
            $scope.loading = true;
            userApi.getUsers()
                .success(
                    function(data) {
                        $scope.loadedUsers = data;
                    })
                .error(
                    function(errorInfo, status) {

                    })
                .finally(function() {
                    $scope.loading = false;
                });
        }
    }

    function ok() {
        result = {projects: $scope.projects, users: $scope.users}
        if($scope.teamName) {
            result["teamName"] = $scope.teamName;
        }
        $modalInstance.close(result);
    }

    function cancel() {
        $modalInstance.dismiss('cancel');
    }
}