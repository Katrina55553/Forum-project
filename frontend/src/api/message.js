import client from "./client";

export function sendMessage(receiver, content) {
  return client.post("/messages", { receiver, content });
}

export function getConversations() {
  return client.get("/messages");
}

export function getMessages(username, page = 1, size = 50) {
  return client.get(`/messages/${username}`, { params: { page, size } });
}

export function markMessagesRead(username) {
  return client.put(`/messages/${username}/read`);
}

export function getUnreadMessageCount() {
  return client.get("/messages/unread-count");
}
