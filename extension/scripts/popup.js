window.onload = function() {
  document.getElementById("messageInput").focus();
};

document.getElementById('messageInput').addEventListener('keypress', function(e) {
  if (e.key === 'Enter') {
      document.getElementById('sendButton').click();
  }
});

document.getElementById('sendButton').addEventListener('click', function() {
  var messageInput = document.getElementById('messageInput');
  var chatBox = document.getElementById('chatBox');

  if (messageInput.value.trim() !== '') {
      var newMessage = document.createElement('div');
      newMessage.textContent = messageInput.value;
      newMessage.classList.add('message', 'message-right');

      chatBox.appendChild(newMessage);
      chatBox.scrollTop = chatBox.scrollHeight;

      messageInput.value = '';

      // Create typing indicator
      var typingIndicator = document.createElement('div');
      typingIndicator.classList.add('typing-indicator', 'message', 'message-left');
      for (var i = 0; i < 3; i++) {
          var dot = document.createElement('div');
          dot.classList.add('dot');
          typingIndicator.appendChild(dot);
      }

      // Append typing indicator to chat box
      chatBox.appendChild(typingIndicator);
      chatBox.scrollTop = chatBox.scrollHeight;

      setTimeout(function() {
          // Remove typing indicator
          chatBox.removeChild(typingIndicator);

          var autoReply = document.createElement('div');
          autoReply.textContent = 'This feature is under development';
          autoReply.classList.add('message', 'message-left');

          chatBox.appendChild(autoReply);
          chatBox.scrollTop = chatBox.scrollHeight;
      }, 1000);
  }
});