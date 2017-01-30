var app = angular.module('forecaster', []);

app.controller('appCtrl', function($scope, $http) {
  $scope.rawData = '';
  $scope.dataReady = false;
  $scope.loading = false;
  $scope.showResult = false;

  $scope.result = {};

  var pos = ['adc', 'mid', 'top', 'jungle', 'support'];

  $scope.blueComp = pos.map(function(pos) {
    return {
      pos: pos,
      name: "",
      id: null,
      status: 'empty' // 'empty', 'loading', 'success', 'failed'
    }
  });

  $scope.purpleComp = pos.map(function(pos) {
    return {
      pos: pos,
      name: "",
      id: null,
      status: 'empty' // 'empty', 'loading', 'success', 'failed'
    }
  });

  // generate mock
  $scope.generateMock = function() {
    $scope.rawData = '["51878309", "22192141", "28239076", "34358720", "35527349", "20391818", "51399696", "44405988", "50740446", "21344514"]';
  }

  // watch the content of the 2 comp variables and update the final data
  var idsChanged = function(newVal, oldVal){
    var newRawData = $scope.blueComp.concat($scope.purpleComp).map(function(val) {return val.id;});
    var dataReady = newRawData.reduce(function(memo, v) {return memo - (v? 1 : 0);}, newRawData.length) == 0;
    if (dataReady) {
      $scope.rawData = '["' + newRawData.join('","') + '"]';
    }
  }

  $scope.$watch('blueComp', idsChanged , true);
  $scope.$watch('purpleComp', idsChanged , true);

  // watch the content of the rawData field to enable the submit button
  $scope.$watch('rawData', function(newVal, oldVal) {
    try {
      var newRawData = JSON.parse(newVal);
      if (newRawData.length = 10 && newRawData.reduce(function(memo, v) {return memo - (typeof(v) == 'string'? 1 : 0);}, newRawData.length) == 0)
        $scope.dataReady = true;
      else
        $scope.dataReady = false;
    } catch (e) { // invalid input
      $scope.dataReady = false;
    }
  })

  $scope.findID = function (pos) {
    pos.status = 'loading';
    getID(pos.name, function(id) {
      if (id != '') {
        pos.id = id;
        pos.status = 'success';
      } else {
        pos.id = '';
        pos.status = 'failed';
      }
    })
  }

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

  function getID(name, cb) {
    $http({
         url: 'name',
         method: "GET",
         params: {name: name}
    }).success(cb);
  }
});

function round(value, decimals) {
  return Number(Math.round(value+'e'+decimals)+'e-'+decimals);
}
