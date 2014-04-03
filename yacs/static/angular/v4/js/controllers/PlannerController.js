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
        if(response.data.result == "No CAPP report")
        {
            $scope.has_capp = false;
            return;
        }
        $scope.courses = response.data.result.courses;
        var semester_names = ["Spring","Summer","Fall"];
        var first_semester = response.data.result.first_semester;
        $scope.semester_names = [semester_names[0],semester_names[1],semester_names[2]];
        $scope.semester_ids = [0,1,2];
        var first_year = response.data.result.first_year; 
        $scope.years = [first_year,first_year+1,first_year+2,first_year+3,first_year+4]; // TODO this should not be hardcoded
        $scope.has_capp = true;
    });
    $scope.showCAPPUploadForm = function()
    {
        window.open ('/planner/upload_capp','_self',false);
    }
}]);

})(angular, app);