var notifyElements = document.querySelectorAll('[id^="dlog-notify-"]');
var back = document.getElementById('close-button');
var dlog = document.getElementById('dialog-container');

notifyElements.forEach(function (notifyElement) {
  notifyElement.addEventListener('click', function () {
    var message = this.getAttribute('data-message');
    var subject = this.getAttribute('data-subject');
    var dialog = document.getElementById('dialog');
    
    dialog.querySelector('span').textContent = subject;
    dialog.querySelector('p').textContent = message;

    dlog.showModal();
  });
});

back.addEventListener('click', function () {
  dlog.close();
});
