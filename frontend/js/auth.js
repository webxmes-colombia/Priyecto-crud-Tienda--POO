export class AuthController {
  constructor(api, onUserChange) {
    this.api = api;
    this.onUserChange = onUserChange;
    this.user = null;
  }

  async restore() {
    if (!this.api.accessToken) return;
    try {
      this.user = await this.api.request("/api/auth/me");
      this.onUserChange(this.user);
    } catch {
      this.logout();
    }
  }

  async login(email, password) {
    const result = await this.api.request("/api/auth/login", {
      method: "POST",
      body: { email, password },
    });
    this.api.setAccessToken(result.access_token);
    this.user = result.user;
    this.onUserChange(this.user);
    return this.user;
  }

  async register(customer) {
    const result = await this.api.request("/api/auth/register", {
      method: "POST",
      body: customer,
    });
    this.api.setAccessToken(result.access_token);
    this.user = result.user;
    this.onUserChange(this.user);
    return this.user;
  }

  logout() {
    this.api.setAccessToken(null);
    this.user = null;
    this.onUserChange(null);
  }
}
