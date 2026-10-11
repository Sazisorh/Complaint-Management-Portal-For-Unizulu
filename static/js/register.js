const registrationRole = document.getElementById('register-role');
const registrationUsername = document.getElementById('register-username');
const registrationDepartmentGroup = document.getElementById('register-department-group');
const registrationDepartment = document.getElementById('register-department');

function updateRegistrationFields() {
    const role = registrationRole.value;
    const prefix = { student: '20', staff: '30', admin: '50' }[role] || '20';
    const isStaff = role === 'staff';

    registrationUsername.pattern = `${prefix}[0-9]{7}`;
    registrationUsername.placeholder = `Enter your 9-digit ID starting with ${prefix}`;
    registrationUsername.title = `ID must be exactly 9 digits and start with ${prefix}.`;
    registrationDepartmentGroup.classList.toggle('is-hidden', !isStaff);
    registrationDepartment.required = isStaff;
    if (!isStaff) {
        registrationDepartment.value = '';
    }
}

registrationRole.addEventListener('change', updateRegistrationFields);
updateRegistrationFields();
