// dsstores.js

$(document).ready(function() {
    // Filter stores
    $('#store-filter').on('input', function() {
        var filter = $(this).val().toLowerCase();
        $('.content-list .item').each(function() {
            var storeName = $(this).text().toLowerCase();
            $(this).toggle(storeName.includes(filter));
        });
    });

    // Add New Store button click event
    $('#add-store-btn').click(function() {
        var newStore = prompt("Enter the new store name:");
        if (newStore) {
            // Call the server to add the new store
            $.post('/stores/add', { store: newStore }, function(response) {
                if (response.success) {
                    location.reload(); // Reload the page to see the new store
                } else {
                    alert("Failed to add store.");
                }
            });
        }
    });

    // Edit and Delete button click events
    $('.edit-btn').click(function() {
        var storeName = $(this).data('store');
        var newStoreName = prompt("Edit store name:", storeName);
        if (newStoreName) {
            // Call the server to update the store name
            $.post('/stores/edit', { oldStore: storeName, newStore: newStoreName }, function(response) {
                if (response.success) {
                    location.reload(); // Reload the page to see the updated store
                } else {
                    alert("Failed to edit store.");
                }
            });
        }
    });

    $('.delete-btn').click(function() {
        var storeName = $(this).data('store');
        if (confirm("Are you sure you want to delete this store?")) {
            // Call the server to delete the store
            $.post('/stores/delete', { store: storeName }, function(response) {
                if (response.success) {
                    location.reload(); // Reload the page to remove the deleted store
                } else {
                    alert("Failed to delete store.");
                }
            });
        }
    });
});
