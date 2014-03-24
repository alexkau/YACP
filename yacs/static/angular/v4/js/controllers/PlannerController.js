'use strict';

(function(angular, app, undefined){

app.controller('PlannerCtrl', ['$scope', '$location','$http','urlProvider','searchOptions','Utils',
               function($scope, $location,$http, urlProvider,searchOptions,Utils){
    searchOptions.visible = false;
    $scope.logged_in = true;
    $http.get("/api/4/planner/courses").then(function(response){
        if(response.data.result == "Not logged in")
        {
            $scope.logged_in = false;
            return;
        }
        $scope.courses = response.data.result;
    });
    $scope.somevalue = true;
    $scope.showHeading = function() {
        $scope.somevalue =  !$scope.somevalue;
    }
    $scope.years = [1,2,3,4];
}]);

})(angular, app);