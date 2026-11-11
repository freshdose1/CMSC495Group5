// Injection returns only rendered text. It never changes the active page.
(() => {
  const root = document.querySelector('main, article, [role="main"]') || document.body;
  if (!root) return '';
  const ignored = 'script,style,noscript,nav,footer,header,aside,form,input,textarea,select,button,[hidden],[aria-hidden="true"]';
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const chunks = [];
  while (walker.nextNode()) {
    const node = walker.currentNode;
    const parent = node.parentElement;
    if (!parent || parent.closest(ignored)) continue;
    const style = getComputedStyle(parent);
    if (style.visibility === 'hidden' || style.display === 'none' || !parent.getClientRects().length) continue;
    chunks.push(node.textContent);
  }
  return chunks.join(' ');
})();
