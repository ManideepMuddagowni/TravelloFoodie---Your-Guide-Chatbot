document.addEventListener("DOMContentLoaded", function () {
  const chatPopupBtn = document.getElementById("chat-popup-btn");
  const chatWidget = document.getElementById("chat-widget");
  const chatMessages = document.getElementById("chat-messages");
  const chatInput = document.getElementById("chat-input");
  const chatSendBtn = document.getElementById("chat-send-btn");
  const chatCloseBtn = document.getElementById("chat-close-btn");

  // List of predefined messages with greetings
  const predefinedMessages = [
    "Hi there! Welcome to TravelloFoodie! Ready to explore?",
    "Hello! Hungry for adventure? Let's discover new cuisines and destinations with TravelloFoodie!",
    "Hi! TravelloFoodie is here to guide your taste buds and travel dreams.",
    "Hello! Exploring new places? Let TravelloFoodie help you plan the perfect trip and meal.",
    "Hi! Looking for amazing food and travel experiences? You're in the right place with TravelloFoodie!",
    "Hello! Travel and food go hand in hand. Let TravelloFoodie help you explore them both!",
    "Hi! Ready to taste the world? Let TravelloFoodie be your guide!",
    "Hello! The best food, the best destinations. Ready for your next adventure with TravelloFoodie?",
    "Hi! Let TravelloFoodie help you find the best culinary spots while traveling. What's your next destination?",
    "Hello! Explore the world, one bite at a time. TravelloFoodie is here to assist!"
  ];

  // Show one predefined message when the page loads
  function displayRandomMessage() {
    const randomMessage = predefinedMessages[Math.floor(Math.random() * predefinedMessages.length)];

    // Create AI message element
    const aiMessageElement = document.createElement("div");
    aiMessageElement.classList.add("message", "ai");

    // AI icon
    const aiIcon = document.createElement("div");
    aiIcon.classList.add("icon");
    const aiImg = document.createElement("img");
    aiImg.src = "/static/images/chatbot-icon.png"; // AI icon
    aiImg.alt = "AI";
    aiIcon.appendChild(aiImg);

    const aiContent = document.createElement("div");
    aiContent.classList.add("content");
    aiContent.innerText = randomMessage;

    aiMessageElement.appendChild(aiIcon);
    aiMessageElement.appendChild(aiContent);
    chatMessages.appendChild(aiMessageElement);
  }

  // Display one random message when the page loads
  displayRandomMessage();

  // Open the chat widget
  chatPopupBtn.addEventListener("click", () => {
    chatWidget.style.display = "flex";
  });

  // Close the chat widget
  chatCloseBtn.addEventListener("click", () => {
    chatWidget.style.display = "none";
  });

  // Function to handle sending a message
  function sendMessage() {
    const userMessage = chatInput.value.trim();
    if (!userMessage) return;

    console.log("User Message:", userMessage); // Debug log

    // Create the user message element
    const userMessageElement = document.createElement("div");
    userMessageElement.classList.add("message", "user");

    // User icon
    const userIcon = document.createElement("div");
    userIcon.classList.add("icon");
    const userImg = document.createElement("img");
    userImg.src = "/static/images/user-icon.png"; // Correct path to user icon
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
    typingContent.innerText = "typing...";

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
        typingIndicator.remove();

        // Add the AI response
        const aiResponseElement = document.createElement("div");
        aiResponseElement.classList.add("message", "ai");

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

        // Add an error message
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
  }

  // Add event listener to "Send" button
  chatSendBtn.addEventListener("click", sendMessage);

  // Add event listener for "Enter" key press
  chatInput.addEventListener("keydown", function (event) {
    console.log("Key pressed:", event.key); // Debugging key press
    if (event.key === "Enter") {
      event.preventDefault(); // Prevent default behavior
      sendMessage();
    }
  });
});