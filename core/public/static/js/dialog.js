var notifyElements = document.querySelectorAll('[id^="dlog-notify-"]');
var back = document.getElementById('close-button');
var dlog = document.getElementById('dialog-container');

var subjectElement = document.getElementById('dialog-subject');
var messageElement = document.getElementById('dialog-message');
var sendersElement = document.getElementById('dialog-senders');

var dialogForm = document.getElementById('dialogForm');

notifyElements.forEach(function (notifyElement) {
  notifyElement.addEventListener('click', function () {
    var message = this.getAttribute('data-message');
    var subject = this.getAttribute('data-subject');
    var senders = this.getAttribute('data-senders');  

    var dlogID = this.getAttribute('dlogID');

    subjectElement.textContent = subject;
    messageElement.textContent = message;
    sendersElement.textContent = "- <"+senders+">";

    dialogForm.querySelector('input[name="dialogID"]').value = dlogID;
    dlog.showModal();
  });
});

back.addEventListener('click', function () {
  dlog.close();
});
