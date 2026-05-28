import client from "./client";

export function getTags() {
  return client.get("/tags");
}
