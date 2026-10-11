document.querySelectorAll('input[type="password"]').forEach((input) => {
    if (input.parentElement.classList.contains('password-field')) {
        return;
    }

    const wrapper = document.createElement('div');
    wrapper.className = 'password-field';
    input.parentNode.insertBefore(wrapper, input);
    wrapper.appendChild(input);

    const button = document.createElement('button');
    button.className = 'password-toggle';
    button.type = 'button';
    button.setAttribute('aria-label', 'Show password');
    button.setAttribute('aria-pressed', 'false');
    const showIcon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12Z"></path><circle cx="12" cy="12" r="3"></circle></svg>';
    const hideIcon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m3 3 18 18M10.6 5.2A10.8 10.8 0 0 1 12 5c6.4 0 10 7 10 7a16 16 0 0 1-3.1 4.1M6.2 6.2C3.5 8 2 12 2 12s3.6 7 10 7c1.4 0 2.7-.4 3.8-1"></path><path d="M9.9 9.9a3 3 0 0 0 4.2 4.2"></path></svg>';
    button.innerHTML = showIcon;
    button.addEventListener('click', () => {
        const reveal = input.type === 'password';
        input.type = reveal ? 'text' : 'password';
        button.innerHTML = reveal ? hideIcon : showIcon;
        button.setAttribute('aria-label', reveal ? 'Hide password' : 'Show password');
        button.setAttribute('aria-pressed', String(reveal));
    });
    wrapper.appendChild(button);
});
