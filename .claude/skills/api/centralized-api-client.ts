/**
 * Centralized API Client for Next.js
 * Automatically attaches Authorization header with JWT token
 */

import { auth } from "@/lib/auth-client"; // Adjust import path as needed

interface ApiOptions extends RequestInit {
  token?: string;
}

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = process.env.NEXT_PUBLIC_API_BASE_URL || "") {
    this.baseUrl = baseUrl;
  }

  /**
   * Makes an API request with automatic token attachment
   */
  async request<T>(endpoint: string, options: ApiOptions = {}): Promise<T> {
    // Get token from session or options
    let token = options.token;
    if (!token) {
      // Attempt to get token from auth session
      try {
        const session = await auth.api.getSession();
        token = session?.token;
      } catch (error) {
        console.warn("Could not get session for API request:", error);
      }
    }

    // Prepare headers
    const headers = new Headers(options.headers);
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }
    headers.set("Content-Type", "application/json");

    // Make the request
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return response.json() as Promise<T>;
  }

  /**
   * GET request helper
   */
  async get<T>(endpoint: string, options?: ApiOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "GET" });
  }

  /**
   * POST request helper
   */
  async post<T>(endpoint: string, data: any, options?: ApiOptions): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  /**
   * PUT request helper
   */
  async put<T>(endpoint: string, data: any, options?: ApiOptions): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  /**
   * DELETE request helper
   */
  async delete<T>(endpoint: string, options?: ApiOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "DELETE" });
  }
}

// Export a singleton instance
export const apiClient = new ApiClient();

// Usage example:
// const todos = await apiClient.get<Todo[]>('/api/todos');
// const newTodo = await apiClient.post<Todo>('/api/todos', { title: 'New task' });