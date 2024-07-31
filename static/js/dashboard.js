document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('.sidebar button');
    const messageElement = document.getElementById('floatingMessage');

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
