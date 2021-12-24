$(document).ready(function() {

	  window.onload = function(){

	  var links = "";

	   var first_row = $("#first_row");
var a_link = "<a></a>";

let n = 0;
var date_to_process = new Date();
	  while (n < 13) {
	  var last_month_name = date_to_process.toLocaleString('default', { month: 'long' });
         var last_year_name = date_to_process.getFullYear();
         console.log(last_month_name+"-"+last_year_name);
         console.log(" ");

         var number_of_days_in_last_month = new Date(date_to_process.getFullYear(), date_to_process.getMonth(), 0).getDate();
         date_to_process.setDate(date_to_process.getDate()-number_of_days_in_last_month);
         links += '<a href=/view_hours/'+last_month_name+'/'+last_year_name+'>'+last_month_name+"-"+last_year_name+'</a>&nbsp;&nbsp;&nbsp;'

         n++;
       }

first_row.append(links);

};


});