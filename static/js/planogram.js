document.addEventListener('DOMContentLoaded', function() {
    // Reuse header and sidebar menu initialization if needed

    // Function to fetch products for the selected planogram
    function fetchPlanogramProducts(planogramId) {
        fetch(`/get_products?planogramId=${planogramId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayProducts(data.products);
                    document.getElementById('planogram-title').innerText = data.planogramName;
                } else {
                    // Handle error
                    console.error(data.message);
                }
            })
            .catch(error => console.error('Error fetching planogram products:', error));
    }

    // Function to display products in the item container
    function displayProducts(products) {
        const itemContainer = document.querySelector('.item-container');
        itemContainer.innerHTML = ''; // Clear existing items
        products.forEach(product => {
            const item = document.createElement('div');
            item.classList.add('item');
            item.innerText = product.name; // Customize as needed
            itemContainer.appendChild(item);
        });
    }

    // Event listener for item selection
    document.querySelectorAll('.item').forEach(item => {
        item.addEventListener('click', function() {
            const planogramId = this.getAttribute('data-planogram-id');
            fetchPlanogramProducts(planogramId);
        });
    });

    // Additional logic as needed
});
