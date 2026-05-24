/**
 * main.js — Nutriqu global JS utilities
 * Micro-interactions, UX helpers, HTMX event hooks
 */

(function () {
  'use strict';

  /* ─────────────────────────────────────────────────────────────
   * 1. Flash message auto-dismiss
   * ───────────────────────────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', function () {
    var messages = document.querySelectorAll('#messages [x-data]');
    messages.forEach(function (el) {
      setTimeout(function () {
        // Trigger Alpine x-show = false setelah 5 detik
        el.dispatchEvent(new CustomEvent('auto-dismiss'));
      }, 5000);
    });
  });

  /* ─────────────────────────────────────────────────────────────
   * 2. HTMX: fade-in pada elemen baru setelah swap
   * ───────────────────────────────────────────────────────────── */
  document.addEventListener('htmx:afterSwap', function (evt) {
    var target = evt.detail.target;
    if (!target) return;
    target.classList.add('animate-fade-in');
    target.addEventListener('animationend', function () {
      target.classList.remove('animate-fade-in');
    }, { once: true });
  });

  /* ─────────────────────────────────────────────────────────────
   * 3. HTMX: scroll ke atas setelah form submit sukses
   * ───────────────────────────────────────────────────────────── */
  document.addEventListener('htmx:afterRequest', function (evt) {
    if (evt.detail.successful && evt.detail.requestConfig.verb === 'post') {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  });

  /* ─────────────────────────────────────────────────────────────
   * 4. Input: format angka Indonesia (titik = ribuan, koma = desimal)
   *    Hanya tampilan — nilai tersimpan tetap float standar
   * ───────────────────────────────────────────────────────────── */
  window.formatIndoNumber = function (value, decimals) {
    if (value === null || value === undefined || value === '') return '—';
    var num = parseFloat(value);
    if (isNaN(num)) return value;
    return num.toLocaleString('id-ID', {
      minimumFractionDigits: decimals !== undefined ? decimals : 1,
      maximumFractionDigits: decimals !== undefined ? decimals : 1,
    });
  };

  /* ─────────────────────────────────────────────────────────────
   * 5. Progress bar: set width setelah DOM siap (untuk animasi)
   * ───────────────────────────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-progress]').forEach(function (el) {
      var pct = Math.min(parseFloat(el.dataset.progress) || 0, 100);
      // Tunda agar browser sempat render transition
      requestAnimationFrame(function () {
        el.style.width = pct + '%';
      });
    });
  });

  /* ─────────────────────────────────────────────────────────────
   * 6. Active nav item highlight — tambahan keamanan bila Alpine
   *    tidak berhasil meng-highlight via template tag
   * ───────────────────────────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', function () {
    var currentPath = window.location.pathname;
    document.querySelectorAll('nav a[href]').forEach(function (link) {
      var href = link.getAttribute('href');
      if (href && href !== '/' && currentPath.startsWith(href)) {
        link.classList.add('text-ink', 'font-medium');
      }
    });
  });

  /* ─────────────────────────────────────────────────────────────
   * 7. Search results: tutup bila klik di luar
   * ───────────────────────────────────────────────────────────── */
  document.addEventListener('click', function (e) {
    var searchResults = document.getElementById('search-results');
    var searchInput   = document.getElementById('food-search-input');
    if (!searchResults) return;
    if (!searchResults.contains(e.target) && e.target !== searchInput) {
      searchResults.innerHTML = '';
    }
  });

  /* ─────────────────────────────────────────────────────────────
   * 8. HTMX: tambah class fade-out sebelum entry dihapus
   * ───────────────────────────────────────────────────────────── */
  document.addEventListener('htmx:beforeSwap', function (evt) {
    if (evt.detail.requestConfig.verb === 'delete') {
      var target = evt.detail.target;
      if (target) {
        target.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
        target.style.opacity    = '0';
        target.style.transform  = 'translateX(-8px)';
      }
    }
  });

})();
