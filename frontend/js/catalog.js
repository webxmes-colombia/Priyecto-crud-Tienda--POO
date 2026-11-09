const currency = new Intl.NumberFormat("es-CO", {
  style: "currency",
  currency: "COP",
  maximumFractionDigits: 0,
});

function option(label, value = "") {
  const item = document.createElement("option");
  item.value = value;
  item.textContent = label;
  return item;
}

export class CatalogController {
  constructor(api, onAddToCart) {
    this.api = api;
    this.onAddToCart = onAddToCart;
    this.grid = document.querySelector("#product-grid");
    this.message = document.querySelector("#catalog-message");
    this.count = document.querySelector("#catalog-count");
    this.search = document.querySelector("#search-filter");
    this.category = document.querySelector("#category-filter");
    this.brand = document.querySelector("#brand-filter");
    this.searchTimer = null;
  }

  async init() {
    this.search.addEventListener("input", () => {
      clearTimeout(this.searchTimer);
      this.searchTimer = setTimeout(() => this.load(), 250);
    });
    this.category.addEventListener("change", () => this.load());
    this.brand.addEventListener("change", () => this.load());
    try {
      const [categories, brands] = await Promise.all([
        this.api.request("/api/catalog/categories"),
        this.api.request("/api/catalog/brands"),
      ]);
      this.fillOptions(this.category, categories, "Todas");
      this.fillOptions(this.brand, brands, "Todas");
      await this.load();
    } catch (error) {
      this.showMessage(error.message, "error");
    }
  }

  fillOptions(select, items, firstLabel) {
    select.replaceChildren(option(firstLabel));
    for (const item of items) select.append(option(item.name, item.id));
  }

  async refreshBrands() {
    const selected = this.brand.value;
    const brands = await this.api.request("/api/catalog/brands");
    this.fillOptions(this.brand, brands, "Todas");
    if (brands.some((brand) => String(brand.id) === selected)) this.brand.value = selected;
  }

  async load() {
    this.showMessage("Cargando productos…");
    try {
      const products = await this.api.request("/api/catalog/products", {
        query: {
          search: this.search.value.trim(),
          category_id: this.category.value,
          brand_id: this.brand.value,
          limit: 100,
        },
      });
      this.render(products);
      this.count.textContent = `${products.length} ${products.length === 1 ? "producto" : "productos"}`;
      this.showMessage(products.length ? "" : "No encontramos productos con esos filtros.");
    } catch (error) {
      this.grid.replaceChildren();
      this.count.textContent = "";
      this.showMessage(error.message, "error");
    }
  }

  render(products) {
    this.grid.replaceChildren();
    for (const product of products) {
      const card = document.createElement("article");
      card.className = "product-card";
      const art = document.createElement("div");
      art.className = "product-art";
      art.setAttribute("aria-hidden", "true");
      art.textContent = product.name.slice(0, 2).toUpperCase();

      const info = document.createElement("div");
      info.className = "product-info";
      const category = document.createElement("span");
      category.className = "product-category";
      category.textContent = `${product.category_name} · ${product.brand_name}`;
      const title = document.createElement("h3");
      title.textContent = product.name;
      const description = document.createElement("p");
      description.textContent = product.description || "Repuesto disponible en nuestra tienda.";
      const meta = document.createElement("div");
      meta.className = "product-meta";
      const price = document.createElement("strong");
      price.className = "product-price";
      price.textContent = currency.format(Number(product.price));
      const stock = document.createElement("span");
      stock.className = `stock-label${product.stock === 0 ? " out" : ""}`;
      stock.textContent = product.stock > 0 ? `${product.stock} disponibles` : "Agotado";
      const addButton = document.createElement("button");
      addButton.className = "button button-secondary";
      addButton.type = "button";
      addButton.textContent = product.stock > 0 ? "Agregar" : "Agotado";
      addButton.disabled = product.stock <= 0;
      addButton.addEventListener("click", () => this.onAddToCart(product));
      meta.append(price, stock, addButton);
      info.append(category, title, description, meta);
      card.append(art, info);
      this.grid.append(card);
    }
  }

  showMessage(text, type = "") {
    this.message.textContent = text;
    this.message.className = `form-message ${type}`.trim();
  }
}
