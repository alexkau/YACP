(function($, window, document, undefined){

var selection = {}; // course_id => crns

var updateFuse = new Utils.Fuse({
    delay: 250,
    execute: function(){
        console.log('saving selection');
        var parameters = {};
        $.each(selection, function(value, name){
            var key = 'course_' + name;
            parameters[key] = "checked";
        });
        /*
        $.ajax(url, {
            method: "POST",
            parameters: 'csrf_token=' + Utils.csrf_token() + '&' + $.param(parameters),
            complete: function(){
            }
        });
        */
    }
});

// lower level operations to modify the selection, should automatically
// handle syncing with the server
function addSectionToSelection(courseID, crn){
    updateFuse.stop();
    if(!selection[courseID])
        selection[courseID] = [];
    if(!$.inArray(crn, selection[courseID]))
        selection[courseID].push(crn);
    updateFuse.start();
}

function removeSectionFromSelection(courseID, crn){
    if(!selection[courseID])
        return;
    updateFuse.stop();
    selection[courseID].remove(crn);
    if(selection[courseID].length === 0)
        delete selection[courseID];
    updateFuse.start();
}
// end selection handling

// event handling for #selected
function sectionChanged(){
    // update selection via ajax ???
    var crn = $(this).find('.crn').text(), courseID = $(this).attr('data-cid');

    if (this.checked){
        addSectionToSelection(courseID, crn);
        return;
    }

    removeSectionFromSelection(courseID, crn);
}

function courseChanged(evt){
    var $sections = $(this).parent().find('.section input[type=checkbox]');
    if (this.checked)
        $sections.attr('checked', 'checked');
    else
        $sections.removeAttr('checked');

    $sections.each(function(){
        sectionChanged.call(this, [evt]);
    });
}

// handles adding & removing selections by (un)checking the courses in #courses.
function addToSelected($course){
    console.log('add', $course.attr('data-cid'));
    var courseID = $course.attr('data-cid'),
        crns = Utils.splitNonEmpty($course.attr('data-crns')),
        fullCrns = Utils.splitNonEmpty($course.attr('data-crns-full')),
        availableCrns = Utils.setDifference(crns, fullCrns);
    $.each(availableCrns, function(){
        addSectionToSelection(courseID, this);
    });
}

function removeFromSelected($course){
    console.log('remove', $course.attr('data-cid'));
    var courseID = $course.attr('data-cid'),
        crns = Utils.splitNonEmpty($course.attr('data-crns'));
    $.each(crns, function(){
        removeSectionFromSelection(courseID, this);
    });
}
// end selection GUI modifiers

// event handling for #courses
function courseSelected(evt){
    var el = evt.target, $el = $(el);
    if (!$el.is('input[type=checkbox]'))
        return;

    if (!el.checked){
        removeFromSelected($el);
        // remove from selected
        return;
    }
    // add to selected
    addToSelected($el);
}

// initialization
$(function(){
    $('#selected .course > input[type=checkbox]').live('change', courseChanged);
    $('#selected .section input[type=checkbox]').live('change', sectionChanged);
    $('.save-selected').hide(); // selected courses save button

    // hide add to selection button... autoadd on check
    $('#courses').live('change', courseSelected);
    $('#courses input[type=submit]').hide();
});

})(jQuery, window, document);