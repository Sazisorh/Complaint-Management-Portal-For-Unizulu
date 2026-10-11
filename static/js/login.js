const roleSelect = document.getElementById('role');
const departmentGroup = document.getElementById('department-group');
const departmentSelect = document.getElementById('department');
const usernameInput = document.getElementById('username');
const logo = document.querySelector('.auth-login .logo');

// Staff need a department, and each role has its own ID prefix.
function toggleDepartmentField() {
    const isStaff = roleSelect.value === 'staff';
    const prefix = { student: '20', staff: '30', admin: '50' }[roleSelect.value];
    departmentGroup.classList.toggle('is-hidden', !isStaff);
    departmentSelect.required = isStaff;
    if (!isStaff) {
        departmentSelect.value = '';
    }

    if (prefix) {
        usernameInput.pattern = `${prefix}[0-9]{7}`;
        usernameInput.title = `ID must be exactly 9 digits and start with ${prefix}.`;
        usernameInput.placeholder = `Enter your 9-digit ID starting with ${prefix}`;
        usernameInput.maxLength = 9;
        usernameInput.inputMode = 'numeric';
    } else {
        usernameInput.removeAttribute('pattern');
        usernameInput.removeAttribute('title');
        usernameInput.placeholder = 'Select a role first';
        usernameInput.inputMode = 'text';
    }
}

roleSelect.addEventListener('change', toggleDepartmentField);
toggleDepartmentField();

// Hide the logo if its image file cannot be loaded.
logo.addEventListener('error', function () {
    logo.classList.add('is-hidden');
});
