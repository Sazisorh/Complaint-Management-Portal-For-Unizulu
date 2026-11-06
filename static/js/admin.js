// Keep administrator-created usernames aligned with the role-specific ID format.
const newUserRole = document.getElementById('new-user-role');
const newUserUsername = document.getElementById('new-user-username');

function updateNewUserIdValidation() {
    const prefix = { student: '20', staff: '30', manager: '40', admin: '50' }[newUserRole.value];
    newUserUsername.pattern = `${prefix}[0-9]{7}`;
    newUserUsername.placeholder = `${prefix}XXXXXXX`;
    newUserUsername.title = `ID must be exactly 9 digits and start with ${prefix}.`;
}

newUserRole.addEventListener('change', updateNewUserIdValidation);
updateNewUserIdValidation();
