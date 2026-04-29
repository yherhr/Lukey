/**
 * Luke Davis Mechanical — Cart Helper
 * Shared across all part pages and cart.html
 */
const Cart = {
  key: 'ldm_cart',
  get() {
    try { return JSON.parse(localStorage.getItem(this.key)) || []; }
    catch(e) { return []; }
  },
  save(items) { localStorage.setItem(this.key, JSON.stringify(items)); },
  add(id, qty = 1) {
    const items = this.get();
    const idx = items.findIndex(i => i.id === id);
    if (idx > -1) { items[idx].qty += qty; } else { items.push({ id, qty }); }
    this.save(items);
    this.updateBadge();
  },
  remove(id) {
    this.save(this.get().filter(i => i.id !== id));
    this.updateBadge();
  },
  setQty(id, qty) {
    const items = this.get();
    const idx = items.findIndex(i => i.id === id);
    if (idx > -1) { if (qty < 1) items.splice(idx, 1); else items[idx].qty = qty; }
    this.save(items);
    this.updateBadge();
  },
  count() { return this.get().reduce((s, i) => s + i.qty, 0); },
  clear() { localStorage.removeItem(this.key); this.updateBadge(); },
  updateBadge() {
    const cnt = this.count();
    document.querySelectorAll('.cart-badge').forEach(el => {
      el.textContent = cnt;
      el.style.display = cnt > 0 ? 'flex' : 'none';
    });
  }
};
