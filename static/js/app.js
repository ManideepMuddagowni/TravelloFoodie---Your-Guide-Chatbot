document.addEventListener("DOMContentLoaded", function () {
  const chatPopupBtn = document.getElementById("chat-popup-btn");
  const chatWidget = document.getElementById("chat-widget");
  const chatMessages = document.getElementById("chat-messages");
  const chatInput = document.getElementById("chat-input");
  const chatSendBtn = document.getElementById("chat-send-btn");
  const chatCloseBtn = document.getElementById("chat-close-btn");

  chatPopupBtn.addEventListener("click", () => {
    chatWidget.style.display = "flex";
  });

  chatCloseBtn.addEventListener("click", () => {
    chatWidget.style.display = "none";
  });

  chatSendBtn.addEventListener("click", () => {
    const userMessage = chatInput.value.trim();
    if (!userMessage) return;

    // Create user message element
    const userMessageElement = document.createElement("div");
    userMessageElement.classList.add("message", "user");

    // User icon
    const userIcon = document.createElement("div");
    userIcon.classList.add("icon");
    const userImg = document.createElement("img");
    userImg.src = "/static/images/user-icon.png"; // Replace with the correct user icon path
    userImg.alt = "User";
    userIcon.appendChild(userImg);

    const userContent = document.createElement("div");
    userContent.classList.add("content");
    userContent.innerText = userMessage;

    userMessageElement.appendChild(userIcon);
    userMessageElement.appendChild(userContent);
    chatMessages.appendChild(userMessageElement);

    chatInput.value = "";

    // Display the typing indicator
    const typingIndicator = document.createElement("div");
    typingIndicator.classList.add("message", "ai", "typing-indicator");
    const typingIcon = document.createElement("div");
    typingIcon.classList.add("icon");
    const typingImg = document.createElement("img");
    typingImg.src = "/static/images/chatbot-icon.png"; // AI icon
    typingImg.alt = "AI";
    typingIcon.appendChild(typingImg);

    const typingContent = document.createElement("div");
    typingContent.classList.add("content");
    typingContent.innerText = "AI is typing...";

    typingIndicator.appendChild(typingIcon);
    typingIndicator.appendChild(typingContent);
    chatMessages.appendChild(typingIndicator);

    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Send the user's message to the backend
    fetch("/get_response/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: userMessage }),
    })
      .then(response => response.json())
      .then(data => {
        // Remove the typing indicator once the AI response is ready
        typingIndicator.style.display = "none";

        // Add the AI response
        const aiResponseElement = document.createElement("div");
        aiResponseElement.classList.add("message", "ai");

        // AI icon
        const aiIcon = document.createElement("div");
        aiIcon.classList.add("icon");
        const aiImg = document.createElement("img");
        aiImg.src = "/static/images/chatbot-icon.png"; // AI icon
        aiImg.alt = "AI";
        aiIcon.appendChild(aiImg);

        const aiContent = document.createElement("div");
        aiContent.classList.add("content");
        aiContent.innerText = data.answer;

        aiResponseElement.appendChild(aiIcon);
        aiResponseElement.appendChild(aiContent);
        chatMessages.appendChild(aiResponseElement);

        chatMessages.scrollTop = chatMessages.scrollHeight;
      })
      .catch(error => {
        console.error("Error:", error);
        const errorElement = document.createElement("div");
        errorElement.classList.add("message", "ai");

        const errorIcon = document.createElement("div");
        errorIcon.classList.add("icon");
        const errorImg = document.createElement("img");
        errorImg.src = "/static/images/chatbot-icon.png"; // AI icon
        errorImg.alt = "AI";
        errorIcon.appendChild(errorImg);

        const errorContent = document.createElement("div");
        errorContent.classList.add("content");
        errorContent.innerText = "Sorry, something went wrong. Please try again.";

        errorElement.appendChild(errorIcon);
        errorElement.appendChild(errorContent);
        chatMessages.appendChild(errorElement);

        chatMessages.scrollTop = chatMessages.scrollHeight;
      });
  });
});
