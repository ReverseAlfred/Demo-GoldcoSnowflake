document.addEventListener('DOMContentLoaded', async () => {
    const itemsContainer = document.getElementById('itemsContainer');
    const filterInput = document.getElementById('filterInput');
    const floatingFormContainer = document.getElementById('floatingFormContainer');
    const storeForm = document.getElementById('floorplanForm');
    const floatingMessage = document.getElementById('floatingMessage');
    const deleteConfirmation = document.getElementById('deleteConfirmation');
    const cancelDeleteButton = document.getElementById('cancelDelete');
    const confirmDeleteButton = document.getElementById('confirmDelete');
    const addButton = document.getElementById('addButton');
    
    let currentItemId = null;

    // Function to get URL parameter
    function getUrlParameter(name) {
        const regex = new RegExp(`[?&]${name}=([^&#]*)`);
        const results = regex.exec(window.location.search);
        return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
    }

    const currentStoreId = getUrlParameter('storeId'); // Read storeId from URL

    // Ensure elements are present
    if (!filterInput || !itemsContainer || !floatingFormContainer || !storeForm || !floatingMessage || !deleteConfirmation || !cancelDeleteButton || !confirmDeleteButton || !addButton) {
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
            const response = await fetch(`/stfloorplan?storeId=${currentStoreId}`);
            const data = await response.text(); // Assuming HTML response
            const parser = new DOMParser();
            const doc = parser.parseFromString(data, 'text/html');
            const newTbody = doc.querySelector('#itemsContainer tbody').innerHTML;
            itemsContainer.querySelector('tbody').innerHTML = newTbody;
        } catch (error) {
            console.error('Error fetching store floor plan data:', error);
            showMessage('error', 'Failed to load store floor plan data.');
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
        document.getElementById('formTitle').textContent = 'Add Store to Floor Plan';
        storeForm.reset();
        floatingFormContainer.style.display = 'flex';
    });

    // Cancel floating form
    document.getElementById('cancelButton').addEventListener('click', () => {
        floatingFormContainer.style.display = 'none';
    });

    // Add store form submit
    storeForm.addEventListener('submit', async (event) => {
        event.preventDefault();
    
        const formData = new FormData(storeForm);
        const data = {
            storeId: currentStoreId,
            floorplanId: formData.get('floorplanId')
        };
    
        try {
            const response = await fetch('/stfloorplan/add_floorplan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });
    
            const result = await response.json();
    
            if (response.ok) {
                showMessage('success', 'Floorplan added to store successfully.');
                await fetchItems();
                floatingFormContainer.style.display = 'none';
            } else {
                throw new Error(result.message || 'Failed to add floorplan to store.');
            }
        } catch (error) {
            showMessage('error', error.message);
        }
    });    

    // Handle delete button click
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

    // Confirm delete
    confirmDeleteButton.addEventListener('click', async () => {
        try {
            const response = await fetch('/stfloorplan/delete_floorplan', { // Updated route
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    storeId: currentStoreId, // Ensure the correct data key
                    floorplanId: currentItemId // Ensure the correct data key
                }),
            });

            const result = await response.json();

            if (response.ok) {
                showMessage('success', 'Floorplan removed from store successfully.');
                await fetchItems();
                deleteConfirmation.style.display = 'none';
            } else {
                throw new Error(result.message || 'Failed to remove floorplan from store.');
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
        floatingMessage.style.display = 'block';
        setTimeout(() => {
            floatingMessage.style.display = 'none';
        }, 3000);
    }
});
