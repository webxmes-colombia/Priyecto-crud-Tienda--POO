const currency = new Intl.NumberFormat("es-CO", {
  style: "currency",
  currency: "COP",
  maximumFractionDigits: 0,
});

function createOption(label, value = "") {
  const item = document.createElement("option");
  item.value = value;
  item.textContent = label;
  return item;
}

function addCell(row, text) {
  const cell = document.createElement("td");
  cell.textContent = text;
  row.append(cell);
  return cell;
}

export class AdminController {
  constructor(api, onProductsChanged, onBrandsChanged) {
    this.api = api;
    this.onProductsChanged = onProductsChanged;
    this.onBrandsChanged = onBrandsChanged;
    this.panel = document.querySelector("#admin-panel");
    this.summary = document.querySelector("#dashboard-summary");
    this.message = document.querySelector("#admin-message");
    this.form = document.querySelector("#product-form");
    this.brandForm = document.querySelector("#brand-form");
    this.brandMessage = document.querySelector("#brand-message");
    this.formTitle = document.querySelector("#product-form-title");
    this.list = document.querySelector("#admin-product-list");
    this.includeInactive = document.querySelector("#show-inactive");
    this.cancelEdit = document.querySelector("#cancel-edit");
    this.role = null;
    this.form.addEventListener("submit", (event) => this.saveProduct(event));
    this.brandForm.addEventListener("submit", (event) => this.saveBrand(event));
    this.includeInactive.addEventListener("change", () => this.loadProducts());
    this.cancelEdit.addEventListener("click", () => this.resetForm());
    document.querySelector("#refresh-admin").addEventListener("click", () => this.refresh());
  }

  async setUser(user) {
    this.role = user?.role || null;
    const canManage = ["vendedor", "administrador", "superusuario"].includes(this.role);
    this.panel.hidden = !canManage;
    if (!canManage) return;

    await this.loadOptions();
    await this.refresh();
  }

  async refresh() {
    await Promise.all([this.loadSummary(), this.loadProducts()]);
  }

  async loadSummary() {
    const canSeeSummary = ["administrador", "superusuario"].includes(this.role);
    this.summary.hidden = !canSeeSummary;
    if (!canSeeSummary) return;
    try {
      const values = await this.api.request("/api/admin/dashboard/summary");
      const cards = [
        ["Productos activos", values.products_active],
        ["Stock bajo (5 o menos)", values.products_low_stock],
        ["Clientes", values.customers_total],
        ["Pedidos por atender", values.orders_pending],
        ["Productos totales", values.products_total],
        ["Pedidos", values.orders_total],
        ["Promociones activas", values.promotions_active],
      ];
      this.summary.replaceChildren();
      for (const [label, value] of cards) {
        const card = document.createElement("article");
        card.className = "summary-card";
        const name = document.createElement("span");
        name.textContent = label;
        const number = document.createElement("strong");
        number.textContent = value;
        card.append(name, number);
        this.summary.append(card);
      }
    } catch (error) {
      this.showMessage(`No se pudo cargar el resumen: ${error.message}`, "error");
    }
  }

  async loadOptions() {
    const selectedCategory = this.form.elements.category_id.value;
    const selectedBrand = this.form.elements.brand_id.value;
    const [categories, brands] = await Promise.all([
      this.api.request("/api/catalog/categories"),
      this.api.request("/api/catalog/brands"),
    ]);
    const categorySelect = this.form.elements.category_id;
    const brandSelect = this.form.elements.brand_id;
    categorySelect.replaceChildren(createOption("Selecciona una categoría"));
    brandSelect.replaceChildren(createOption("Selecciona una marca"));
    for (const category of categories) categorySelect.append(createOption(category.name, category.id));
    for (const brand of brands) brandSelect.append(createOption(brand.name, brand.id));
    categorySelect.value = selectedCategory;
    brandSelect.value = selectedBrand;
  }

