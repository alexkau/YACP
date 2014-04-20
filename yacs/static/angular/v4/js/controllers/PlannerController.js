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

    var sendReceiveRequest = function(event, ui) {
        $(".alert").alert();
        var item = ui.item.context;
        var course = item.innerText;

        if($(item).parent().attr("id") == "planner-courses") {
            var semester = -1;
            var year = -1;
        } else {
            var semester = $(item).closest("td").index()-1;
            var year = $(item).parent().parent().children(":first")[0].innerText;            
        }

        var creditsThisSemester = 0
        $(item).parent().children().each(function(){
            creditsThisSemester += $(this).data("credits");
        });
        if(creditsThisSemester > 21)
        {
            alert("Warning: This semester has more than 21 credits.");
        }

        // Move course in DB to new location
        var res = $.post( "/planner/move_course", { course: course, semester: semester, year: year });
        // res.done(function( data ) {
        //     console.log(data);
        // });
    };

    var initSorting = function() {
        $('.multiSortable.planner-col').each(function() {
            var currentYear = (new Date).getFullYear();
            var currentMonth = (new Date).getMonth();
            // Exclude all semesters that have ended
            if($(this).data("year") < currentYear) {
                $(this).removeClass("multiSortable");
                $(this).addClass("notSortable");
            }
            if($(this).data("year") == currentYear) {
                // Months are zero-indexed
                if($(this).data("semester") == 0 && currentMonth >= 5) {
                    $(this).removeClass("multiSortable");
                    $(this).addClass("notSortable");
                } else if($(this).data("semester") == 1 && currentMonth >= 7) {
                    $(this).removeClass("multiSortable");
                    $(this).addClass("notSortable");
                }
            }
        });
        // Init sortables
        $('.multiSortable').sortable({
            items: '> div:not(.immovable)',
            connectWith: '.multiSortable',
            receive: sendReceiveRequest,
        });
    };

    // Don't look. Nothing here to see. Move along.
    window.setTimeout(initSorting, 1000);
    
    $scope.showCAPPUploadForm = function()
    {
        window.open ('/planner/upload_capp','_self',false);
    }
}]);

})(angular, app);