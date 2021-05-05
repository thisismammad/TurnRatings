
function active_loader() {
  $(".main-loader").css('display', 'flex')
}
function disable_loader() {
  $(".main-loader").css('display', 'none')
}





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
        data: {"sp_id": sp_id, "medical_id": medical_id},
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

$("#alert").fadeTo(5000, 4000).slideUp(500, function () {
    $("#alert").slideUp(500);
});


$("#select_city_report").change(function () {
    let city_id = $(this).val();
    $.ajax({
        url: '/load-data-for-report',
        data: {"city_id": city_id},
        type: 'POST',
        success: function (response) {
            console.log("---------------load-medicals--------------");

            $("#select_medical_report").empty()
            $("#select_medical_report").html("<option value=\"0\" selected >مرکز درمانی را انتخاب کنید ...</option>")
            $("#select_doctor_report").empty()
            $("#select_doctor_report").html("<option value=\"0\" selected >پزشک را انتخاب کنید ...</option>")
            $("#select_specialties_report").empty()
            $("#select_specialties_report").html("<option value=\"0\" selected >تخصص را انتخاب کنید ...</option>")

            if (city_id !== "0") {
                let sps = []
                for (const m in response["medicals"]) {
                    if (response["medicals"][m]["medical_city"] === parseInt(city_id)) {
                        let option = $("<option></option>")
                        $(option).text(response["medicals"][m]["medical_name"]);
                        $(option).val(response["medicals"][m]["medical_id"]);
                        $("#select_medical_report").append(option);
                        for (const d in response["doctors"]) {
                            if (response["doctors"][d]["doctor_medical"] === response["medicals"][m]["medical_id"]) {
                                let option = $("<option></option>")
                                $(option).text(response["doctors"][d]["doctor_name"] + '-' + response["doctors"][d]["doctor_last_name"]);
                                $(option).val(response["doctors"][d]["doctor_id"]);
                                $("#select_doctor_report").append(option);
                                if (sps.includes(response["doctors"][d]["doctor_sp"])) {

                                } else {
                                    sps.push(response["doctors"][d]["doctor_sp"])
                                }
                            }
                        }

                    }
                }
                for (const s in response["specialties"]) {
                    if (sps.includes(response["specialties"][s]["sp_id"])) {
                        let option = $("<option ></option>")
                        $(option).text(response["specialties"][s]["sp_name"]);
                        $(option).val(response["specialties"][s]["sp_id"]);
                        $("#select_specialties_report").append(option);
                    }
                }
            } else {
                for (const d in response["doctors"]) {
                    let option = $("<option></option>")
                    $(option).text(response["doctors"][d]["doctor_name"] + '-' + response["doctors"][d]["doctor_last_name"]);
                    $(option).val(response["doctors"][d]["doctor_id"]);
                    $("#select_doctor_report").append(option);
                }
                for (const m in response["medicals"]) {
                    let option = $("<option ></option>")
                    $(option).text(response["medicals"][m]["medical_name"]);
                    $(option).val(response["medicals"][m]["medical_id"]);
                    $("#select_medical_report").append(option);
                }
                for (const s in response["specialties"]) {
                    let option = $("<option></option>")
                    $(option).text(response["specialties"][s]["sp_name"]);
                    $(option).val(response["specialties"][s]["sp_id"]);
                    $("#select_specialties_report").append(option);

                }
            }

        },
        error: function (error) {
            console.log("---------------error--------------");

        }
    });
});

