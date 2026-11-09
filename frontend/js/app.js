import { AdminController } from "./admin.js";
import { AuthController } from "./auth.js";
import { StoreApi } from "./api.js";
import { CatalogController } from "./catalog.js";
import { CartController } from "./cart.js";

const api = new StoreApi();
let catalog;
let admin;
let cart;
const authMessage = document.querySelector("#auth-message");

function setAuthMessage(message, type = "") {
  authMessage.textContent = message;
  authMessage.className = `form-message ${type}`.trim();
}

function onUserChange(user) {
  const authSection = document.querySelector("#auth-section");
  const accountSummary = document.querySelector("#account-summary");
  authSection.hidden = Boolean(user);
  accountSummary.hidden = !user;
  if (user) {
    document.querySelector("#account-label").textContent = `${user.name || user.email} · ${user.role}`;
    setAuthMessage("");
  }
  cart.setUser(user);
  admin.setUser(user).catch((error) => admin.showMessage(error.message, "error"));
}

const auth = new AuthController(api, onUserChange);
catalog = new CatalogController(api, (product) => cart.add(product));
admin = new AdminController(api, () => catalog.load(), () => catalog.refreshBrands());
cart = new CartController(
  api,
  () => {
    cart.toggle(false);
    document.querySelector("#auth-section").hidden = false;
    document.querySelector("#show-login").click();
    document.querySelector("#auth-section").scrollIntoView({ behavior: "smooth", block: "center" });
  },
  async () => {
    await catalog.load();
    if (admin.role) await admin.refresh();
  },
);

document.querySelector("#show-login").addEventListener("click", () => {
  document.querySelector("#login-form").hidden = false;
  document.querySelector("#register-form").hidden = true;
  document.querySelector("#show-login").classList.add("active");
  document.querySelector("#show-register").classList.remove("active");
  document.querySelector("#show-login").setAttribute("aria-selected", "true");
  document.querySelector("#show-register").setAttribute("aria-selected", "false");
  setAuthMessage("");
});

document.querySelector("#show-register").addEventListener("click", () => {
  document.querySelector("#login-form").hidden = true;
  document.querySelector("#register-form").hidden = false;
  document.querySelector("#show-register").classList.add("active");
  document.querySelector("#show-login").classList.remove("active");
  document.querySelector("#show-register").setAttribute("aria-selected", "true");
  document.querySelector("#show-login").setAttribute("aria-selected", "false");
  setAuthMessage("");
});

document.querySelector("#login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  try {
    await auth.login(form.elements.email.value.trim(), form.elements.password.value);
    form.reset();
  } catch (error) {
    setAuthMessage(error.message, "error");
  }
});

document.querySelector("#register-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const data = Object.fromEntries(new FormData(form));
  data.email = data.email.trim();
  try {
    await auth.register(data);
    form.reset();
  } catch (error) {
    setAuthMessage(error.message, "error");
  }
});

document.querySelector("#logout-button").addEventListener("click", () => {
  auth.logout();
});

catalog.init();
auth.restore();
