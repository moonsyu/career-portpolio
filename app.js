const dialog = document.querySelector('.image-dialog');
const dialogImage = dialog.querySelector('img');
const viewport = dialog.querySelector('.dialog-viewport');
let zoom = 1;
let pan = { x: 0, y: 0 };
let drag = null;

function renderImage() {
  dialogImage.style.transform = `translate(-50%, -50%) translate(${pan.x}px, ${pan.y}px) scale(${zoom})`;
}
function fitImage() {
  if (!dialog.open || !dialogImage.naturalWidth) return;
  const ratio = Math.min((viewport.clientWidth - 32) / dialogImage.naturalWidth,
    (viewport.clientHeight - 32) / dialogImage.naturalHeight, 1);
  dialogImage.style.width = `${dialogImage.naturalWidth * ratio}px`;
  zoom = 1; pan = { x: 0, y: 0 }; renderImage();
}
function changeZoom(next, point = { x: 0, y: 0 }) {
  const bounded = Math.min(6, Math.max(0.5, next));
  const factor = bounded / zoom;
  pan = { x: point.x - (point.x - pan.x) * factor, y: point.y - (point.y - pan.y) * factor };
  zoom = bounded; renderImage();
}
dialogImage.addEventListener('load', fitImage);
document.querySelectorAll('[data-enlarge]').forEach(button => {
  button.addEventListener('click', () => {
    const image = button.querySelector('img');
    dialogImage.src = image.currentSrc || image.src;
    dialogImage.alt = image.alt;
    dialog.setAttribute('aria-label', image.alt);
    dialog.showModal(); fitImage();
  });
});
viewport.addEventListener('pointerdown', event => {
  if (event.button !== 0 || event.isPrimary === false) return;
  event.preventDefault();
  drag = { id: event.pointerId, x: event.clientX, y: event.clientY, panX: pan.x, panY: pan.y };
  viewport.setPointerCapture(event.pointerId);
  viewport.classList.add('is-dragging');
  viewport.focus({ preventScroll: true });
});
viewport.addEventListener('pointermove', event => {
  if (!drag || drag.id !== event.pointerId) return;
  pan = { x: drag.panX + event.clientX - drag.x, y: drag.panY + event.clientY - drag.y };
  renderImage();
});
function endDrag(event) {
  if (!drag || drag.id !== event.pointerId) return;
  if (viewport.hasPointerCapture(event.pointerId)) viewport.releasePointerCapture(event.pointerId);
  drag = null; viewport.classList.remove('is-dragging');
}
viewport.addEventListener('pointerup', endDrag);
viewport.addEventListener('pointercancel', endDrag);
viewport.addEventListener('lostpointercapture', endDrag);
viewport.addEventListener('wheel', event => {
  event.preventDefault();
  const box = viewport.getBoundingClientRect();
  const pixels = event.deltaY * (event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? viewport.clientHeight : 1);
  changeZoom(zoom * Math.exp(-Math.max(-240, Math.min(240, pixels)) * 0.002), {
    x: event.clientX - box.left - box.width / 2,
    y: event.clientY - box.top - box.height / 2
  });
}, { passive: false });
viewport.addEventListener('dblclick', fitImage);
viewport.addEventListener('keydown', event => {
  const moves = { ArrowLeft: [40, 0], ArrowRight: [-40, 0], ArrowUp: [0, 40], ArrowDown: [0, -40] };
  if (moves[event.key]) {
    event.preventDefault(); pan.x += moves[event.key][0]; pan.y += moves[event.key][1]; renderImage();
  } else if (event.key === '+' || event.key === '=') { event.preventDefault(); changeZoom(zoom * 1.25); }
  else if (event.key === '-') { event.preventDefault(); changeZoom(zoom / 1.25); }
  else if (event.key === 'Home' || event.key === '0') { event.preventDefault(); fitImage(); }
});
dialog.querySelector('.dialog-close').addEventListener('click', () => dialog.close());
dialog.addEventListener('close', () => { drag = null; viewport.classList.remove('is-dragging'); dialogImage.removeAttribute('src'); });
dialog.addEventListener('click', event => {
  if (event.target !== dialog) return;
  const box = dialog.getBoundingClientRect();
  if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
});
new ResizeObserver(() => { if (dialog.open) fitImage(); }).observe(viewport);

document.querySelectorAll('[data-demo-toggle]').forEach(button => {
  const demo = document.getElementById(button.dataset.demoToggle);
  const image = demo.querySelector('img');
  function setPlaying(playing) {
    image.src = playing ? image.dataset.gif : image.dataset.poster;
    button.textContent = playing ? 'GIF 일시정지' : 'GIF 재생';
    button.setAttribute('aria-pressed', String(playing));
  }
  setPlaying(!window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  button.addEventListener('click', () => setPlaying(button.getAttribute('aria-pressed') !== 'true'));
});
const sections = document.querySelectorAll('main > section[id], footer[id]');
const navigation = document.querySelectorAll('nav a[href^="#"]');
const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      navigation.forEach(link => {
        if (link.hash === `#${entry.target.id}`) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    }
  });
}, { rootMargin: '-10% 0px -65% 0px', threshold: 0 });
sections.forEach(section => observer.observe(section));
