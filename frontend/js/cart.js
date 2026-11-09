const STORAGE_KEY = "repuestos_bogota_cart_v1";
const currency = new Intl.NumberFormat("es-CO", {
  style: "currency",
  currency: "COP",
  maximumFractionDigits: 0,
});

export class CartController {
  constructor(api, onRequireLogin, onOrderCreated) {
    this.api = api;
    this.onRequireLogin = onRequireLogin;
    this.onOrderCreated = onOrderCreated;
    this.user = null;
    this.items = this.readItems();
    this.panel = document.querySelector("#cart-panel");
    this.list = document.querySelector("#cart-items");
    this.emptyMessage = document.querySelector("#cart-empty");
    this.count = document.querySelector("#cart-count");
    this.subtotal = document.querySelector("#cart-subtotal");
    this.authHint = document.querySelector("#cart-auth-hint");
    this.loginButton = document.querySelector("#cart-login-button");
    this.checkoutForm = document.querySelector("#checkout-form");
    this.checkoutMessage = document.querySelector("#checkout-message");
    this.placeOrderButton = document.querySelector("#place-order");

    document.querySelector("#cart-open").addEventListener("click", () => this.toggle());
    document.querySelector("#cart-close").addEventListener("click", () => this.toggle(false));
    this.loginButton.addEventListener("click", () => this.onRequireLogin());
    this.checkoutForm.addEventListener("submit", (event) => this.checkout(event));
    this.setUser(null);
    this.render();
  }

  readItems() {
    try {
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
      if (!Array.isArray(saved)) return [];
      return saved
        .filter((item) => item && typeof item === "object"
          && Number.isInteger(Number(item.productId)) && Number(item.productId) > 0
          && Number.isInteger(Number(item.quantity)) && Number(item.quantity) > 0)
        .map((item) => ({
          productId: Number(item.productId),
          name: String(item.name || "Producto").slice(0, 160),
          price: Number.isFinite(Number(item.price)) && Number(item.price) >= 0 ? String(item.price) : "0",
          stock: Number.isInteger(Number(item.stock)) && Number(item.stock) >= 0 ? Number(item.stock) : 0,
          quantity: Math.min(Number(item.quantity), 99),
        }));
    } catch {
      return [];
    }
  }

