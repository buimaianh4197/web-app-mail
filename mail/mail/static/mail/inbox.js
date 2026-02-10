document.addEventListener('DOMContentLoaded', function() {

    document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
    document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
    document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
    document.querySelector('#compose').addEventListener('click', compose_email);

    document.querySelector('#compose-form').onsubmit = submit_email;

    load_mailbox('inbox');
});

function getCookie(name) {
    const cookies = document.cookie.split(';');

    const foundCookie = cookies.find(row => row.trim().startsWith(name + '='));

    return foundCookie ? decodeURIComponent(foundCookie.split('=')[1]) : null;
}

function compose_email() {
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'block';
    document.querySelector('#email-detail-view').style.display = 'none';

    document.querySelector('#compose-recipients').value = '';
    document.querySelector('#compose-subject').value = '';
    document.querySelector('#compose-body').value = '';
}

function submit_email() {
    const recipients = document.querySelector('#compose-recipients').value;
    const subject = document.querySelector('#compose-subject').value;
    const body = document.querySelector('#compose-body').value;

    fetch('/emails', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            recipients: recipients,
            subject: subject,
            body: body
        })
    })
    .then(response => response.json())
    .then(result => {
        console.log(result);
        load_mailbox('sent');
    })
    .catch(error => console.log('Error:', error));

    return false;
}

function load_mailbox(mailbox) {
    document.querySelector('#emails-view').style.display = 'block';
    document.querySelector('#compose-view').style.display = 'none';
    document.querySelector('#email-detail-view').style.display = 'none';

    document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

    fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(emails => {
        emails.forEach(email => {
            const element = document.createElement('div');
            element.className = "list-group-item d-flex justify-content-between align-items-center mb-1";
            element.style.cursor = 'pointer';
            element.style.border = '1px solid #ddd';
            element.style.padding = '10px';
            
            element.style.backgroundColor = email.read ? '#f8f9fa' : 'white';
            element.style.fontWeight = email.read ? 'normal' : 'bold';

            element.innerHTML = `
                <span>
                    <strong class="mr-3">${email.sender}</strong> 
                    <span>${email.subject}</span>
                </span>
                <span class="text-muted small">${email.timestamp}</span>
            `;

            element.addEventListener('click', () => view_email(email.id));
            document.querySelector('#emails-view').append(element);
        });
    });
}

function view_email(id) {
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'none';
    const detailView = document.querySelector('#email-detail-view');
    detailView.style.display = 'block';
    detailView.innerHTML = '';

    fetch(`/emails/${id}`)
    .then(response => response.json())
    .then(email => {
        detailView.innerHTML = `
            <div class="mb-3">
                <div><strong>From:</strong> ${email.sender}</div>
                <div><strong>To:</strong> ${email.recipients.join(", ")}</div>
                <div><strong>Subject:</strong> ${email.subject}</div>
                <div><strong>Timestamp:</strong> ${email.timestamp}</div>
            </div>
            <hr>
            <div style="white-space: pre-wrap;" class="mb-4">${email.body}</div>
            <hr>
        `;

        if (!email.read) {
            fetch(`/emails/${id}`, {
                method: 'PUT',
                headers: { 'X-CSRFToken': getCookie('csrftoken') },
                body: JSON.stringify({ read: true })
            });
        }

        const btn_archive = document.createElement('button');
        btn_archive.innerHTML = email.archived ? "Unarchive" : "Archive";
        btn_archive.className = email.archived ? "btn btn-sm btn-warning mr-2" : "btn btn-sm btn-outline-primary mr-2";
        btn_archive.onclick = () => {
            fetch(`/emails/${id}`, {
                method: 'PUT',
                headers: { 'X-CSRFToken': getCookie('csrftoken') },
                body: JSON.stringify({ archived: !email.archived })
            })
            .then(() => load_mailbox('inbox'));
        };
        detailView.append(btn_archive);

        const btn_reply = document.createElement('button');
        btn_reply.innerHTML = "Reply";
        btn_reply.className = "btn btn-sm btn-outline-secondary";
        btn_reply.onclick = () => {
            compose_email();
            document.querySelector('#compose-recipients').value = email.sender;
            let subject = email.subject;
            if (!subject.startsWith("Re: ")) {
                subject = `Re: ${subject}`;
            }
            document.querySelector('#compose-subject').value = subject;
            document.querySelector('#compose-body').value = `\n\nOn ${email.timestamp} ${email.sender} wrote:\n${email.body}\n-----------------------------------\n`;
        };
        detailView.append(btn_reply);
    });
}