document.addEventListener('DOMContentLoaded', () => {
    const filterInput = document.getElementById('filterInput');
    const addItemButton = document.getElementById('addItemButton');
    const itemsContainer = document.getElementById('itemsContainer');
    const storesButton = document.getElementById('storesButton');

    // Function to handle filtering
    filterInput.addEventListener('input', () => {
        const filterValue = filterInput.value.toLowerCase();
        const items = itemsContainer.getElementsByClassName('item');
        
        Array.from(items).forEach(item => {
            const text = item.textContent.toLowerCase();
            item.style.display = text.includes(filterValue) ? 'flex' : 'none';
        });
    });

    // Function to handle adding new items
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

    // Function to handle store button redirection
    if (storesButton) {
        storesButton.addEventListener('click', () => {
            window.location.href = '/dsstore';
        });
    }
});
