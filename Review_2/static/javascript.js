document.addEventListener('DOMContentLoaded', function () {
    // Form validation for signup and login forms
    const signupForm = document.getElementById('signup-form');
    const loginForm = document.getElementById('login-form');

    if (signupForm) {
        signupForm.addEventListener('submit', function (e) {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            if (username.trim() === '' || password.trim() === '') {
                e.preventDefault();
                alert('Please fill in all fields.');
            }
        });
    }

    if (loginForm) {
        loginForm.addEventListener('submit', function (e) {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            if (username.trim() === '' || password.trim() === '') {
                e.preventDefault();
                alert('Please enter your username and password.');
            }
        });
    }

    // Toggle visibility of sections (for dashboards)
    const toggles = document.querySelectorAll('.toggle-btn');
    toggles.forEach(btn => {
        btn.addEventListener('click', function () {
            const target = document.getElementById(this.dataset.target);
            if (target) {
                target.classList.toggle('hidden');
            }
        });
    });

    // Confirm member deletion (for admin)
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            const confirmation = confirm('Are you sure you want to delete this member?');
            if (!confirmation) {
                event.preventDefault();
            }
        });
    });
});