$("#select_medical_report").change(function () {
    let medical_id = $(this).val();
    $.ajax({
        url: '/load-data-for-report',
        data: {"medical_id": medical_id},
        type: 'POST',
        success: function (response) {
            console.log("---------------load-specialties--------------");
            $("#select_doctor_report").empty()
            $("#select_doctor_report").html("<option value=\"0\" selected >پزشک را انتخاب کنید ...</option>")
            $("#select_specialties_report").empty()
            $("#select_specialties_report").html("<option value=\"0\" selected >تخصص را انتخاب کنید ...</option>")
            $("#select_city_report").empty()
            $("#select_city_report").html("<option value=\"0\" selected >شهر را انتخاب کنید ...</option>")
            let medical_city = 0
            let sps = []
            for (const m in response["medicals"]) {
                console.log(response["medicals"][m]["medical_id"])
                if (response["medicals"][m]["medical_id"] === parseInt(medical_id)) {
                    medical_city = response["medicals"][m]["medical_city"]
                }
            }
            if (medical_id !== "0") {
                for (const d in response["doctors"]) {
                    if (response["doctors"][d]["doctor_medical"] === parseInt(medical_id)) {
                        let option = $("<option></option>")
                        $(option).text(response["doctors"][d]["doctor_name"] + '-' + response["doctors"][d]["doctor_last_name"]);
                        $(option).val(response["doctors"][d]["doctor_id"]);
                        $("#select_doctor_report").append(option);
                        if (sps.includes(response["doctors"][d]["doctor_sp"])) {

                        } else {
                            sps.push(response["doctors"][d]["doctor_sp"])
                        }
                    }
                }
                for (const c in response["cities"]) {
                    if (response["cities"][c]["city_id"] === medical_city) {
                        let option = $("<option selected></option>")
                        $(option).text(response["cities"][c]["city_name"]);
                        $(option).val(response["cities"][c]["city_id"]);
                        $("#select_city_report").append(option);
                    } else {
                        let option = $("<option ></option>")
                        $(option).text(response["cities"][c]["city_name"]);
                        $(option).val(response["cities"][c]["city_id"]);
                        $("#select_city_report").append(option);
                    }
                }
                for (const s in response["specialties"]) {
                    if (sps.includes(response["specialties"][s]["sp_id"])) {
                        let option = $("<option ></option>")
                        $(option).text(response["specialties"][s]["sp_name"]);
                        $(option).val(response["specialties"][s]["sp_id"]);
                        $("#select_specialties_report").append(option);
                    }
                }
            } else {
                for (const d in response["doctors"]) {
                    let option = $("<option></option>")
                    $(option).text(response["doctors"][d]["doctor_name"] + '-' + response["doctors"][d]["doctor_last_name"]);
                    $(option).val(response["doctors"][d]["doctor_id"]);
                    $("#select_doctor_report").append(option);
                }
                for (const c in response["cities"]) {
                    let option = $("<option ></option>")
                    $(option).text(response["cities"][c]["city_name"]);
                    $(option).val(response["cities"][c]["city_id"]);
                    $("#select_city_report").append(option);
                }
                for (const s in response["specialties"]) {
                    let option = $("<option></option>")
                    $(option).text(response["specialties"][s]["sp_name"]);
                    $(option).val(response["specialties"][s]["sp_id"]);
                    $("#select_specialties_report").append(option);

                }
            }

        },
        error: function (error) {
            console.log("---------------error--------------");

        }
    });
})
;

$("#select_specialties_report").change(function () {
    let sp_id = $(this).val();
    $.ajax({
        url: '/load-data-for-report',
        data: {"sp_id": sp_id},
        type: 'POST',
        success: function (response) {
            console.log("--------------- load-doctors --------------");


            if (sp_id !== "0") {
                $("#select_doctor_report").empty()
                $("#select_doctor_report").html("<option value=\"0\" selected >پزشک را انتخاب کنید ...</option>")
                for (const d in response["doctors"]) {
                    if (response["doctors"][d]["doctor_sp"] === parseInt(sp_id)) {
                        let option = $("<option></option>")
                        $(option).text(response["doctors"][d]["doctor_name"] + '-' + response["doctors"][d]["doctor_last_name"]);
                        $(option).val(response["doctors"][d]["doctor_id"]);
                        $("#select_doctor_report").append(option);
                    }
                }
            } else {
                $("#select_doctor_report").empty()
                $("#select_doctor_report").html("<option value=\"0\" selected >پزشک را انتخاب کنید ...</option>")
                for (const m in response["medicals"]) {
                    let option = $("<option></option>")
                    $(option).text(response["medicals"][m]["medical_name"]);
                    $(option).val(response["medicals"][m]["medical_id"]);
                    $("#select_medical_report").append(option);
                }
                for (const c in response["cities"]) {
                    let option = $("<option ></option>")
                    $(option).text(response["cities"][c]["city_name"]);
                    $(option).val(response["cities"][c]["city_id"]);
                    $("#select_city_report").append(option);
                }
                for (const d in response["doctors"]) {
                    let option = $("<option></option>")
                    $(option).text(response["doctors"][d]["doctor_name"] + '-' + response["doctors"][d]["doctor_last_name"]);
                    $(option).val(response["doctors"][d]["doctor_id"]);
                    $("#select_doctor_report").append(option);
                }
            }

        },
        error: function (error) {
            console.log("---------------error--------------");
        }
    });
});


