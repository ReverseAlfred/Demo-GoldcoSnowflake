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

            if (response.ok) {
                // Show success message and redirect to dashboard
                messageElement.textContent = 'Login successful!';
                messageElement.className = 'floating-message success show';

                // Redirect after a short delay
                setTimeout(() => {
                    window.location.href = '/dashboard'; // Use /dashboard here
                }, 1500); // Adjust delay as needed
            } else {
                // Read and display the response text
                const text = await response.text();
                messageElement.textContent = text;
                messageElement.className = 'floating-message error show';

                // Hide message after a few seconds
                setTimeout(() => {
                    messageElement.className = 'floating-message error hide';
                }, 3000); // Adjust delay as needed
            }
        } catch (error) {
            // Handle network or other errors
            messageElement.textContent = 'An unexpected error occurred. Please try again.';
            messageElement.className = 'floating-message error show';

            // Hide message after a few seconds
            setTimeout(() => {
                messageElement.className = 'floating-message error hide';
            }, 3000); // Adjust delay as needed
        }
    });
});
