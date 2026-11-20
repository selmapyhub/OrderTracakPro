/**
 * OrderTrack Pro - Frontend Logic
 * Interactive stage cycling, Table/Card view toggling, and PWA registration.
 */

document.addEventListener('DOMContentLoaded', function () {
  initViewMode();
  initStageToggles();
  initTooltips();
  initServiceWorker();
});

/* ==========================================================================
   1. Table vs Card View Toggle with LocalStorage Persistence
   ========================================================================== */
function initViewMode() {
  const tableViewBtn = document.getElementById('btn-view-table');
  const cardViewBtn = document.getElementById('btn-view-card');
  const tableViewContainer = document.getElementById('container-view-table');
  const cardViewContainer = document.getElementById('container-view-card');

  if (!tableViewBtn || !cardViewBtn || !tableViewContainer || !cardViewContainer) {
    return;
  }

  function setView(mode, updateUrl = true) {
    if (mode === 'card') {
      tableViewContainer.classList.add('d-none');
      cardViewContainer.classList.remove('d-none');
      cardViewBtn.classList.add('active');
      tableViewBtn.classList.remove('active');
      localStorage.setItem('ordertrack_view_mode', 'card');
    } else {
      cardViewContainer.classList.add('d-none');
      tableViewContainer.classList.remove('d-none');
      tableViewBtn.classList.add('active');
      cardViewBtn.classList.remove('active');
      localStorage.setItem('ordertrack_view_mode', 'table');
    }

    if (updateUrl) {
      const url = new URL(window.location.href);
      url.searchParams.set('view', mode);
      window.history.replaceState({}, '', url.toString());
    }
  }

  tableViewBtn.addEventListener('click', function (e) {
    e.preventDefault();
    setView('table');
  });

  cardViewBtn.addEventListener('click', function (e) {
    e.preventDefault();
    setView('card');
  });

  // Check saved preference or URL param
  const urlParams = new URLSearchParams(window.location.search);
  const urlView = urlParams.get('view');
  const savedView = localStorage.getItem('ordertrack_view_mode');

  if (urlView === 'card' || urlView === 'table') {
    setView(urlView, false);
  } else if (savedView) {
    setView(savedView, false);
  }
}

/* ==========================================================================
   2. Interactive Quick Stage Updater (AJAX)
   ========================================================================== */
function initStageToggles() {
  const stagePills = document.querySelectorAll('.interactive-stage-pill');

  stagePills.forEach(pill => {
    pill.addEventListener('click', async function (e) {
      e.preventDefault();

      const orderId = this.dataset.orderId;
      const stageKey = this.dataset.stageKey;
      const targetStatus = this.dataset.targetStatus || '';

      if (!orderId || !stageKey) return;

      // Visual feedback loading
      const originalHtml = this.innerHTML;
      this.style.opacity = '0.5';

      try {
        const csrfToken = getCookie('csrftoken');
        const response = await fetch(`/order/${orderId}/stage-update/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken,
          },
          body: new URLSearchParams({
            stage: stageKey,
            target_status: targetStatus,
          })
        });

        if (!response.ok) {
          throw new Error('Failed to update stage.');
        }

        const data = await response.json();
        if (data.success) {
          // Update all instances of this stage pill on the page (both table and card views)
          const allPillsForStage = document.querySelectorAll(
            `.interactive-stage-pill[data-order-id="${orderId}"][data-stage-key="${stageKey}"]`
          );

          allPillsForStage.forEach(p => {
            p.classList.remove('status-PENDING', 'status-IN_PROGRESS', 'status-COMPLETED');
            p.classList.add(`status-${data.new_status}`);
            p.setAttribute('title', `${stageKey.toUpperCase()}: ${data.new_label} (Click to advance)`);

            // Icon update
            let iconHtml = '<i class="bi bi-circle"></i>';
            if (data.new_status === 'COMPLETED') {
              iconHtml = '<i class="bi bi-check-circle-fill"></i>';
            } else if (data.new_status === 'IN_PROGRESS') {
              iconHtml = '<i class="bi bi-arrow-repeat spin-icon"></i>';
            }
            p.innerHTML = `${iconHtml} <span>${stageKey.toUpperCase().substring(0, 4)}</span>`;
          });

          // Update Progress Bars for this order
          const progressBars = document.querySelectorAll(`.order-progress-bar-${orderId}`);
          progressBars.forEach(bar => {
            bar.style.width = `${data.progress}%`;
            bar.setAttribute('aria-valuenow', data.progress);
            bar.textContent = `${data.progress}%`;

            // Update color class
            bar.classList.remove('bg-primary', 'bg-warning', 'bg-success', 'bg-danger');
            if (data.progress === 100 || data.order_status === 'COMPLETED') {
              bar.classList.add('bg-success');
            } else if (data.order_status === 'URGENT') {
              bar.classList.add('bg-danger');
            } else if (data.order_status === 'DELAYED') {
              bar.classList.add('bg-warning');
            } else {
              bar.classList.add('bg-primary');
            }
          });

          // Update Status Badge if it changed
          const statusBadges = document.querySelectorAll(`.order-status-badge-${orderId}`);
          statusBadges.forEach(badge => {
            badge.textContent = data.order_status_label;
            badge.className = `badge-status badge-status-${data.order_status.toLowerCase().replace('_', '-')} order-status-badge-${orderId}`;
          });

          showToast(`Order #${data.order_id}: ${stageKey.toUpperCase()} updated to ${data.new_label} (${data.progress}%)`);
        }
      } catch (err) {
        console.error(err);
        showToast('Error updating stage. Please refresh the page.', 'danger');
      } finally {
        this.style.opacity = '1';
      }
    });
  });
}

