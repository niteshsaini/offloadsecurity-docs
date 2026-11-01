// Wraps every Markdown table in <div class="table-wrap"> so a wide table
// scrolls inside its own box instead of widening the whole page on phones.
// (Styling lives in src/css/custom.css → "Tables".)
function wrapTables(node) {
  if (!node.children) return;
  node.children = node.children.map((child) => {
    if (child.type === 'element' && child.tagName === 'table') {
      return {
        type: 'element',
        tagName: 'div',
        properties: {className: ['table-wrap']},
        children: [child],
      };
    }
    wrapTables(child);
    return child;
  });
}

module.exports = function rehypeTableWrap() {
  return (tree) => wrapTables(tree);
};
