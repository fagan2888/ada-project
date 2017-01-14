var app = angular.module('forecaster', []);

app.controller('appCtrl', function($scope, $http) {
  $scope.rawData = '["31858318", "42270213", "56396690", "45290268", "53012710", "31877470", "19931164", "30857494", "24752272", "62835377"]'
  $scope.loading = false;
  $scope.showResult = false;

  $scope.result = {};

  $scope.submitForm = function() {

    $scope.loading = true;
    $scope.showResult = false;

    postRequest($scope.rawData, function(res) {
      $scope.loading = false;

      var blueVictory = round(parseFloat(res.blue_victory)*100, 2);
      $scope.result.blue = blueVictory
      $scope.result.purple = 100 - blueVictory;
      $scope.showResult = true;

    });


  }

  function postRequest(data, cb) {
    $http({
        method: 'POST',
        url: 'forecast',
        data: "summs=" + data,
        headers: {'Content-Type': 'application/x-www-form-urlencoded'}
    }).success(cb);
  }
});

function round(value, decimals) {
  return Number(Math.round(value+'e'+decimals)+'e-'+decimals);
}
