document.addEventListener('DOMContentLoaded', async () => {
    const itemsContainer = document.getElementById('itemsContainer');
    const filterInput = document.getElementById('filterInput');
    const floatingFormContainer = document.getElementById('floatingFormContainer');
    const planogramForm = document.getElementById('planogramForm');
    const floatingMessage = document.getElementById('floatingMessage');
    const deleteConfirmation = document.getElementById('deleteConfirmation');
    const cancelButton = document.getElementById('cancelButton');
    const confirmDeleteButton = document.getElementById('confirmDelete');
    const cancelDeleteButton = document.getElementById('cancelDelete');
    const addButton = document.getElementById('addPlanogramBtn');

    let currentPlanogramId = null;

    // Ensure elements are present
    if (!filterInput || !itemsContainer || !floatingFormContainer || !planogramForm || !floatingMessage || !deleteConfirmation || !cancelButton || !confirmDeleteButton || !cancelDeleteButton || !addButton) {
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
        document.getElementById('formTitle').textContent = 'Add Planogram';
        planogramForm.reset();
        currentPlanogramId = null;
        floatingFormContainer.style.display = 'flex';
    });

    // Cancel floating form
    cancelButton.addEventListener('click', () => {
        floatingFormContainer.style.display = 'none';
    });

    // Save planogram (Add/Edit)
    planogramForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        // Form validation
        if (!planogramForm.checkValidity()) {
            showMessage('error', 'Please fill in all required fields.');
            return;
        }

        const formData = new FormData(planogramForm);
        const data = {
            planogramId: currentPlanogramId,
            planogramName: formData.get('planogramName'),
            description: formData.get('description'),
            category: formData.get('category'),
            pdfPath: formData.get('pdfPath')
        };

        const url = currentPlanogramId ? `/dsplanogram/update_planogram` : '/dsplanogram/add';

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
                showMessage('success', currentPlanogramId ? 'Planogram updated successfully.' : 'Planogram added successfully.');
                await fetchItems(); // Reload items or update the DOM as needed
                floatingFormContainer.style.display = 'none';
            } else {
                throw new Error(result.message || 'Failed to save planogram.');
            }
        } catch (error) {
            showMessage('error', error.message);
        }
    });

    // Edit button click
    itemsContainer.addEventListener('click', (event) => {
        if (event.target.classList.contains('edit-button')) {
            currentPlanogramId = event.target.getAttribute('data-id');
            document.getElementById('formTitle').textContent = 'Edit Planogram';
            // Populate form with current item details
            const item = event.target.closest('.item');
            const fields = item.querySelectorAll('td');
            document.getElementById('planogramName').value = fields[1].textContent;
            document.getElementById('description').value = fields[2].textContent;
            document.getElementById('category').value = fields[3].textContent;
            document.getElementById('pdfPath').value = fields[4].textContent; // Populate PDF Path
            floatingFormContainer.style.display = 'flex';
        }

        if (event.target.classList.contains('delete-button')) {
            currentPlanogramId = event.target.getAttribute('data-id');
            deleteConfirmation.style.display = 'flex';
        }
    });

    // Confirm delete
    confirmDeleteButton.addEventListener('click', async () => {
        try {
            const response = await fetch(`/dsplanogram/delete_planogram/${currentPlanogramId}`, {
                method: 'DELETE',
            });

            if (response.ok) {
                showMessage('success', 'Planogram deleted successfully.');
                await fetchItems(); // Reload items or update the DOM as needed
                deleteConfirmation.style.display = 'none';
            } else {
                throw new Error('Failed to delete planogram.');
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
        floatingMessage.className = `floating-message ${type} show`; // Add 'show' class to make message visible
        floatingMessage.style.display = 'block'; // Ensure it's visible
        setTimeout(() => {
            floatingMessage.style.display = 'none'; // Hide after timeout
        }, 3000);
    }
});
