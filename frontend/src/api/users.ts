import { apiRequest } from "./client";
import { RegisterUserPayload } from "../types/vocabulary";

export function registerUser(payload: RegisterUserPayload): Promise<void> {
  return apiRequest<void>("/users/register", {
    method: "POST",
    body: JSON.stringify(payload),
    errorMessage: "Could not register user.",
  });
}
