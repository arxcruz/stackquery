'use strict';

var angular = require('angular');
var directivesModule = require('./_index.js');

function Message() {
    return {
        restrict: 'E',
        templateUrl: '/views/message.html',
        scope: {
            errorMessage: '=?',
            successMessage: '=?'
        },

        link: function(scope, element, attrs) {
            scope.errorMessage = angular.isDefined(attrs.errorMessage) ? scope.$parent.$eval(attrs.errorMessage) : '';
            scope.successMessage = angular.isDefined(attrs.successMessage) ? scope.$parent.$eval(attrs.successMessage) : '';
            scope.hasError = function() {
                return scope.errorMessage !== '';
            };

            scope.hasSuccess = function() {
                return scope.successMessage !== '';
            };

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
    };
}

directivesModule.directive('sqMessage', Message);