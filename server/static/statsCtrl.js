var app = angular.module('forecaster', []);

app.controller('statsCtrl', function($scope, $http) {
  $scope.data = {GPM: {
    counts: [1, 2],
    bins: [5, 6, 7]
  }}
});

app.directive('d3Hist', function($timeout, $window) {
  return {
    restrict: 'EA',
    scope: {
        data: '=' // bi-directional data-binding
      },
    link: function(scope, element, attrs) {
      element.ready(function () {
        var height, width;
        $timeout(function () {

          var svg = d3.select(element[0])
            .append('svg')
            .style('width', '100%');

          // Browser onresize event
          window.onresize = function() {
            scope.$apply();
          };

          // Watch for resize event
          scope.$watch(function() {
            return angular.element($window)[0].innerWidth;
          }, function() {
            scope.render(scope.data);
          });

          // watch for a change in the data
          scope.$watch("data", function() {
            scope.render(scope.data);
          }, true)


          scope.render = function(data) {
            height  = element[0].offsetHeight;
            width  = element[0].offsetWidth;
            console.log('render')

            svg.selectAll('*').remove();
            if (!data) return;

          }


        });
      });
    }
  };
});
