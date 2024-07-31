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
        });
    });
});
