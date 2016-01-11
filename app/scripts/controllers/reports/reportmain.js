'use strict';

function ReportMainCtrl($scope, $routeParams) {
    $scope.tabs = [{active: true}, {active: false}, {active: false}, {active: false}];
    var activeTab = parseInt($routeParams.tabId);

    setActive(activeTab);

    function setActive(tab) {
        if(tab) {
            $scope.tabs[tab].active = true;
        }
    }
}

export default {
    name: 'reportMainCtrl',
    fn: ReportMainCtrl
};
