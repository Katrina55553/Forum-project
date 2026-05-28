import client from "./client";

export function uploadAvatar(file) {
  const formData = new FormData();
  formData.append("file", file);
  return client.post("/upload/avatar", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
}
