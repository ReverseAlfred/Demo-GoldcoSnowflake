document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const messageElement = document.getElementById('floatingMessage');

    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const formData = new FormData(loginForm);

        try {
            const response = await fetch('/login', {
                method: 'POST',
                body: formData,
            });

            const text = await response.text();

            if (response.ok) {
                // Show success message and redirect to dashboard
                showMessage('success', 'Login successful!');

                // Redirect after a short delay
                setTimeout(() => {
                    window.location.href = '/dashboard'; // Use /dashboard here
                }, 1500); // Adjust delay as needed
            } else {
                // Show error message based on response text
                showMessage('error', text);
            }
        } catch (error) {
            // Handle network or other errors
            showMessage('error', 'An unexpected error occurred. Please try again.');
        }
    });

    // Show message function to handle the display of messages
    function showMessage(type, message) {
        messageElement.textContent = message;
        messageElement.className = `floating-message ${type} show`;

        setTimeout(() => {
            messageElement.classList.remove('show');
            messageElement.classList.add('hide');
        }, 3000); // Adjust delay as needed
    }
});
