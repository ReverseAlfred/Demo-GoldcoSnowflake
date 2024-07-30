$(document).ready(function() {
    $('#store-filter').on('input', function() {
        var filter = $(this).val().toLowerCase();
        $('.content-list .item').each(function() {
            var itemText = $(this).text().toLowerCase();
            if (itemText.indexOf(filter) === -1) {
                $(this).hide();
            } else {
                $(this).show();
            }
        });
    });
});
