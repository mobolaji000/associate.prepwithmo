$(document).ready(function() {

 window.onload = function(){
 var offset = -6; //adjust to cst
var today = new Date(new Date().getTime() + offset * 3600 * 1000).toISOString().split('T')[0];
        document.getElementById("start_date").value = today;
        document.getElementById("end_date").value = today;

        var is_admin = $("#is_admin");
            var is_admin = $("#is_admin").attr("data-is_admin");
            //alert(is_admin);
            if (is_admin == "False")
            {
              var tutor_or_student_list = $("#tutor_or_student_list");
            var select_options = "";
            var students_info = $("#students_info").attr("data-students_info");
            var students_info = JSON.parse(students_info);
             select_options +=  '<option value="" selected disabled hidden>Choose student</option>';
             for (var key in students_info){
                    console.log( key, students_info[key] );
                    select_options += '<option value="'+key+'">'+students_info[key]+'</option>';
                }
                document.getElementById("label_for_tutor_or_student_list").innerHTML = 'Select Student';
                 document.getElementById("error_for_tutor_or_student_list").innerHTML = 'Valid student is required.';
                tutor_or_student_list.append(select_options);

            }

        };

 $('input[name="search_by_tutor_or_student"]').change(function() {
        if ($(this).val() == "search_by_tutor") {
            var tutor_or_student_list = $("#tutor_or_student_list");
            var select_options = "";
            var tutors_info = $("#tutors_info").attr("data-tutors_info");
            var tutors_info = JSON.parse(tutors_info);
            select_options +=  '<option value="" selected disabled hidden>Choose tutor</option>';
             for (var key in tutors_info){
                    console.log( key, tutors_info[key] );
                    select_options += '<option value="'+key+'">'+tutors_info[key]+'</option>';
                }
                 document.getElementById("label_for_tutor_or_student_list").innerHTML = 'Select Tutor';
                 document.getElementById("error_for_tutor_or_student_list").innerHTML = 'Valid tutor is required.';
                tutor_or_student_list.append(select_options);
        } else {
           var tutor_or_student_list = $("#tutor_or_student_list");
            var select_options = "";
            var students_info = $("#students_info").attr("data-students_info");
            var students_info = JSON.parse(students_info);
             select_options +=  '<option value="" selected disabled hidden>Choose student</option>';
             for (var key in students_info){
                    console.log( key, students_info[key] );
                    select_options += '<option value="'+key+'">'+students_info[key]+'</option>';
                }
                document.getElementById("label_for_tutor_or_student_list").innerHTML = 'Select Student';
                 document.getElementById("error_for_tutor_or_student_list").innerHTML = 'Valid student is required.';
                tutor_or_student_list.append(select_options);
        }
    });
});