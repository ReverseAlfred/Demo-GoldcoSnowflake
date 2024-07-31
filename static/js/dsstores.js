$(document).ready(function() {
    console.log("dsstores.js loaded");

    // Function to load stores based on filter
    function loadStores(filter) {
        $.ajax({
            url: '/dsstores',
            type: 'GET',
            data: { filter: filter },
            success: function(response) {
                $('#content').html(response);
                console.log("Filtered stores loaded");
            },
            error: function(xhr, status, error) {
                console.error("AJAX error:", status, error);
            }
        });
    }

    // Handle filter input
    $('#store-filter').on('input', function() {
        console.log("Filter input detected");
        var filter = $(this).val().toLowerCase();
        console.log("Filter value:", filter);
        loadStores(filter); // Load stores with filter applied
    });

    // Handle add store button click
    $('#add-store-btn').click(function() {
        console.log("Add New Store button clicked");
        var newStore = prompt("Enter the new store name:");
        if (newStore) {
            $.post('/stores/add', { store: newStore }, function(response) {
                if (response.success) {
                    location.reload(); // Reload the page to see the new store
                } else {
                    alert("Failed to add store.");
                }
            });
        }
    });

    // Handle edit button click
    $(document).on('click', '.edit-btn', function() {
        var storeName = $(this).data('store');
        var newStoreName = prompt("Edit store name:", storeName);
        if (newStoreName) {
            $.post('/stores/edit', { oldStore: storeName, newStore: newStoreName }, function(response) {
                if (response.success) {
                    location.reload(); // Reload the page to see the updated store
                } else {
                    alert("Failed to edit store.");
                }
            });
        }
    });

    // Handle delete button click
    $(document).on('click', '.delete-btn', function() {
        var storeName = $(this).data('store');
        if (confirm("Are you sure you want to delete this store?")) {
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
