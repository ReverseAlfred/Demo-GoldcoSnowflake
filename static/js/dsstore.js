document.addEventListener('DOMContentLoaded', async () => {
    const itemsContainer = document.getElementById('itemsContainer');
    const filterInput = document.getElementById('filterInput');
    const floatingFormContainer = document.getElementById('floatingFormContainer');
    const storeForm = document.getElementById('storeForm');
    const floatingMessage = document.getElementById('floatingMessage');
    const deleteConfirmation = document.getElementById('deleteConfirmation');
    const cancelButton = document.getElementById('cancelButton');
    const confirmDeleteButton = document.getElementById('confirmDelete');
    const cancelDeleteButton = document.getElementById('cancelDelete');
    const addButton = document.getElementById('addButton');
    let currentItemId = null;

    // Ensure elements are present
    if (!filterInput || !itemsContainer || !floatingFormContainer || !storeForm || !floatingMessage || !deleteConfirmation || !cancelButton || !confirmDeleteButton || !cancelDeleteButton || !addButton) {
        console.error('One or more required elements are missing.');
        return;
    }

    // Fetch and populate items
    async function fetchItems() {
        try {
            const response = await fetch('/dsstore');
            const data = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(data, 'text/html');
            const newTbody = doc.querySelector('#itemsContainer tbody').innerHTML;
            itemsContainer.querySelector('tbody').innerHTML = newTbody;
        } catch (error) {
            console.error('Error fetching store data:', error);
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
        document.getElementById('formTitle').textContent = 'Add Store';
        storeForm.reset();
        currentItemId = null;
        floatingFormContainer.style.display = 'flex';
    });

    // Cancel floating form
    cancelButton.addEventListener('click', () => {
        floatingFormContainer.style.display = 'none';
    });

    // Save store (Add/Edit)
    storeForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const formData = new FormData(storeForm);
        const data = {
            storeId: currentItemId,  // Ensure storeId is included
            storeName: formData.get('storeName'),
            location: formData.get('location'),
            size: formData.get('size'),
            manager: formData.get('manager'),
            contactInfo: formData.get('contactInfo')
        };
        const url = currentItemId ? `/dsstore/update_store` : '/dsstore/add';
        const method = currentItemId ? 'POST' : 'POST';  // Updated to use POST for both

        console.log('Form Data:', data);  // Log form data for debugging

        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            const result = await response.json();
            console.log('Server Response:', result);  // Log server response for debugging

            if (response.ok) {
                showMessage('success', currentItemId ? 'Store updated successfully.' : 'Store added successfully.');
                await fetchItems(); // Reload items or update the DOM as needed
                floatingFormContainer.style.display = 'none';
            } else {
                throw new Error(result.message || 'Failed to save store.');
            }
        } catch (error) {
            showMessage('error', error.message);
        }
    });

    // Edit button click
    itemsContainer.addEventListener('click', (event) => {
        if (event.target.classList.contains('edit-button')) {
            currentItemId = event.target.getAttribute('data-id');
            document.getElementById('formTitle').textContent = 'Edit Store';
            // Populate form with current item details
            const item = event.target.closest('.item');
            const fields = item.querySelectorAll('td');
            document.getElementById('storeName').value = fields[1].textContent;
            document.getElementById('location').value = fields[2].textContent;
            document.getElementById('size').value = fields[3].textContent;
            document.getElementById('manager').value = fields[4].textContent;
            document.getElementById('contactInfo').value = fields[5].textContent;
            floatingFormContainer.style.display = 'flex';
        }

        if (event.target.classList.contains('delete-button')) {
            currentItemId = event.target.getAttribute('data-id');
            deleteConfirmation.style.display = 'flex';
        }
    });

    // Confirm delete
    confirmDeleteButton.addEventListener('click', async () => {
        try {
            const response = await fetch(`/dsstore/delete_store`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ storeId: currentItemId }),
            });

            const result = await response.json();
            console.log('Delete Response:', result);  // Log server response for debugging

            if (response.ok) {
                showMessage('success', 'Store deleted successfully.');
                await fetchItems(); // Reload items or update the DOM as needed
                deleteConfirmation.style.display = 'none';
            } else {
                throw new Error(result.message || 'Failed to delete store.');
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
