document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('setup-form');

  form?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    const payload = new URLSearchParams(formData);

    try {
      const res = await fetch('/auth/setup', {
        method: 'POST',
        body: payload,
      });

      const data = await res.json();

      if (!res.ok) {
        alert(data.detail || 'Setup failed.');
        return;
      }

      alert(data.message || 'Admin account created.');
      window.location.href = '/auth/login'; // Redirect to login
    } catch (err) {
      console.error('Setup error:', err);
      alert('Something went wrong.');
    }
  });
});