/* ==========================================================================
   3. Bootstrap Tooltip Initialization
   ========================================================================== */
function initTooltips() {
  if (window.bootstrap && bootstrap.Tooltip) {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl);
    });
  }
}

/* ==========================================================================
   4. Utility: Get CSRF Token from Cookies
   ========================================================================== */
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

/* ==========================================================================
   5. Lightweight Toast Notifications
   ========================================================================== */
function showToast(message, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '1090';
    document.body.appendChild(container);
  }

  const toastEl = document.createElement('div');
  toastEl.className = `toast align-items-center text-white bg-${type === 'danger' ? 'danger' : 'dark'} border-0 show shadow`;
  toastEl.setAttribute('role', 'alert');
  toastEl.setAttribute('aria-live', 'assertive');
  toastEl.setAttribute('aria-atomic', 'true');

  toastEl.innerHTML = `
    <div class="d-flex">
      <div class="toast-body py-2 px-3 small">
        <i class="bi bi-info-circle me-1"></i> ${message}
      </div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>
  `;

  container.appendChild(toastEl);

  setTimeout(() => {
    toastEl.remove();
  }, 3200);
}

/* ==========================================================================
   6. PWA / Service Worker & In-App Installation Prompt
   ========================================================================== */
let deferredPrompt = null;

function initServiceWorker() {
  // Register Service Worker at root scope
  if ('serviceWorker' in navigator && window.location.protocol.startsWith('http')) {
    navigator.serviceWorker.register('/sw.js', { scope: '/' })
      .then(reg => {
        console.log('[OrderTrack PWA] Service Worker registered with root scope:', reg.scope);
      })
      .catch(err => {
        // Fallback to static if needed
        navigator.serviceWorker.register('/static/sw.js').catch(() => {});
      });
  }

  // Handle native install prompt
  const installBtn = document.getElementById('pwa-install-btn');
  const banner = document.getElementById('pwa-install-banner');
  const bannerInstallBtn = document.getElementById('pwa-banner-install-btn');

  window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent standard mini-infobar on mobile
    e.preventDefault();
    deferredPrompt = e;

    // Show Install button in navbar
    if (installBtn) {
      installBtn.classList.remove('d-none');
      installBtn.classList.add('d-flex');
    }

    // Show Mobile installation banner if user hasn't dismissed it
    const bannerDismissed = sessionStorage.getItem('ordertrack_pwa_dismissed');
    if (banner && !bannerDismissed) {
      banner.classList.remove('d-none');
      banner.classList.add('d-flex', 'show');
    }
  });

  async function triggerInstall() {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === 'accepted') {
      showToast('Installing OrderTrack Pro to your home screen...', 'success');
    }
    deferredPrompt = null;
    if (installBtn) installBtn.classList.add('d-none');
    if (banner) banner.classList.add('d-none');
  }

  if (installBtn) {
    installBtn.addEventListener('click', triggerInstall);
  }

  if (bannerInstallBtn) {
    bannerInstallBtn.addEventListener('click', triggerInstall);
  }

  // Listen for successful installation
  window.addEventListener('appinstalled', () => {
    showToast('OrderTrack Pro has been added to your Home Screen! 🎉', 'success');
    if (installBtn) installBtn.classList.add('d-none');
    if (banner) banner.classList.add('d-none');
  });
}
