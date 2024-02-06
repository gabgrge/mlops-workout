$(document).ready(function(){
    $(".filter").on("keyup", function() {
        var input = $(this).val().toUpperCase();
        var column = $(this).data("column"); // get the column number
        $(this).closest('.filter-table').find("tbody tr").each(function() {
            var row = $(this);
            var cell = $(row.find("td").get(column)); // get the corresponding cell
            if (cell.text().toUpperCase().indexOf(input) > -1) {
                row.show();
            } else {
                row.hide();
            }
        });
    });
});