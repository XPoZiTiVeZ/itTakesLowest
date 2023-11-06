function showMessages() {
    console.log('show')
    const messages = document.querySelectorAll('.messages li');
    console.log(messages);
    for (var i = 0; i < messages.length; i++) {
        console.log(i)
        console.log(messages[i]);
        let message = messages[i];
        setTimeout(function() {
            message.classList.add('show');
            message.classList.remove('hide1');
        }, 500 + i * 500);
        setTimeout(function() {
            message.classList.remove('show');
            message.classList.add('hide2');
        }, 5000 + (messages.length - i) * 500);
    };
}

window.addEventListener('load', showMessages);