$("#select_doctor_report").change(function () {
    let doctor_id = $(this).val();
    console.log(doctor_id)
    $.ajax({
        url: '/load-data-for-report',
        data: {"doctor_id": doctor_id},
        type: 'POST',
        success: function (response) {
            console.log("--------------- load-doctors --------------");
            $("#select_specialties_report").empty()
            $("#select_specialties_report").html("<option value=\"0\" selected >تخصص را انتخاب کنید ...</option>")
            $("#select_medical_report").empty()
            $("#select_medical_report").html("<option value=\"0\" selected >مرکز درمانی را انتخاب کنید ...</option>")
            $("#select_city_report").empty()
            $("#select_city_report").html("<option value=\"0\" selected >شهر را انتخاب کنید ...</option>")
            let doctor_medical = 0
            let doctor_sp = 0
            for (const d in response["doctors"]) {
                if (response["doctors"][d]["doctor_id"] === parseInt(doctor_id)) {
                    doctor_medical = response["doctors"][d]["doctor_medical"]
                    doctor_sp = response["doctors"][d]["doctor_sp"]
                }
            }
            if (doctor_medical !== 0) {
                for (const m in response["medicals"]) {
                    if (response["medicals"][m]["medical_id"] === doctor_medical) {
                        let option = $("<option selected></option>")
                        $(option).text(response["medicals"][m]["medical_name"]);
                        $(option).val(response["medicals"][m]["medical_id"]);
                        $("#select_medical_report").append(option);

                        for (const c in response["cities"]) {
                            if (response["cities"][c]["city_id"] === response["medicals"][m]["medical_city"]) {
                                let option = $("<option selected></option>")
                                $(option).text(response["cities"][c]["city_name"]);
                                $(option).val(response["cities"][c]["city_id"]);
                                $("#select_city_report").append(option);
                            } else {
                                let option = $("<option ></option>")
                                $(option).text(response["cities"][c]["city_name"]);
                                $(option).val(response["cities"][c]["city_id"]);
                                $("#select_city_report").append(option);
                            }
                        }
                    } else {
                        let option = $("<option></option>")
                        $(option).text(response["medicals"][m]["medical_name"]);
                        $(option).val(response["medicals"][m]["medical_id"]);
                        $("#select_medical_report").append(option);
                    }
                }
                for (const s in response["specialties"]) {
                    if (response["specialties"][s]["sp_id"] === doctor_sp) {
                        let option = $("<option selected></option>")
                        $(option).text(response["specialties"][s]["sp_name"]);
                        $(option).val(response["specialties"][s]["sp_id"]);
                        $("#select_specialties_report").append(option);
                    } else {
                        let option = $("<option></option>")
                        $(option).text(response["specialties"][s]["sp_name"]);
                        $(option).val(response["specialties"][s]["sp_id"]);
                        $("#select_specialties_report").append(option);
                    }
                }
            } else {
                for (const m in response["medicals"]) {
                    let option = $("<option></option>")
                    $(option).text(response["medicals"][m]["medical_name"]);
                    $(option).val(response["medicals"][m]["medical_id"]);
                    $("#select_medical_report").append(option);
                }
                for (const c in response["cities"]) {
                    let option = $("<option ></option>")
                    $(option).text(response["cities"][c]["city_name"]);
                    $(option).val(response["cities"][c]["city_id"]);
                    $("#select_city_report").append(option);
                }
                for (const s in response["specialties"]) {
                    let option = $("<option></option>")
                    $(option).text(response["specialties"][s]["sp_name"]);
                    $(option).val(response["specialties"][s]["sp_id"]);
                    $("#select_specialties_report").append(option);

                }
            }
        },
        error:
            function (error) {
                console.log("---------------error--------------");
            }
    });
});


$("#select_position").change(function () {
    let positions = $(this).val();
    $.ajax({
        url: '/load-medicals-admin',
        data: {"medical_id": positions},
        type: 'POST',
        success: function (response) {
            console.log("---------------load-medicals--------------");
            $("#medicals").empty()
            $("#medicals").html("<option value=\"0\" selected hidden >مرکز درمانی را انتخاب کنید ...</option>")
            if (positions == 0 || positions == 1) {
                $("#medicals").empty()
                $("#medicals").html("<option value=\"0\" selected hidden >مرکز درمانی را انتخاب کنید ...</option>")
            } else {
                for (const m in response["medicals"]) {
                    let option = $("<option></option>")
                    $(option).text(response["medicals"][m]["medical_name"]);
                    console.log(response["medicals"][m]["medical_name"]);
                    $(option).val(response["medicals"][m]["medical_id"]);
                    $("#medicals").append(option);
                }
            }
        },
        error: function (error) {
            console.log("---------------error--------------");
        }
    });
});