  async saveBrand(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const payload = {
      name: form.elements.name.value.trim(),
      country_of_origin: form.elements.country_of_origin.value.trim() || null,
    };
    try {
      await this.api.request("/api/admin/brands", { method: "POST", body: payload });
      form.reset();
      this.brandMessage.textContent = "Marca creada y agregada a los selectores.";
      this.brandMessage.className = "form-message success";
      await this.loadOptions();
      await this.onBrandsChanged();
    } catch (error) {
      this.brandMessage.textContent = error.message;
      this.brandMessage.className = "form-message error";
    }
  }

  async loadProducts() {
    try {
      const products = await this.api.request("/api/admin/products", {
        query: { include_inactive: this.includeInactive.checked, limit: 100 },
      });
      this.renderProducts(products);
    } catch (error) {
      this.showMessage(`No se pudo cargar el inventario: ${error.message}`, "error");
    }
  }

  renderProducts(products) {
    this.list.replaceChildren();
    for (const product of products) {
      const row = document.createElement("tr");
      const nameCell = addCell(row, product.name);
      nameCell.title = `${product.category_name} · ${product.brand_name}`;
      addCell(row, currency.format(Number(product.price)));
      addCell(row, String(product.stock));
      addCell(row, product.active ? "Activo" : "Inactivo");
      const actions = document.createElement("td");
      const edit = document.createElement("button");
      edit.className = "button button-secondary";
      edit.type = "button";
      edit.textContent = "Editar";
      edit.addEventListener("click", () => this.editProduct(product));
      actions.append(edit);
      const activation = document.createElement("button");
      activation.className = `button ${product.active ? "button-danger" : "button-secondary"}`;
      activation.type = "button";
      activation.textContent = product.active ? "Desactivar" : "Reactivar";
      activation.addEventListener("click", () => this.setActive(product));
      actions.append(activation);
      row.append(actions);
      this.list.append(row);
    }
    if (!products.length) {
      const row = document.createElement("tr");
      const cell = addCell(row, "No hay productos para mostrar.");
      cell.colSpan = 5;
      this.list.append(row);
    }
  }

  editProduct(product) {
    this.form.elements.product_id.value = product.id;
    this.form.elements.name.value = product.name;
    this.form.elements.description.value = product.description || "";
    this.form.elements.price.value = product.price;
    this.form.elements.stock.value = product.stock;
    this.form.elements.category_id.value = product.category_id;
    this.form.elements.brand_id.value = product.brand_id;
    this.formTitle.textContent = "Editar producto";
    this.cancelEdit.hidden = false;
    this.form.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  async saveProduct(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const productId = form.elements.product_id.value;
    const data = {
      name: form.elements.name.value.trim(),
      description: form.elements.description.value.trim() || null,
      price: form.elements.price.value,
      stock: Number(form.elements.stock.value),
      category_id: Number(form.elements.category_id.value),
      brand_id: Number(form.elements.brand_id.value),
    };
    try {
      await this.api.request(productId ? `/api/admin/products/${productId}` : "/api/admin/products", {
        method: productId ? "PUT" : "POST",
        body: data,
      });
      this.showMessage(productId ? "Producto actualizado." : "Producto creado.", "success");
      this.resetForm();
      await this.refresh();
      this.onProductsChanged();
    } catch (error) {
      this.showMessage(error.message, "error");
    }
  }

  async setActive(product) {
    const action = product.active ? "desactivar" : "reactivar";
    if (!window.confirm(`¿Quieres ${action} “${product.name}”?`)) return;
    try {
      await this.api.request(
        product.active ? `/api/admin/products/${product.id}` : `/api/admin/products/${product.id}/activate`,
        { method: product.active ? "DELETE" : "PATCH" },
      );
      this.showMessage(product.active ? "Producto desactivado." : "Producto reactivado.", "success");
      await this.refresh();
      this.onProductsChanged();
    } catch (error) {
      this.showMessage(error.message, "error");
    }
  }

  resetForm() {
    this.form.reset();
    this.form.elements.product_id.value = "";
    this.formTitle.textContent = "Crear producto";
    this.cancelEdit.hidden = true;
  }

  showMessage(text, type = "") {
    this.message.textContent = text;
    this.message.className = `form-message ${type}`.trim();
  }
}
