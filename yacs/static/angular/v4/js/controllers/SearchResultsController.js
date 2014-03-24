'use strict';

(function(angular, app, undefined){

app.controller('SearchResultsCtrl', ['$q', '$scope', '$routeParams', '$location',
			   'CourseFetcher', 'CourseSearch', 'urlProvider', 'Selection',
			   function($q, $scope, $routeParams, $location, CourseFetcher, CourseSearch, urlProvider, Selection){
	$scope.courses = [];
	var query = decodeURIComponent($routeParams.query || '');
	var selectionPromise = Selection.current;
	$q.all([$scope.semester, selectionPromise]).then(function(values){
		var semester = values[0];
		var selection = values[1];

		if (query === '') {
			return;
		}

		CourseFetcher({semester_id: semester.id}).then(function(allCourses){
			var courses = $scope.courses = CourseSearch(allCourses, query);
			console.log(courses);
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

