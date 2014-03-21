'use strict';

(function(angular, app, undefined){

app.controller('SelectionCtrl', ['$window', '$scope', '$q', '$location', 'Selection',
			   'currentSemesterPromise', 'CourseFetcher', 'schedulePresenter',
			   'SectionTime', 'searchOptions', 'ICAL_URL',
			   function($window, $scope, $q, $location, Selection,
						currentSemesterPromise, CourseFetcher, schedulePresenter,
						SectionTime, searchOptions, ICAL_URL){
	$scope.courses = [];
	$scope.emptyText = "You didn't select any courses. They would go here.";
	$scope.scheduleIndex = 0;
	searchOptions.visible = false;

	var selectionPromise;
	var query = $location.search();
	if (query.id && !isNaN(parseInt(query.id, 10))){
		selectionPromise = Selection.loadById(query.id);
	} else {
		// save the selection first
		selectionPromise = Selection.loadCurrentWithId();
	}
	if (query.n && !isNaN(parseInt(query.n, 10))){
		$scope.scheduleIndex = Math.max(parseInt(query.n, 10), 0);
	}

	$q.all([currentSemesterPromise, selectionPromise]).then(function(values){
		var semester = values[0];
		var selection = values[1];
		var filters = {
			semester_id: semester.id,
			id: selection.courseIds()
		};

		function updateUI(schedules){
			$scope.schedule = schedules[$scope.scheduleIndex];
			$location.search({
				id: selection.id,
				n: $scope.scheduleIndex
			}).replace();
			/* iCal link broken
			if ($scope.schedule && $scope.schedule.crns.length){
				$scope.ical_url = ICAL_URL + '?crn=' + $scope.schedule.crns.join('&crn=');
			} else {
				$scope.ical_url = null;
			}
			*/
			return schedules;
		}

		function setScheduleIndex(amt){
			if (!$scope.schedules){
				return;
			}
			var max = $scope.schedules.length - 1;
			$scope.scheduleIndex = Math.min(Math.max(amt, 0), max);
			return updateUI($scope.schedules);
		};

		function refreshAndSave(shouldSave){
			function refresh(){
				selection.apply($scope.courses);
				var schedulesPromise = selection.schedules(_.values(selection.blockedTimes));
				var promise = schedulePresenter(schedulesPromise, _.values(selection.allBlockedTimes()));
				promise.then(function(schedules){
					$scope.schedules = schedules;
					return setScheduleIndex($scope.scheduleIndex);
				});
			}

			if (shouldSave){
				selection.save().then(refresh);
			} else {
				refresh();
			}
		}

		if (selection.numberOfCourses()){
			CourseFetcher(filters).then(function(courses){
				$scope.courses = courses;
				refreshAndSave(false);
			});
		}

		$scope.showClearButton = function(){
			return selection.numberOfCourses();
		};

		$scope.clickCourse = function(course){
			selection.updateCourse(course).then(function(){
				refreshAndSave(true);
			}, function(err){
				refreshAndSave(false);
			});
		};

		$scope.clickSection = function(course, section){
			selection.updateSection(course, section).then(function(){
				refreshAndSave(true);
			}, function(err){
				refreshAndSave(false);
			});
		};

		$scope.clickClearSelection = function(){
			selection.clear();
			refreshAndSave(true);
		};

		$scope.previousSchedule = function(){
			setScheduleIndex($scope.scheduleIndex - 1);
		};

		$scope.nextSchedule = function(){
			setScheduleIndex($scope.scheduleIndex + 1);
		};

		$scope.keyDown = function(event){
			var left = 37, right = 39;
			if (event.keyCode === left){
				$scope.previousSchedule();
			} else if (event.keyCode === right){
				$scope.nextSchedule();
			}
		};

		$scope.isBlocked = function(time, dow){
			return selection.blockedTimes[dow + '_' + time.toObject()];
		};

		$scope.toggleBlockableTime = function(time, dow){
			var key = dow + '_' + time.toObject();
			if ($scope.isBlocked(time, dow)){
				selection.removeBlockedTime(key);
			} else {
				selection.setBlockedTime(key);
			}
			refreshAndSave(true);
		};

		$scope.print = function(){
			$window.print();
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
}]);

})(angular, app);
