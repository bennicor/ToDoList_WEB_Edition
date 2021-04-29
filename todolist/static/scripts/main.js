// Изменение формата даты, отображаемго в календаре
$(".calendar").on("change", function() {
    this.setAttribute(
        "data-date",
        moment(this.value, "YYYY-MM-DD")
        .format(this.getAttribute("data-date-format"))
    )
}).trigger("change")

$(document).ready(function() {
    $("#myModal").modal('show');
});

$(function() {
    window.setTimeout(function() {
        $('#my-alert').alert('close');
    }, 5000);
});