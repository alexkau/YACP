'use strict';

(function(angular, app, undefined){

app.controller('SearchCtrl', function($scope, $location, $timeout, $route, urlProvider){
	var timeout = null;
	var previousPath = null;
	$scope.semester.then(function(semester){
		$scope.query = decodeURIComponent($route.current.params.query || '');
		$scope.$watch('query', function(){
			if (timeout){
				$timeout.cancel(timeout);
				timeout = null;
			}
			timeout = $timeout(function(){
				if ($scope.query && $scope.query !== ''){
					// restore previous url
					if (!$route.current.params.query){
						previousPath = $location.path();
					}
					$location.path(urlProvider(
						semester.year,
						semester.month,
						'search',
						$scope.query
					));
					timeout = null;
				} else if (previousPath){
					$location.path(previousPath);
				}
			}, 250);
		});
	});
});

})(angular, app);

