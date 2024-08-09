document.addEventListener('DOMContentLoaded', async () => {
    const itemsContainer = document.getElementById('itemsContainer');
    const filterInput = document.getElementById('filterInput');
    const floatingMessage = document.getElementById('floatingMessage');
    const deleteConfirmation = document.getElementById('deleteConfirmation');
    const cancelDeleteButton = document.getElementById('cancelDelete');
    const confirmDeleteButton = document.getElementById('confirmDelete');
    const addButton = document.getElementById('addButton');
    
    let currentItemId = null;

    // Ensure elements are present
    if (!filterInput || !itemsContainer || !floatingMessage || !deleteConfirmation || !cancelDeleteButton || !confirmDeleteButton) {
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
            const response = await fetch(`/clstore?clusterId={{ cluster_id }}`);
            const data = await response.json();

            const stores = data.stores || [];
            const allStores = data.allStores || [];

            const tbody = itemsContainer.querySelector('tbody');
            tbody.innerHTML = '';

            stores.forEach(store => {
                const tr = document.createElement('tr');
                tr.className = 'item';
                tr.innerHTML = `
                    <td>${store.storeId}</td>
                    <td>${store.storeName}</td>
                    <td>
                        <button class="delete-button custom-style" data-id="${store.storeId}">Delete</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        } catch (error) {
            console.error('Error fetching store data:', error);
            showMessage('error', 'Failed to load store data.');
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

    // Delete button click
    itemsContainer.addEventListener('click', (event) => {
        if (event.target.classList.contains('delete-button')) {
            currentItemId = event.target.getAttribute('data-id');
            deleteConfirmation.style.display = 'flex';
        }
    });

    // Confirm delete
    confirmDeleteButton.addEventListener('click', async () => {
        try {
            const response = await fetch(`/clstore/delete_store`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ storeId: currentItemId }),
            });

            const result = await response.json();

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
        floatingMessage.style.display = 'block'; // Ensure it's visible
        setTimeout(() => {
            floatingMessage.style.display = 'none'; // Hide after timeout
        }, 3000);
    }
});
