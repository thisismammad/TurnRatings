$("#select_city").change(function () {
    let value = $(this).val();
    $.ajax({
        url: '/load-medicals',
        data: {"city_id": value},
        type: 'POST',
        success: function (response) {
            console.log("---------------load-medicals--------------");
            $("#select_medical").empty()
            $("#select_medical").html("<option value=\"0\" selected  hidden>مرکز درمانی را انتخاب کنید ...</option>")

            for (const medical in response["medicals"]) {
                let option = $("<option></option>")
                $(option).text(response["medicals"][medical]["medical_name"]);
                $(option).val(response["medicals"][medical]["medical_id"]);

                $("#select_medical").append(option);

            }
        },
        error: function (error) {
            console.log("---------------error--------------");

        }
    });
});

$("#select_medical").change(function () {
    let value = $(this).val();
    $.ajax({
        url: '/load-specialties',
        data: {"medical_id": value},
        type: 'POST',
        success: function (response) {
            console.log("---------------load-specialties--------------");
            $("#select_specialties").empty()
            $("#select_specialties").html("<option value=\"0\" selected  hidden>تخصص را انتخاب کنید ...</option>")
            for (const sp in response["specialties"]) {
                let option = $("<option></option>")
                $(option).text(response["specialties"][sp]["sp_name"]);
                $(option).val(response["specialties"][sp]["sp_id"]);

                $("#select_specialties").append(option);

            }
        },
        error: function (error) {
            console.log("---------------error--------------");

        }
    });
});

$("#select_specialties").change(function () {
    let sp_id = $(this).val();
    let medical_id = $("#select_medical").val();
    $.ajax({
        url: '/load-doctors',
        data: {"sp_id": sp_id , "medical_id":medical_id},
        type: 'POST',
        success: function (response) {
            console.log("--------------- load-doctors --------------");
            $("#select_doctor").empty()
            $("#select_doctor").html("<option value=\"0\" selected  hidden>پزشک را انتخاب کنید ...</option>")
            for (const doctor in response["doctors"]) {
                let option = $("<option></option>")
                $(option).text(response["doctors"][doctor]["doctor_name"]);
                $(option).val(response["doctors"][doctor]["doctor_id"]);

                $("#select_doctor").append(option);

            }
        },
        error: function (error) {
            console.log("---------------error--------------");

        }
    });
});

$("#alert").fadeTo(5000, 4000).slideUp(500, function(){
    $("#alert").slideUp(500);
});