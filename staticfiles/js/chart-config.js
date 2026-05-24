/**
 * chart-config.js — Nutriqu Chart.js Global Configuration
 * Daftarkan satu kali di base.html sebelum chart individual di-render.
 * Mengikuti design.md §7.8
 */

(function () {
  'use strict';

  // Tunggu Chart.js tersedia (CDN async)
  function initChartDefaults() {
    if (typeof Chart === 'undefined') {
      return setTimeout(initChartDefaults, 50);
    }

    /* ── Global defaults ── */
    Chart.defaults.font.family  = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif";
    Chart.defaults.font.size    = 12;
    Chart.defaults.color        = '#41454d';  /* --color-muted */
    Chart.defaults.animation    = { duration: 600, easing: 'easeInOutQuart' };
    Chart.defaults.responsive   = true;
    Chart.defaults.maintainAspectRatio = true;

    /* ── Tooltip defaults ── */
    Chart.defaults.plugins.tooltip.backgroundColor  = '#181d26';
    Chart.defaults.plugins.tooltip.titleColor       = '#ffffff';
    Chart.defaults.plugins.tooltip.bodyColor        = '#ffffff';
    Chart.defaults.plugins.tooltip.padding          = 10;
    Chart.defaults.plugins.tooltip.cornerRadius     = 6;
    Chart.defaults.plugins.tooltip.displayColors    = true;
    Chart.defaults.plugins.tooltip.boxPadding       = 3;

    /* ── Legend defaults ── */
    Chart.defaults.plugins.legend.labels.font        = { size: 12, family: "'Inter', sans-serif" };
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
    Chart.defaults.plugins.legend.labels.pointStyleWidth = 8;
    Chart.defaults.plugins.legend.labels.padding       = 16;
  }

  document.addEventListener('DOMContentLoaded', initChartDefaults);

  /* ─────────────────────────────────────────────────────────────
   * Palet warna yang dipakai seluruh grafik Nutriqu
   * ───────────────────────────────────────────────────────────── */
  window.nutriquColors = {
    primary:      '#181d26',   /* --color-primary */
    primaryFade:  'rgba(24, 29, 38, 0.08)',
    primaryBar:   'rgba(24, 29, 38, 0.75)',
    primaryHover: '#333840',
    success:      '#006400',   /* --color-success */
    warning:      '#aa2d00',   /* --color-sig-coral */
    mint:         '#a8d8c4',   /* --color-sig-mint */
    peach:        '#fcab79',   /* --color-sig-peach */
    grid:         '#e0e2e6',   /* --color-surface-strong */
    muted:        '#41454d',   /* --color-muted */
  };

  /* ─────────────────────────────────────────────────────────────
   * Preset: Line Chart (Tren Kalori)
   * Gunakan: nutriquChartPresets.line(ctx, labels, data, tdee?)
   * ───────────────────────────────────────────────────────────── */
  window.nutriquChartPresets = {

    /**
     * Line chart untuk tren kalori harian.
     * @param {HTMLCanvasElement} ctx
     * @param {string[]} labels
     * @param {number[]} energyData
     * @param {number} [tdee=0]  - garis putus-putus target
     * @returns {Chart}
     */
    line: function (ctx, labels, energyData, tdee) {
      var c = window.nutriquColors;
      var datasets = [
        {
          label: 'Energi (kkal)',
          data: energyData,
          borderColor: c.primary,
          backgroundColor: c.primaryFade,
          borderWidth: 2,
          fill: true,
          tension: 0.35,
          pointRadius: 4,
          pointHoverRadius: 6,
          pointBackgroundColor: c.primary,
          pointBorderColor: '#ffffff',
          pointBorderWidth: 2,
        }
      ];

      if (tdee && tdee > 0) {
        datasets.push({
          label: 'Target TDEE',
          data: labels.map(function () { return tdee; }),
          borderColor: c.warning,
          borderWidth: 1.5,
          borderDash: [6, 3],
          pointRadius: 0,
          fill: false,
          tension: 0,
        });
      }

      return new Chart(ctx, {
        type: 'line',
        data: { labels: labels, datasets: datasets },
        options: {
          responsive: true,
          interaction: { mode: 'index', intersect: false },
          plugins: {
            legend: { position: 'bottom' },
            tooltip: { mode: 'index', intersect: false },
          },
          scales: {
            x: {
              grid: { display: false },
              ticks: { color: c.muted, font: { size: 12 } },
              border: { display: false },
            },
            y: {
              beginAtZero: true,
              grid: { color: c.grid, drawBorder: false },
              ticks: { color: c.muted, font: { size: 12 } },
              border: { display: false },
            }
          }
        }
      });
    },

    /**
     * Bar chart untuk laporan mingguan.
     * @param {HTMLCanvasElement} ctx
     * @param {string[]} labels
     * @param {number[]} energyData
     * @param {number} [tdee=0]
     * @returns {Chart}
     */
    bar: function (ctx, labels, energyData, tdee) {
      var c = window.nutriquColors;
      var datasets = [
        {
          label: 'Energi (kkal)',
          data: energyData,
          backgroundColor: c.primaryBar,
          hoverBackgroundColor: c.primaryHover,
          borderRadius: 6,
          borderSkipped: false,
        }
      ];

      if (tdee && tdee > 0) {
        datasets.push({
          label: 'Target TDEE',
          data: labels.map(function () { return tdee; }),
          type: 'line',
          borderColor: c.warning,
          borderWidth: 1.5,
          borderDash: [6, 3],
          pointRadius: 0,
          fill: false,
        });
      }

      return new Chart(ctx, {
        type: 'bar',
        data: { labels: labels, datasets: datasets },
        options: {
          responsive: true,
          plugins: {
            legend: { position: 'bottom' },
            tooltip: { mode: 'index', intersect: false },
          },
          scales: {
            x: {
              grid: { display: false },
              ticks: { color: c.muted, font: { size: 12 } },
              border: { display: false },
            },
            y: {
              beginAtZero: true,
              grid: { color: c.grid },
              ticks: { color: c.muted, font: { size: 12 } },
              border: { display: false },
            }
          }
        }
      });
    },

    /**
     * Donut chart untuk distribusi makronutrien.
     * @param {HTMLCanvasElement} ctx
     * @param {number} carb
     * @param {number} protein
     * @param {number} fat
     * @returns {Chart}
     */
    donut: function (ctx, carb, protein, fat) {
      var c = window.nutriquColors;
      return new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['Karbohidrat', 'Protein', 'Lemak'],
          datasets: [{
            data: [carb, protein, fat],
            backgroundColor: [c.primary, c.mint, c.peach],
            borderWidth: 0,
            hoverOffset: 4,
          }]
        },
        options: {
          cutout: '72%',
          plugins: {
            legend: {
              position: 'bottom',
            },
            tooltip: {
              callbacks: {
                label: function (item) {
                  var total = item.dataset.data.reduce(function (a, b) { return a + b; }, 0);
                  var pct   = total > 0 ? Math.round(item.parsed / total * 100) : 0;
                  return item.label + ': ' + item.parsed.toLocaleString('id-ID') + 'g (' + pct + '%)';
                }
              }
            }
          }
        }
      });
    }
  };

})();
