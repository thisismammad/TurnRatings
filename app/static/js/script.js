$("#select_city").change(function () {
    let value = $(this).val();
    $.ajax({
			url: '/load-medicals',
			data: {"city_id":value},
			type: 'POST',
			success: function(response){
				console.log("---------------this  work--------------");
				console.log(response)
			},
			error: function(error){
				console.log("---------------error--------------");
				console.log(error)
			}
		});
});