// const API_BASE_URL = "http://localhost:8000"; // Adjust if deployed

// // DOM Elements
// const messagesDiv = document.getElementById("messages");
// const messageInput = document.getElementById("message");
// const sendButton = document.getElementById("send");

// // Chat variables
// const chatId = "your_chat_id"; // Replace with an actual chat ID from the backend
// const senderId = "user1"; // Replace with a dynamic user ID (e.g., logged-in user)

// // Fetch all messages and display them
// async function fetchMessages() {
//   try {
//     const response = await fetch(`${API_BASE_URL}/get_messages/${chatId}`);
//     if (!response.ok) throw new Error("Failed to fetch messages");

//     const messages = await response.json();
//     messagesDiv.innerHTML = ""; // Clear previous messages

//     messages.forEach((msg) => {
//       const messageElement = document.createElement("p");
//       messageElement.textContent = `${msg.senderId}: ${msg.text}`;
//       messagesDiv.appendChild(messageElement);
//     });

//     // Scroll to the bottom
//     messagesDiv.scrollTop = messagesDiv.scrollHeight;
//   } catch (error) {
//     console.error("Error fetching messages:", error);
//   }
// }

// // Send a new message
// async function sendMessage() {
//   const text = messageInput.value.trim();
//   if (!text) return;

//   try {
//     const response = await fetch(`${API_BASE_URL}/send_message/`, {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify({
//         chat_id: chatId,
//         sender_id: senderId,
//         text: text,
//       }),
//     });

//     if (!response.ok) throw new Error("Failed to send message");

//     messageInput.value = ""; // Clear input field
//     await fetchMessages(); // Refresh messages
//   } catch (error) {
//     console.error("Error sending message:", error);
//   }
// }

// // Event listeners
// sendButton.addEventListener("click", sendMessage);
// messageInput.addEventListener("keypress", (e) => {
//   if (e.key === "Enter") sendMessage();
// });

// // Fetch messages on page load
// fetchMessages();
 