  save() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(this.items));
  }

  setUser(user) {
    this.user = user;
    const isCustomer = user?.role === "cliente";
    this.checkoutForm.hidden = !isCustomer;
    this.loginButton.hidden = Boolean(user);
    if (!user) this.authHint.textContent = "Ingresa o crea una cuenta para confirmar tu pedido.";
    else if (!isCustomer) this.authHint.textContent = "La compra está disponible para cuentas de cliente.";
    else this.authHint.textContent = "Confirma los datos de entrega antes de continuar.";

    if (isCustomer) {
      this.checkoutForm.elements.delivery_email.value = user.email || "";
      this.checkoutForm.elements.delivery_phone.value = user.phone || "";
      this.checkoutForm.elements.delivery_address.value = user.address || "";
    } else if (!user) {
      this.checkoutForm.reset();
    }
    this.render();
  }

  toggle(forceOpen) {
    const shouldOpen = forceOpen ?? this.panel.hidden;
    this.panel.hidden = !shouldOpen;
    document.querySelector("#cart-open").setAttribute("aria-expanded", String(shouldOpen));
    if (shouldOpen) this.panel.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  add(product) {
    const existing = this.items.find((item) => item.productId === product.id);
    if (existing) {
      if (existing.quantity >= product.stock) {
        this.showCheckoutMessage(`Solo hay ${product.stock} unidades disponibles.`, "error");
        this.toggle(true);
        return;
      }
      existing.quantity += 1;
      existing.stock = product.stock;
      existing.price = product.price;
    } else {
      this.items.push({
        productId: product.id,
        name: product.name,
        price: product.price,
        stock: product.stock,
        quantity: 1,
      });
    }
    this.save();
    this.render();
    this.toggle(true);
    this.showCheckoutMessage(`${product.name} se agregó al carrito.`, "success");
  }

  changeQuantity(productId, delta) {
    const item = this.items.find((entry) => entry.productId === productId);
    if (!item) return;
    const nextQuantity = item.quantity + delta;
    if (nextQuantity <= 0) this.items = this.items.filter((entry) => entry.productId !== productId);
    else if (nextQuantity <= item.stock) item.quantity = nextQuantity;
    else this.showCheckoutMessage(`Solo hay ${item.stock} unidades disponibles.`, "error");
    this.save();
    this.render();
  }

  remove(productId) {
    this.items = this.items.filter((item) => item.productId !== productId);
    this.save();
    this.render();
  }

  render() {
    this.list.replaceChildren();
    this.emptyMessage.hidden = this.items.length > 0;
    const units = this.items.reduce((sum, item) => sum + item.quantity, 0);
    this.count.textContent = String(units);
    const subtotalCents = this.items.reduce(
      (sum, item) => sum + Math.round(Number(item.price) * 100) * item.quantity,
      0,
    );
    this.subtotal.textContent = currency.format(subtotalCents / 100);
    this.placeOrderButton.disabled = this.items.length === 0;

    for (const item of this.items) {
      const row = document.createElement("article");
      row.className = "cart-item";
      const summary = document.createElement("div");
      const title = document.createElement("h3");
      title.textContent = item.name;
      const unitPrice = document.createElement("p");
      unitPrice.textContent = `${currency.format(Number(item.price))} por unidad`;
      summary.append(title, unitPrice);

      const total = document.createElement("strong");
      total.className = "cart-item-price";
      total.textContent = currency.format((Math.round(Number(item.price) * 100) * item.quantity) / 100);

      const quantity = document.createElement("div");
      quantity.className = "quantity-control";
      const decrease = document.createElement("button");
      decrease.type = "button";
      decrease.textContent = "−";
      decrease.setAttribute("aria-label", `Quitar una unidad de ${item.name}`);
      decrease.addEventListener("click", () => this.changeQuantity(item.productId, -1));
      const amount = document.createElement("span");
      amount.textContent = String(item.quantity);
      const increase = document.createElement("button");
      increase.type = "button";
      increase.textContent = "+";
      increase.setAttribute("aria-label", `Agregar una unidad de ${item.name}`);
      increase.addEventListener("click", () => this.changeQuantity(item.productId, 1));
      const remove = document.createElement("button");
      remove.type = "button";
      remove.textContent = "×";
      remove.setAttribute("aria-label", `Eliminar ${item.name} del carrito`);
      remove.addEventListener("click", () => this.remove(item.productId));
      quantity.append(decrease, amount, increase, remove);
      row.append(summary, total, quantity);
      this.list.append(row);
    }
  }

  async checkout(event) {
    event.preventDefault();
    if (!this.user || this.user.role !== "cliente" || !this.items.length) return;
    const form = this.checkoutForm;
    const body = {
      items: this.items.map((item) => ({ product_id: item.productId, quantity: item.quantity })),
      payment_method: form.elements.payment_method.value,
      delivery_email: form.elements.delivery_email.value.trim(),
      delivery_phone: form.elements.delivery_phone.value.trim(),
      delivery_address: form.elements.delivery_address.value.trim(),
    };
    this.placeOrderButton.disabled = true;
    this.showCheckoutMessage("Validando existencias y registrando el pedido…");
    try {
      const order = await this.api.request("/api/orders", { method: "POST", body });
      this.items = [];
      this.save();
      this.render();
      const paymentMessage = order.payment_method === "contraentrega"
        ? "El pago queda pendiente para la entrega."
        : "La transferencia es manual y queda pendiente de confirmación; coordínala con la tienda.";
      this.showCheckoutMessage(
        `Pedido #${order.id} registrado. Total de productos: ${currency.format(Number(order.total))}. ${paymentMessage}`,
        "success",
      );
      await this.onOrderCreated();
    } catch (error) {
      this.showCheckoutMessage(error.message, "error");
      await this.onOrderCreated();
    } finally {
      this.placeOrderButton.disabled = this.items.length === 0;
    }
  }

  showCheckoutMessage(message, type = "") {
    this.checkoutMessage.textContent = message;
    this.checkoutMessage.className = `form-message ${type}`.trim();
  }
}
