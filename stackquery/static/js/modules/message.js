angular.module('stackqueryDirectives', [])
    .directive('sqMessage', Message)

function Message() {
    return {
        restrict: 'E',
        templateUrl: 'static/js/modules/templates/message.html',
        scope: {
            errorMessage: '=?',
            successMessage: '=?'
        },

        link: function(scope, element, attrs) {
            scope.errorMessage = angular.isDefined(attrs.errorMessage) ? scope.$parent.$eval(attrs.errorMessage) : '';
            scope.successMessage = angular.isDefined(attrs.successMessage) ? scope.$parent.$eval(attrs.successMessage) : '';
            scope.hasError = function() {
                return scope.errorMessage != '';
            }

            scope.hasSuccess = function() {
                return scope.successMessage != '';
            }

            scope.$watch('successMessage', function(newValue, oldValue) {
                dismissMessages();
            });

            function dismissMessages() {
                setTimeout(function() {
                    scope.successMessage = '';
                    scope.errorMessage = '';
                    scope.$apply();
                }, 4000);
            }
        }
    }
} 