var app = angular.module('forecaster', []);

app.controller('statsCtrl', function($scope, $http) {
  $http({
    method: 'GET',
    url: 'stats.json'
  }).then(function (response) {
    $scope.stats = response.data;
  });


  $scope.cumulative = false;

  $scope.features = [
    {key: 'GPM', text: 'Gold Per Minute'},
    {key: 'KD', text: 'Kills / Deaths'},
    {key: 'KDA', text: '(Kills + Assists) / Deaths'},
    {key: 'cs10', text: 'Last hits per minute in the first 10 minutes of the game'},
    {key: 'cs20', text: 'Last hits per minute in minute 10 - 20'},
    {key: 'csDiff10', text: 'Difference in Last hits per minute in the first 10 minutes of the game (compared to the lane opponent)'},
    {key: 'csDiff20', text: 'Difference in Last hits per minute in minute 10 - 20 (compared to the lane opponent)'},
    {key: 'gpm10', text: 'Gold per minute in the first 10 minutes of the game'},
    {key: 'gpm20', text: 'Gold per minute in minute 10 - 20'},
    {key: 'largestKillingSpree', text: 'Largest killing spree'},
    {key: 'totalDamageDealt', text: 'Total damage dealt'},
    {key: 'totalDamageDealtToChampions', text: 'Total damage dealt to champions'},
    {key: 'totalDamageTaken', text: 'Total damage daken'},
    {key: 'totalTimeCrowdControlDealt', text: 'Duration of crowd control dealt'},
    {key: 'winrate', text: 'Winrate'},
    {key: 'xpDiff10', text: 'Difference in experience per minute in the first 10 minutes of the game (compared to the lane opponent)'},
    {key: 'xpDiff20', text: 'Difference in experience per minute in minute 10 - 20 (compared to the lane opponent)'}
  ];

  $scope.queryName = function (name) {
    $scope.status = 'loading';
    getID(name, function(id) {
      if (id != '') {
        getFeatures(id, function(features) {
          $scope.status = 'success';
          $scope.player_features = (mapFeatures(features[0]));
        });
      } else {
        $scope.status = 'failed';
        $scope.player_features = null;
      }
    });
  }

  function mapFeatures(features) {
    var keys = ["winrate", "GPM", "KDA", "KD", "largestKillingSpree", "totalDamageDealt",
              "totalDamageDealtToChampions", "totalDamageTaken","totalTimeCrowdControlDealt",
              "cs10", "cs20", "csDiff10", "csDiff20", "gpm10", "gpm20", "xpDiff10", "xpDiff20"];
    var features_obj = {};
    for (var i = 0; i < keys.length; i++) {
      features_obj[keys[i]] = features[i];
    }

    return features_obj;
  }

  function getFeatures(id, cb) {
    $http({
         url: 'features',
         method: "GET",
         params: {id: id}
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

app.directive('d3Hist', function($timeout, $window) {
  return {
    restrict: 'EA',
    scope: {
        data: '=',
        cumulative: '=',
        playerValue: '='
      },
    link: function(scope, element, attrs) {
      element.ready(function () {
        var height, width;
        $timeout(function () {
          // Browser onresize event
          window.onresize = function() {
            scope.$apply();
          };

          // Watch for resize event
          scope.$watch(function() {
            return angular.element($window)[0].innerWidth;
          }, function() {
            scope.render(scope.data, scope.cumulative, scope.playerValue);
          });

          // watch for a change in the data
          scope.$watch("data", function() {
            scope.render(scope.data, scope.cumulative, scope.playerValue);
          }, true);

          // watch for a change in the distribution type
          scope.$watch("cumulative", function() {
            scope.render(scope.data, scope.cumulative, scope.playerValue);
          }, true)

          // watch for a change in the player value
          scope.$watch("playerValue", function() {
            scope.render(scope.data, scope.cumulative, scope.playerValue);
          }, true)



          scope.render = function(data, cumulative, player_value) {
            if (!data) return;

            if (cumulative) { // add past values in the data array
              var oldData = data;
              data = [oldData[0]];
              for (var i = 1; i < oldData.length; i++) {
                data.push({
                  x0: oldData[i].x0,
                  x1: oldData[i].x1,
                  count: data[i-1].count + oldData[i].count
                });
              }
            }

            width  = $(element[0]).parent().width();
            height = width * 0.5;

            d3.select(element[0]).selectAll('*').remove();

            var svg = d3.select(element[0]).append('svg').style('width', '100%')

            svg.style('height', height).style('width', width);

            // var data = d3.range(1000).map(d3.randomBates(10));
            var formatCount = d3.format(",.0f");

            var margin = {top: 10, right: 30, bottom: 30, left: 30},
                width = width - margin.left - margin.right,
                height = height - margin.top - margin.bottom,
                g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

            var x = d3.scaleLinear()
                // .domain([250, 500])
                .domain([data[0].x0, data[data.length-1].x1])
                .rangeRound([0, width]);

            var max = d3.max(data, function(d) { return d.count; });

            var y = d3.scaleLinear()
                .domain([0, max])
                .range([height, 0]);

            var bar = g.selectAll(".bar")
              .data(data)
              .enter().append("g")
                .attr("class", "bar")
                .attr("transform", function(d) { return "translate(" + x(d.x0) + "," + y(d.count) + ")"; });

            bar.append("rect")
                .attr("x", 1)
                .attr("width", x(data[0].x1) - x(data[0].x0) - 1)
                .attr("height", function(d) { return height - y(d.count); });

            g.append("g")
                .attr("class", "axis axis--x")
                .attr("transform", "translate(0," + height + ")")
                .call(d3.axisBottom(x));

            // show the feature value of the player
            if(player_value) {
              g.append("line")
                 .attr("y1", y(0))
                 .attr("y2", y(max))
                 .attr("x1", x(player_value))
                 .attr("x2", x(player_value))
                 .attr( "stroke", "red" )
                 .attr( "stroke-width", "2" )
            }
            refreshGrid();
          }
        });
      });
    }
  };
});

var notRefreshed = true;

// watcher for masonry
function refreshGrid () {
  setTimeout(function() {
    if (notRefreshed) {
      console.log('refresh')
      $('.grid').masonry({
          itemSelector: '.col',
      });
      notRefreshed = false;
      setTimeout(function() {
        notRefreshed = true;
      }, 5);
    }
  }, 5);
}
