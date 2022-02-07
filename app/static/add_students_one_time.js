$(document).ready(function() {

 $('input[name="search_by_tutor_or_student"]').change(function() {
         document.getElementById("tutor_or_student_list").innerHTML = "";
         document.getElementById("tutor_or_student_list").value = "";
        if ($(this).val() == "search_by_tutor") {
            var tutor_or_student_list = $("#tutor_or_student_data_list");
            var select_options = "";
            var tutors_info = $("#tutors_info").attr("data-tutors_info");
            var tutors_info = JSON.parse(tutors_info);
            select_options +=  '<option value="" selected disabled hidden>Choose tutor</option>';
             for (var key in tutors_info){
                    console.log(tutors_info[key] );
                    select_options += '<option value="'+key+'">'+tutors_info[key]+'</option>';
                }
                 document.getElementById("label_for_tutor_or_student_list").innerHTML = 'Select Tutor';
                 document.getElementById("error_for_tutor_or_student_list").innerHTML = 'Valid tutor is required.';
                tutor_or_student_list.append(select_options);
        } else {
           var tutor_or_student_list = $("#tutor_or_student_data_list");
            var select_options = "";
            var students_info = $("#students_info").attr("data-students_info");
            var students_info = JSON.parse(students_info);
             select_options +=  '<option value="" selected disabled hidden>Choose student</option>';
             for (var key in students_info){
                    console.log(students_info[key] );
                    select_options += '<option value="'+key+'">'+students_info[key]+'</option>';
                }
                document.getElementById("label_for_tutor_or_student_list").innerHTML = 'Select Student';
                 document.getElementById("error_for_tutor_or_student_list").innerHTML = 'Valid student is required.';
                tutor_or_student_list.append(select_options);
        }
    });


    $('input[id="add"]').click(function() {
    var search_by_tutor_or_student = $( 'input[name=search_by_tutor_or_student]:checked' ).val();

    if (search_by_tutor_or_student == "search_by_tutor") {
    var selected_tutor_or_student = $("#tutor_or_student_list").val();
    var tutors_to_add = $("#tutors_to_add").val();
    $("#tutors_to_add").val(tutors_to_add+"\n"+selected_tutor_or_student);
    }
    else
    {
    var selected_tutor_or_student = $("#tutor_or_student_list").val();
    var students_to_add = $("#students_to_add").val();
    $("#students_to_add").val(students_to_add+"\n"+selected_tutor_or_student);
    }

    });

});