$(".select_position_edit").change(function () {
    let positions = $(this).val();
    $.ajax({
        url: '/load-medicals-admin',
        data: {"medical_id": positions},
        type: 'POST',
        success: function (response) {
            console.log("---------------load-medicals--------------");
            $(".medicals_edit").empty()
            $(".medicals_edit").html("<option value=\"0\" selected hidden >مرکز درمانی را انتخاب کنید ...</option>")
            console.log("---------------ed po 1--------------");
            console.log(positions);
            if (positions == 0 || positions == 1) {
                $(".medicals_edit").empty()
                $(".medicals_edit").html("<option value=\"0\" selected hidden >مرکز درمانی را انتخاب کنید ...</option>")
                console.log("---------------ed po 2--------------");
            } else {
                console.log("---------------ed po 3--------------");

                for (const m in response["medicals"]) {
                    let option = $("<option></option>")
                    $(option).text(response["medicals"][m]["medical_name"]);
                    $(option).val(response["medicals"][m]["medical_id"]);
                    $(".medicals_edit").append(option);
                }
            }
        },
        error: function (error) {
            console.log("---------------error--------------");
        }
    });
});

$(".reveal").on('click', function () {
    var $pwd = $(".pwd");
    if ($pwd.attr('type') === 'password') {
        $pwd.attr('type', 'text');
        console.log("+++++++++++++++++++++++++=")
    } else {
        $pwd.attr('type', 'password');
        console.log("_____________________")
    }
});

$('#modal-add-item').on('hidden.bs.modal', function (e) {
    $(this)
        .find("input,textarea,select")
        .val('')
        .end()
        .find("input[type=checkbox], input[type=radio]")
        .prop("checked", "")
        .end();
})

$(document).ready(function () {
    $('#data-table').DataTable({
        language: {
            "sEmptyTable": "هیچ داده‌ای در جدول وجود ندارد",
            "sInfo": "نمایش _START_ تا _END_ از _TOTAL_ ردیف",
            "sInfoEmpty": "نمایش 0 تا 0 از 0 ردیف",
            "sInfoFiltered": "(فیلتر شده از _MAX_ ردیف)",
            "sInfoThousands": ",",
            "sLengthMenu": "نمایش _MENU_ ردیف",
            "sLoadingRecords": "در حال بارگزاری...",
            "sProcessing": "در حال پردازش...",
            "sSearch": "",
            "searchPlaceholder": "جستجو...",
            "sZeroRecords": "رکوردی با این مشخصات پیدا نشد",
            "oPaginate": {
                "sFirst": "برگه‌ی نخست",
                "sLast": "برگه‌ی آخر",
                "sNext": "بعدی",
                "sPrevious": "قبلی"
            },
            "oAria": {
                "sSortAscending": ": فعال سازی نمایش به صورت صعودی",
                "sSortDescending": ": فعال سازی نمایش به صورت نزولی"
            }
        },
        "paging": false,
        "order": [],
        "lengthChange": false,
        "info": false,
    });
});


$("#get_report").click(function () {
    // let positions = $(this).val();
    active_loader()
    $("#row_data").empty()
    $.ajax({
        url: '/reporting',
        // data: {"medical_id": positions},
        data: $('#report_form').serialize(),
        type: 'POST',
        success: function (response) {
            console.log("---------------success--------------");
            for (const index in response["data"]) {
                var today = new Date(response["data"][index]["date"]);
                var dd = today.getDate();

                var mm = today.getMonth() + 1;
                var yyyy = today.getFullYear();
                if (dd < 10) {
                    dd = '0' + dd;
                }

                if (mm < 10) {
                    mm = '0' + mm;
                }
                today = mm + '-' + dd + '-' + yyyy;
                console.log(today);
                var record = ` <tr>
                                <th scope="row">${parseInt(index) + 1}</th>
                                <td>${response["data"][index]["sick_NC"]}</td>
                                <td>${response["data"][index]["sick_name"]}</td>
                                <td>${response["data"][index]["doctor"]}</td>
                                <td>${response["data"][index]["medical"]}</td>
                                <td>${today}</td>
                                <td>${response["data"][index]["status"]}</td>
                            </tr>`
                $("#row_data").append(record)
            }
            disable_loader();
        },
        error: function (error) {
            console.log("---------------error--------------");
            disable_loader();
        }
    });
});




