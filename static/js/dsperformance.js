document.addEventListener('DOMContentLoaded', async () => {
    const itemsContainer = document.getElementById('itemsContainer');
    const filterInput = document.getElementById('filterInput');
    const floatingFormContainer = document.getElementById('floatingFormContainer');
    const performanceForm = document.getElementById('performanceForm');
    const floatingMessage = document.getElementById('floatingMessage');
    const deleteConfirmation = document.getElementById('deleteConfirmation');
    const cancelDeleteButton = document.getElementById('cancelDelete');
    const confirmDeleteButton = document.getElementById('confirmDelete');
    const addButton = document.getElementById('addButton');

    let currentItemId = null;

    // Check if required elements are available
    if (!filterInput || !itemsContainer || !floatingFormContainer || !performanceForm || !floatingMessage || !deleteConfirmation || !cancelDeleteButton || !confirmDeleteButton || !addButton) {
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

    // Fetch and display performance items
    async function fetchItems() {
        try {
            const response = await fetch('/dsperformance');
            const data = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(data, 'text/html');
            const newTbody = doc.querySelector('#itemsContainer tbody').innerHTML;
            itemsContainer.querySelector('tbody').innerHTML = newTbody;
        } catch (error) {
            console.error('Error fetching performance data:', error);
            showMessage('error', 'Failed to load performance data.');
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

    // Show form for adding new performance record
    addButton.addEventListener('click', () => {
        document.getElementById('formTitle').textContent = 'Add Performance';
        performanceForm.reset();
        currentItemId = null;
        floatingFormContainer.style.display = 'flex';
    });

    // Cancel form and close the floating form container
    document.getElementById('cancelButton').addEventListener('click', () => {
        floatingFormContainer.style.display = 'none';
    });

    // Handle form submission for add/update
    performanceForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        if (!performanceForm.checkValidity()) {
            showMessage('error', 'Please fill in all required fields.');
            return;
        }

        const formData = new FormData(performanceForm);
        const data = {
            dbKey: currentItemId,
            dbPlanogramParentKey: formData.get('dbPlanogramParentKey'),
            dbProductParentKey: formData.get('dbProductParentKey'),
            factings: formData.get('factings'),
            capacity: formData.get('capacity'),
            unitMovement: formData.get('unitMovement'),
            sales: formData.get('sales'),
            margen: formData.get('margen'),
            cost: formData.get('cost')
        };

        const url = currentItemId ? `/dsperformance/update_performance` : '/dsperformance/add';

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
                showMessage('success', currentItemId ? 'Performance updated successfully.' : 'Performance added successfully.');
                await fetchItems();
                floatingFormContainer.style.display = 'none';
            } else {
                throw new Error(result.message || 'Failed to save performance.');
            }
        } catch (error) {
            showMessage('error', error.message);
        }
    });

    // Handle edit and delete button clicks
    itemsContainer.addEventListener('click', (event) => {
        if (event.target.classList.contains('edit-button')) {
            currentItemId = event.target.getAttribute('data-id');
            document.getElementById('formTitle').textContent = 'Edit Performance';
            const item = event.target.closest('.item');
            const fields = item.querySelectorAll('td');
            document.getElementById('dbPlanogramParentKey').value = fields[1].textContent;
            document.getElementById('dbProductParentKey').value = fields[2].textContent;
            document.getElementById('factings').value = fields[3].textContent;
            document.getElementById('capacity').value = fields[4].textContent;
            document.getElementById('unitMovement').value = fields[5].textContent;
            document.getElementById('sales').value = fields[6].textContent;
            document.getElementById('margen').value = fields[7].textContent;
            document.getElementById('cost').value = fields[8].textContent;
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
            const response = await fetch(`/dsperformance/delete_performance`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ dbKey: currentItemId }),
            });

            const result = await response.json();

            if (response.ok) {
                showMessage('success', 'Performance deleted successfully.');
                await fetchItems();
                deleteConfirmation.style.display = 'none';
            } else {
                throw new Error(result.message || 'Failed to delete performance.');
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
