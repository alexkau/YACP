'use strict';

(function(angular, app, undefined){

app.controller('CatalogCtrl', ['$q', '$scope', '$location', '$routeParams',
			   '$timeout', 'CourseFetcher', 'Selection', 'currentSemesterPromise',
			   function($q, $scope, $location, $routeParams, $timeout, CourseFetcher, Selection, currentSemesterPromise){
	$scope.courses = [];
	$scope.emptyText = "Loading courses...";
	var selectionPromise = Selection.current;
	currentSemesterPromise.then(function(semester){
		var coursePromise = CourseFetcher({semester_id: semester.id, department_code: $routeParams.dept});
		$q.all([selectionPromise, coursePromise]).then(function(values){
			var selection = values[0];
			var courses = values[1];
			$scope.courses = courses;
			selection.apply($scope.courses);

			$scope.clickCourse = function(course){
				selection.updateCourse(course).then(function(){
					selection.save();
					selection.apply($scope.courses);
				}, function(){
					selection.apply($scope.courses);
				});
			};

			$scope.clickSection = function(course, section){
				selection.updateSection(course, section).then(function(){
					selection.save();
					selection.apply($scope.courses);
				}, function(){
					selection.apply($scope.courses);
				});
			};
			$scope.remove_just_added = function(course){course.just_added = false};
			$scope.addCourseToPlanner = function(course){
				console.log(course);
				$.post("/planner/add_course",{course:course.department.code+" "+course.number});
				course.in_planner = true;
				course.just_added = true;
				$timeout(function(){$scope.remove_just_added(course)},1000);
			};
			angular.forEach($scope.courses,function(course,i){
				console.log(course);
				$.post("/planner/is_in_planner",{course:course.department.code+" "+course.number},function(data){
					$scope.courses[i].in_planner = (data == "True"); 
				});
			});
			$scope.openRateMyProfessors = function(instructorsText){
				var instructors = instructorsText.split(/, |\//);
				var i = 0;
				while (i < instructors.length) {
					$.ajax({
						type: "GET",
						url: "/api/4/retrieve_rate_my_professors_url/",
						data: {
							instructor: instructors[i]
						},
						dataType: "json",
						success: function(url) {
							window.open(url["result"]["url"]);
						}
					});
 					i++;
				}
			};
		});
	});
}]);

})(angular, app);

