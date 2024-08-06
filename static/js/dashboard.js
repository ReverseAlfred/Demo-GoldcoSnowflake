document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.querySelector('.sidebar');
    const messageElement = document.getElementById('floatingMessage');

    // Button mappings for navigation
    const buttonMappings = {
        'Dashboard': '/dashboard',
        'Cluster': '/dscluster',
        'Stores': '/dsstore',
        'Products': '/dsproduct',
        'FloorPlans': '/dsfloorplan',
        'Planograms': '/dsplanogram',
        'Performance': '/dsperformance',
        'Positions': '/dsposition'
    };

    sidebar.addEventListener('click', (event) => {
        // Check if the clicked element is a button
        if (event.target.tagName === 'BUTTON') {
            const buttonText = event.target.textContent.trim();
            const targetUrl = buttonMappings[buttonText];
            
            if (targetUrl) {
                // Show success message
                showMessage('success', `${buttonText} clicked!`);
                
                // Redirect based on button mapping
                window.location.href = targetUrl;
            } else {
                console.warn('Unhandled button text:', buttonText);
            }
        }
    });

    // Function to show floating message
    function showMessage(type, message) {
        messageElement.textContent = message;
        messageElement.className = `floating-message ${type} show`;
        messageElement.style.display = 'block'; // Ensure it's visible
        setTimeout(() => {
            messageElement.style.display = 'none'; // Hide after timeout
        }, 3000);
    }
});
