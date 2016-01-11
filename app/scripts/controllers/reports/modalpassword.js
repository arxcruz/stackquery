'use strict';

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

export default {
    name: 'passwordCtrl',
    fn: PasswordCtrl
};
