document.addEventListener('DOMContentLoaded', async () => {
    const itemsContainer = document.getElementById('itemsContainer');
    const filterInput = document.getElementById('filterInput');
    const floatingFormContainer = document.getElementById('floatingFormContainer');
    const floorplanForm = document.getElementById('floorplanForm');
    const floatingMessage = document.getElementById('floatingMessage');
    const deleteConfirmation = document.getElementById('deleteConfirmation');
    const cancelDeleteButton = document.getElementById('cancelDelete');
    const confirmDeleteButton = document.getElementById('confirmDelete');
    const addButton = document.getElementById('addButton');
    
    let currentItemId = null;

    // Ensure elements are present
    if (!filterInput || !itemsContainer || !floatingFormContainer || !floorplanForm || !floatingMessage || !deleteConfirmation || !cancelDeleteButton || !confirmDeleteButton || !addButton) {
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
            const response = await fetch('/dsfloorplan');
            const data = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(data, 'text/html');
            const newTbody = doc.querySelector('#itemsContainer tbody').innerHTML;
            itemsContainer.querySelector('tbody').innerHTML = newTbody;
        } catch (error) {
            console.error('Error fetching floorplan data:', error);
            showMessage('error', 'Failed to load floorplan data.');
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
        document.getElementById('formTitle').textContent = 'Add FloorPlan';
        floorplanForm.reset();
        currentItemId = null;
        floatingFormContainer.style.display = 'flex';
    });

    // Cancel floating form
    document.getElementById('cancelButton').addEventListener('click', () => {
        floatingFormContainer.style.display = 'none';
    });

    // Save floorplan (Add/Edit)
    floorplanForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        // Form validation
        if (!floorplanForm.checkValidity()) {
            showMessage('error', 'Please fill in all required fields.');
            return;
        }

        const formData = new FormData(floorplanForm);
        const data = {
            floorPlanId: currentItemId,
            storeId: formData.get('storeId'),
            floorplanDescription: formData.get('floorplanDescription'),
            layoutImage: formData.get('layoutImage'),
            dimensions: formData.get('dimensions')
        };

        const url = currentItemId ? `/dsfloorplan/update_floorplan` : '/dsfloorplan/add';

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
                showMessage('success', currentItemId ? 'FloorPlan updated successfully.' : 'FloorPlan added successfully.');
                await fetchItems(); // Reload items or update the DOM as needed
                floatingFormContainer.style.display = 'none';
            } else {
                throw new Error(result.message || 'Failed to save floorplan.');
            }
        } catch (error) {
            showMessage('error', error.message);
        }
    });

    // Edit button click
    itemsContainer.addEventListener('click', (event) => {
        if (event.target.classList.contains('edit-button')) {
            currentItemId = event.target.getAttribute('data-id');
            document.getElementById('formTitle').textContent = 'Edit FloorPlan';
            // Populate form with current item details
            const item = event.target.closest('.item');
            const fields = item.querySelectorAll('td');
            document.getElementById('storeId').value = fields[1].textContent;
            document.getElementById('floorplanDescription').value = fields[2].textContent;
            document.getElementById('layoutImage').value = fields[3].textContent;
            document.getElementById('dimensions').value = fields[4].textContent;
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
            const response = await fetch(`/dsfloorplan/delete_floorplan`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ floorPlanId: currentItemId }),
            });

            const result = await response.json();

            if (response.ok) {
                showMessage('success', 'FloorPlan deleted successfully.');
                await fetchItems(); // Reload items or update the DOM as needed
                deleteConfirmation.style.display = 'none';
            } else {
                throw new Error(result.message || 'Failed to delete floorplan.');
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