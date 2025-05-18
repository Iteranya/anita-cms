document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('login-form');

  form?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    const payload = new URLSearchParams(formData);

    try {
      const res = await fetch('/auth/login', {
        method: 'POST',
        body: payload,
      });

      if (!res.ok) {
        const err = await res.json();
        alert(err.detail || 'Login failed.');
        return;
      }

      const result = await res.json();
      if (result.status === 'success') {
        window.location.href = '/admin'; // Redirect after login
      }
    } catch (err) {
      console.error('Login error:', err);
      alert('Something went wrong.');
    }
  });
});
