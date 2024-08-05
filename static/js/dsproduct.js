document.addEventListener('DOMContentLoaded', async () => {
    const itemsContainer = document.getElementById('itemsContainer');
    const filterInput = document.getElementById('filterInput');
    const floatingFormContainer = document.getElementById('floatingFormContainer');
    const productForm = document.getElementById('productForm');
    const floatingMessage = document.getElementById('floatingMessage');
    const deleteConfirmation = document.getElementById('deleteConfirmation');
    const cancelButton = document.getElementById('cancelButton');
    const confirmDeleteButton = document.getElementById('confirmDelete');
    const cancelDeleteButton = document.getElementById('cancelDelete');
    const addButton = document.getElementById('addProductBtn'); // Updated ID

    let currentProductId = null;

    // Ensure elements are present
    if (!filterInput || !itemsContainer || !floatingFormContainer || !productForm || !floatingMessage || !deleteConfirmation || !cancelButton || !confirmDeleteButton || !cancelDeleteButton || !addButton) {
        console.error('One or more required elements are missing.');
        return;
    }

    // Sidebar navigation
    const sidebarButtons = {
        'Dashboard': '/dashboard',
        'Cluster': '/dscluster',
        'Stores': '/dsstore',
        'Products': '/dsproduct',
        'FloorPlans': '/dsfloorplan',
        'Planograms': '/dsplanogram',
        'Performance': '/dsperformance',
        'Positions': '/dsposition'
    };

    document.querySelector('.sidebar').addEventListener('click', (event) => {
        // Check if the clicked element is a button
        if (event.target.tagName === 'BUTTON') {
            const buttonText = event.target.textContent.trim();
            if (sidebarButtons[buttonText]) {
                window.location.href = sidebarButtons[buttonText];
                showMessage('success', `${buttonText} clicked!`);
            }
        }
    });

    // Fetch and populate items
    async function fetchItems() {
        try {
            const response = await fetch('/dsproduct');
            const data = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(data, 'text/html');
            const newTbody = doc.querySelector('#itemsContainer tbody').innerHTML;
            itemsContainer.querySelector('tbody').innerHTML = newTbody;
        } catch (error) {
            console.error('Error fetching product data:', error);
            showMessage('error', 'Failed to load product data.');
        }
    }

    await fetchItems();

    // Filter items
    filterInput.addEventListener('input', () => {
        const filterText = filterInput.value.toLowerCase();
        const items = itemsContainer.querySelectorAll('.item');
        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            item.style.display = text.includes(filterText) ? '' : 'none';
        });
    });

    // Show floating form
    addButton.addEventListener('click', () => {
        document.getElementById('formTitle').textContent = 'Add Product';
        productForm.reset();
        currentProductId = null;
        floatingFormContainer.style.display = 'flex';
    });

    // Cancel floating form
    cancelButton.addEventListener('click', () => {
        floatingFormContainer.style.display = 'none';
    });

    // Save product (Add/Edit)
    productForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        // Form validation
        if (!productForm.checkValidity()) {
            showMessage('error', 'Please fill in all required fields.');
            return;
        }

        const formData = new FormData(productForm);
        const data = {
            productId: currentProductId,
            productName: formData.get('productName'),
            category: formData.get('category'),
            brand: formData.get('brand'),
            price: formData.get('price'),
            description: formData.get('description'),
            sku: formData.get('sku'),
            dimensions: formData.get('dimensions'),
            weight: formData.get('weight')
        };

        const url = currentProductId ? `/dsproduct/update_product` : '/dsproduct/add';

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            const result = await response.json();

            if (response.ok) {
                showMessage('success', currentProductId ? 'Product updated successfully.' : 'Product added successfully.');
                await fetchItems(); // Reload items or update the DOM as needed
                floatingFormContainer.style.display = 'none';
            } else {
                throw new Error(result.message || 'Failed to save product.');
            }
        } catch (error) {
            showMessage('error', error.message);
        }
    });

    // Edit button click
    itemsContainer.addEventListener('click', (event) => {
        if (event.target.classList.contains('edit-button')) {
            currentProductId = event.target.getAttribute('data-id');
            document.getElementById('formTitle').textContent = 'Edit Product';
            // Populate form with current item details
            const item = event.target.closest('.item');
            const fields = item.querySelectorAll('td');
            document.getElementById('productName').value = fields[1].textContent;
            document.getElementById('category').value = fields[2].textContent;
            document.getElementById('brand').value = fields[3].textContent;
            document.getElementById('price').value = fields[4].textContent;
            document.getElementById('description').value = fields[5].textContent;
            document.getElementById('sku').value = fields[6].textContent;
            document.getElementById('dimensions').value = fields[7].textContent;
            document.getElementById('weight').value = fields[8].textContent;
            floatingFormContainer.style.display = 'flex';
        }

        if (event.target.classList.contains('delete-button')) {
            currentProductId = event.target.getAttribute('data-id');
            deleteConfirmation.style.display = 'flex';
        }
    });

    // Confirm delete
    confirmDeleteButton.addEventListener('click', async () => {
        try {
            const response = await fetch(`/dsproduct/delete_product`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ productId: currentProductId }),
            });

            const result = await response.json();

            if (response.ok) {
                showMessage('success', 'Product deleted successfully.');
                await fetchItems(); // Reload items or update the DOM as needed
                deleteConfirmation.style.display = 'none';
            } else {
                throw new Error(result.message || 'Failed to delete product.');
            }
        } catch (error) {
            showMessage('error', error.message);
        }
    });

    // Cancel delete
    cancelDeleteButton.addEventListener('click', () => {
        deleteConfirmation.style.display = 'none';
    });

    // Show message
    function showMessage(type, message) {
        floatingMessage.textContent = message;
        floatingMessage.className = `floating-message ${type} show`;
        setTimeout(() => {
            floatingMessage.classList.remove('show');
        }, 3000);
    }
});
