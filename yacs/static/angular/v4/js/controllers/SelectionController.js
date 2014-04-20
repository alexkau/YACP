'use strict';

(function(angular, app, undefined){

app.controller('SelectionCtrl', ['$window', '$scope', '$q', '$location', 'Selection',
			   'currentSemesterPromise', 'CourseFetcher', 'schedulePresenter',
			   'SectionTime', 'searchOptions', 'ICAL_URL','$timeout',
			   function($window, $scope, $q, $location, Selection,
						currentSemesterPromise, CourseFetcher, schedulePresenter,
						SectionTime, searchOptions, ICAL_URL,$timeout){
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
				angular.forEach($scope.courses,function(course,i){
					console.log(course);
					$.post("/planner/is_in_planner",{course:course.department.code+" "+course.number},function(data){
						$scope.courses[i].in_planner = (data == "True"); 
					});
				});

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

		function addClassTime(class_times, class_time){
			var start = class_time[0][0] * (24 * 6) + (6) * class_time[0][1] + (class_time[0][2] / 10);
			var end = class_time[1][0] * (24 * 6)+ (6) * class_time[1][1] + (class_time[1][2] / 10);
			for (var i = 0; i < class_times.length; i++){
				if(class_times[i][0] == start || class_times[i][1] == end)
					return;
			}
			class_times.push(new Array(start, end));
		}

		function getAllClassTimes(schedules){
			var all_class_times = new Array();
			for (var i = 0; i < schedules.length; i++) {
				var schedule = schedules[i];
				var crns = schedule.crns;
				var class_times = new Array();
				for (var j=0; j<schedule.dows.length; j++) {
					var blocks = schedule.blocks[schedule.dows[j]];
					if (blocks){
						for (var k=0; k<blocks.length; k++){
							var sections = blocks[k].course.sections;
							for (var l=0; l<sections.length; l++){
								var section_times= sections[l].section_times;
								if (crns.indexOf(sections[l].crn) != -1){ 
									for (var m=0; m<section_times.length; m++){
										if (section_times[m].days_of_the_week.indexOf(schedule.dows[j]) != -1){ 
											var start_time= new Array(j, parseInt(section_times[m].start.split(":")[0]), parseInt(section_times[m].start.split(":")[1]));
											var end_time= new Array(j, parseInt(section_times[m].end.split(":")[0]), parseInt(section_times[m].end.split(":")[1]));
											addClassTime(class_times, new Array(start_time, end_time));
										}
									}
								}
							}	
						}			
					}
				}
				all_class_times.push(class_times);
			}
			return all_class_times;
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

		$scope.shortOrLongPeriods = function(schedules, short_or_long){
			$scope.scheduleIndex = 0;
			var all_class_times = getAllClassTimes(schedules);
			$.ajax({
				type: "GET",
				url: "/semesters/schedules/getShortOrLongPeriods/",
				data: {
					schedules : JSON.stringify(all_class_times),
					short_or_long : short_or_long
				},
				dataType: "json",
				success: function(result) {
					var updated_schedules=new Array();
					for (var i = 0; i < result.length; i++)
						updated_schedules.push(schedules[result[i]]);
					$scope.schedules= updated_schedules;
					updateUI(updated_schedules);
				}
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
