var notifyElements = document.querySelectorAll('[id^="dlog-notify-"]');
var back = document.getElementById('close-button');
var dlog = document.getElementById('dialog-container');

var messageElement = document.getElementById('dialog-message');

var dialogForm = document.getElementById('dialogForm');

notifyElements.forEach(function (notifyElement) {
  notifyElement.addEventListener('click', function () {
    var message = this.getAttribute('data-message');

    var dlogID = this.getAttribute('dlogID');
    messageElement.innerHTML = message;

    dialogForm.querySelector('input[name="dialogID"]').value = dlogID;
    dlog.showModal();
  });
});

back.addEventListener('click', function () {
  dlog.close();
});
