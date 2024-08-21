document.addEventListener('DOMContentLoaded', async () => {
    const itemsContainer = document.getElementById('itemsContainer');
    const filterInput = document.getElementById('filterInput');
    const floatingFormContainer = document.getElementById('floatingFormContainer');
    const planogramForm = document.getElementById('planogramForm');
    const floatingMessage = document.getElementById('floatingMessage');
    const deleteConfirmation = document.getElementById('deleteConfirmation');
    const cancelDeleteButton = document.getElementById('cancelDelete');
    const confirmDeleteButton = document.getElementById('confirmDelete');
    const addButton = document.getElementById('addButton');

    let currentItemId = null;

    // Check if required elements are available
    if (!filterInput || !itemsContainer || !floatingFormContainer || !planogramForm || !floatingMessage || !deleteConfirmation || !cancelDeleteButton || !confirmDeleteButton || !addButton) {
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

    // Fetch and display items
    async function fetchItems() {
        try {
            const response = await fetch('/dsplanogram');
            const data = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(data, 'text/html');
            const newTbody = doc.querySelector('#itemsContainer tbody').innerHTML;
            itemsContainer.querySelector('tbody').innerHTML = newTbody;
        } catch (error) {
            console.error('Error fetching planogram data:', error);
            showMessage('error', 'Failed to load planogram data.');
        }
    }

    await fetchItems();

    // Filter items based on search input
    filterInput.addEventListener('input', () => {
        const filterText = filterInput.value.toLowerCase();
        const items = itemsContainer.querySelectorAll('.item');
        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            item.style.display = text.includes(filterText) ? '' : 'none';
        });
    });

    // Show form for adding new planogram record
    addButton.addEventListener('click', () => {
        document.getElementById('formTitle').textContent = 'Add Planogram';
        planogramForm.reset();
        currentItemId = null;
        floatingFormContainer.style.display = 'flex';
    });

    // Cancel form and close the floating form container
    document.getElementById('cancelButton').addEventListener('click', () => {
        floatingFormContainer.style.display = 'none';
    });

    planogramForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        
        // Validate form
        if (!planogramForm.checkValidity()) {
            showMessage('error', 'Please fill in all required fields.');
            return;
        }
    
        const formData = new FormData(planogramForm);
        const data = {
            planogramName: formData.get('planogramName') || '',  // Ensure non-null value
            dbStatus: parseInt(formData.get('dbStatus')) || 0  // Ensure integer value
        };
        
        // Debugging - log data before sending
        console.log('Data being sent:', data);
        
        if (!data.planogramName || isNaN(data.dbStatus)) {
            showMessage('error', 'All fields are required.');
            return;
        }
        
        const url = currentItemId ? `/dsplanogram/update_planogram` : '/dsplanogram/add';
    
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
                showMessage('success', currentItemId ? 'Planogram updated successfully.' : 'Planogram added successfully.');
                floatingFormContainer.style.display = 'none';
                await fetchItems();  // Refresh the items list
            } else {
                showMessage('error', result.message || 'Failed to save planogram.');
            }
        } catch (error) {
            console.error('Error saving planogram:', error);
            showMessage('error', 'An error occurred while saving the planogram.');
        }
    });    

    // Handle edit and delete button clicks
    itemsContainer.addEventListener('click', (event) => {
        if (event.target.classList.contains('edit-button')) {
            currentItemId = event.target.getAttribute('data-id');
            document.getElementById('formTitle').textContent = 'Edit Planogram';
            const item = event.target.closest('.item');
            const fields = item.querySelectorAll('td');
            document.getElementById('planogramName').value = fields[1].textContent;
            document.getElementById('dbStatus').value = fields[2].textContent;
            floatingFormContainer.style.display = 'flex';
        }

        if (event.target.classList.contains('delete-button')) {
            currentItemId = event.target.getAttribute('data-id');
            deleteConfirmation.style.display = 'flex';
        }
    });

    // Confirm delete action
    confirmDeleteButton.addEventListener('click', async () => {
        try {
            const response = await fetch(`/dsplanogram/delete_planogram`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ planogramId: currentItemId }),
            });

            const result = await response.json();

            if (response.ok) {
                showMessage('success', 'Planogram deleted successfully.');
                await fetchItems();
                deleteConfirmation.style.display = 'none';
            } else {
                throw new Error(result.message || 'Failed to delete planogram.');
            }
        } catch (error) {
            showMessage('error', error.message);
        }
    });

    // Cancel delete action
    cancelDeleteButton.addEventListener('click', () => {
        deleteConfirmation.style.display = 'none';
    });

    // Display message function
    function showMessage(type, message) {
        floatingMessage.textContent = message;
        floatingMessage.className = `floating-message ${type} show`;
        floatingMessage.style.display = 'block';
        setTimeout(() => {
            floatingMessage.style.display = 'none';
        }, 3000);
    }
});
