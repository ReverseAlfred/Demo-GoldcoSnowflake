document.addEventListener('DOMContentLoaded', () => {
    const filterInput = document.getElementById('filterInput');
    const addItemButton = document.getElementById('addItemButton');
    const itemsContainer = document.getElementById('itemsContainer');
    const buttons = document.querySelectorAll('.sidebar button');
    const messageElement = document.getElementById('floatingMessage');

    // Filter items based on input
    filterInput.addEventListener('input', () => {
        const filterValue = filterInput.value.toLowerCase();
        const items = itemsContainer.getElementsByClassName('item');
        
        Array.from(items).forEach(item => {
            const text = item.textContent.toLowerCase();
            item.style.display = text.includes(filterValue) ? 'flex' : 'none';
        });
    });

    // Add new item
    addItemButton.addEventListener('click', () => {
        const newItem = document.createElement('div');
        newItem.className = 'item';
        newItem.innerHTML = `
            <span>New Store</span>
            <button class="edit-button">Edit</button>
            <button class="delete-button">Delete</button>
        `;
        itemsContainer.appendChild(newItem);
    });

    // Navigation buttons
    buttons.forEach(button => {
        button.addEventListener('click', (event) => {
            const buttonText = event.target.textContent;
            messageElement.textContent = `${buttonText} clicked!`;
            messageElement.className = 'floating-message success show'; // Show success message for now

            setTimeout(() => {
                messageElement.classList.remove('show');
            }, 5000); // Hide after 5 seconds

            // Redirect based on button text
            switch (buttonText) {
                case 'Stores':
                    window.location.href = '/dsstore';
                    break;
                case 'Products':
                    // Implement navigation to Products
                    break;
                case 'FloorPlans':
                    // Implement navigation to FloorPlans
                    break;
                case 'Planograms':
                    // Implement navigation to Planograms
                    break;
                case 'Positions':
                    // Implement navigation to Positions
                    break;
                case 'Performance':
                    // Implement navigation to Performance
                    break;
                default:
                    console.warn('Unhandled button text:', buttonText);
            }
        });
    });
});
