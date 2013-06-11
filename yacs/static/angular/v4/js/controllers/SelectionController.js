'use strict';

(function(angular, app, undefined){

app.controller('SelectionCtrl', function($scope, $q, Selection, currentSemesterPromise, CourseFetcher){
	$scope.courses = [];
	$scope.hideSearchBar = true;
	$q.all([currentSemesterPromise, Selection.current]).then(function(values){
		var semester = values[0];
		var selection = values[1];
		var filters = {
			semester_id: semester.id,
			id: selection.courseIds()
		};
		CourseFetcher(filters).then(function(courses){
			$scope.courses = courses;
			selection.apply(courses);
		});

		$scope.click_course = function(course){
			selection.updateCourse(course).then(function(){
				selection.save();
				selection.apply($scope.courses);
			}, function(err){
				selection.apply($scope.courses);
			});
		};

		$scope.click_section = function(course, section){
			selection.updateSection(course, section).then(function(){
				selection.save();
				selection.apply($scope.courses);
			}, function(err){
				selection.apply($scope.courses);
			});
		};
	});
});

})(angular, app);

