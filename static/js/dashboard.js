document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.querySelector('.sidebar');
    const messageElement = document.getElementById('floatingMessage');

    sidebar.addEventListener('click', (event) => {
        // Check if the clicked element is a button
        if (event.target.tagName === 'BUTTON') {
            const buttonText = event.target.textContent.trim();
            messageElement.textContent = `${buttonText} clicked!`;
            messageElement.className = 'floating-message success show'; // Show success message

            setTimeout(() => {
                messageElement.classList.remove('show');
            }, 5000); // Hide after 5 seconds

            // Redirect based on button text
            switch (buttonText) {
                case 'Dashboard':
                    window.location.href = '/dashboard';
                    break;
                case 'Cluster':
                    window.location.href = '/dscluster';
                    break;
                case 'Stores':
                    window.location.href = '/dsstore';
                    break;
                case 'Products':
                    window.location.href = '/dsproduct';
                    break;
                case 'FloorPlans':
                    window.location.href = '/dsfloorplan';
                    break;
                case 'Planograms':
                    window.location.href = '/dsplanogram';
                    break;
                case 'Performance':
                    window.location.href = '/dsperformance';
                    break;
                case 'Positions':
                    window.location.href = '/dsposition';
                    break;
                default:
                    console.warn('Unhandled button text:', buttonText);
            }
        }
    });
});
