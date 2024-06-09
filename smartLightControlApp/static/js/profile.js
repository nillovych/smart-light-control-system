function startTrainingModel(event) {
    event.preventDefault();
    document.getElementById('loadingAnimation').style.display = 'block';
    document.body.classList.add('disabled-element');

    fetch(urlTrainModels, { method: 'GET' })
    .then(response => response.json())
    .then(data => {
        document.getElementById('loadingAnimation').style.display = 'none';
        document.body.classList.remove('disabled-element');
        const modelMessageContainer = document.getElementById('modelMessage');
        const alertClass = data.status === 'success' ? 'alert-success' : 'alert-danger';
        const messageHTML = `<div class="alert ${alertClass}">${data.message}</div>`;
        if (modelMessageContainer) {
            modelMessageContainer.innerHTML = messageHTML;
        } else {
            const newMessage = document.createElement('div');
            newMessage.id = 'modelMessage';
            newMessage.className = 'mt-2';
            newMessage.innerHTML = messageHTML;
            document.getElementById('createModelContainer').appendChild(newMessage);
        }
    })
    .catch(error => {
        document.getElementById('loadingAnimation').style.display = 'none';
        document.body.classList.remove('disabled-element');
        const modelMessageContainer = document.getElementById('modelMessage');
        const errorMessageHTML = '<div class="alert alert-danger">Сталась помилка при створенні моделі.</div>';
        if (modelMessageContainer) {
            modelMessageContainer.innerHTML = errorMessageHTML;
        } else {
            const newMessage = document.createElement('div');
            newMessage.id = 'modelMessage';
            newMessage.className = 'mt-2';
            newMessage.innerHTML = errorMessageHTML;
            document.getElementById('createModelContainer').appendChild(newMessage);
        }
    });
}

document.getElementById('consentCheckbox').addEventListener('change', function () {
    const consent = this.checked;
    const csrfToken = csrfTokenValue;
    const createModelContainer = document.getElementById('createModelContainer');

    fetch(urlUpdateConsent, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        },
        body: 'consent=' + consent
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log('Consent updated successfully.');
            if (consent) {
                createModelContainer.classList.add('show');
            } else {
                createModelContainer.classList.remove('show');
            }
        } else {
            console.error('Failed to update consent:', data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

function toggleAiControl() {
    const csrfToken = csrfTokenValue;
    const toggleButton = document.getElementById('toggleAiControlButton');
    const currentState = toggleButton.textContent === 'Стоп';
    const newState = !currentState;

    toggleButton.textContent = newState ? 'Стоп' : 'Старт';

    fetch(urlAiControlEnabled, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        },
        body: 'ai_control_enabled=' + newState
    })
    .then(response => response.json())
    .then(data => {
        if (data.status !== 'success') {
            console.error('Failed to toggle AI control:', data.message);
            toggleButton.textContent = currentState ? 'Стоп' : 'Старт'; // Revert back in case of error
        }
    })
    .catch(error => {
        console.error('Error:', error);
        toggleButton.textContent = currentState ? 'Стоп' : 'Старт'; // Revert back in case of error
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const consentCheckbox = document.getElementById('consentCheckbox');
    const createModelContainer = document.getElementById('createModelContainer');
    if (consentCheckbox.checked) {
        createModelContainer.classList.add('show');
    } else {
        createModelContainer.classList.remove('show');
    }

    const toggleButton = document.getElementById('toggleAiControlButton');
    if (toggleButton) {
        const currentState = aiControlEnabledValue === 'True';
        toggleButton.textContent = currentState ? 'Стоп' : 'Старт';
    }
});
