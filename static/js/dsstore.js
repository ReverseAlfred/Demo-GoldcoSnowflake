document.addEventListener('DOMContentLoaded', async () => {
    const itemsContainer = document.getElementById('itemsContainer');
    const filterInput = document.getElementById('filterInput');
    const floatingFormContainer = document.getElementById('floatingFormContainer');
    const storeForm = document.getElementById('storeForm');
    const floatingMessage = document.getElementById('floatingMessage');
    const deleteConfirmation = document.getElementById('deleteConfirmation');
    const cancelDeleteButton = document.getElementById('cancelDelete');
    const confirmDeleteButton = document.getElementById('confirmDelete');
    const addButton = document.getElementById('addButton');
    
    let currentItemId = null;

    if (!filterInput || !itemsContainer || !floatingFormContainer || !storeForm || !floatingMessage || !deleteConfirmation || !cancelDeleteButton || !confirmDeleteButton || !addButton) {
        console.error('One or more required elements are missing.');
        return;
    }

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
        if (event.target.tagName === 'BUTTON') {
            const buttonText = event.target.textContent.trim();
            if (sidebarButtons[buttonText]) {
                window.location.href = sidebarButtons[buttonText];
                showMessage('success', `${buttonText} clicked!`);
            }
        }
    });

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
            showMessage('error', 'Failed to load store data.');
        }
    }

    await fetchItems();

    filterInput.addEventListener('input', () => {
        const filterText = filterInput.value.toLowerCase();
        const items = itemsContainer.querySelectorAll('.item');
        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            item.style.display = text.includes(filterText) ? '' : 'none';
        });
    });

    addButton.addEventListener('click', () => {
        document.getElementById('formTitle').textContent = 'Add Store';
        storeForm.reset();
        currentItemId = null;
        floatingFormContainer.style.display = 'flex';
    });

    document.getElementById('cancelButton').addEventListener('click', () => {
        floatingFormContainer.style.display = 'none';
    });

    storeForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        if (!storeForm.checkValidity()) {
            showMessage('error', 'Please fill in all required fields.');
            return;
        }

        const formData = new FormData(storeForm);
        const data = {
            storeId: currentItemId,
            storeName: formData.get('storeName'),
            descriptivo1: formData.get('descriptivo1'),
            dbStatus: formData.get('dbStatus')
        };

        const url = currentItemId ? `/dsstore/update_store` : '/dsstore/add';

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
                showMessage('success', currentItemId ? 'Store updated successfully.' : 'Store added successfully.');
                await fetchItems();
                floatingFormContainer.style.display = 'none';
            } else {
                throw new Error(result.message || 'Failed to save store.');
            }
        } catch (error) {
            showMessage('error', error.message);
        }
    });

    itemsContainer.addEventListener('click', (event) => {
        if (event.target.classList.contains('edit-button')) {
            currentItemId = event.target.getAttribute('data-id');
            document.getElementById('formTitle').textContent = 'Edit Store';
            const item = event.target.closest('.item');
            const fields = item.querySelectorAll('td');
            document.getElementById('storeName').value = fields[1].textContent;
            document.getElementById('descriptivo1').value = fields[2].textContent;
            document.getElementById('dbStatus').value = fields[3].textContent;
            floatingFormContainer.style.display = 'flex';
        }

        if (event.target.classList.contains('delete-button')) {
            currentItemId = event.target.getAttribute('data-id');
            deleteConfirmation.style.display = 'flex';
        }
    });

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

            if (response.ok) {
                showMessage('success', 'Store deleted successfully.');
                await fetchItems();
                deleteConfirmation.style.display = 'none';
            } else {
                throw new Error(result.message || 'Failed to delete store.');
            }
        } catch (error) {
            showMessage('error', error.message);
        }
    });

    cancelDeleteButton.addEventListener('click', () => {
        deleteConfirmation.style.display = 'none';
    });

    function showMessage(type, message) {
        floatingMessage.textContent = message;
        floatingMessage.className = `floating-message ${type} show`;
        floatingMessage.style.display = 'block';
        setTimeout(() => {
            floatingMessage.style.display = 'none';
        }, 3000);
    }
});
