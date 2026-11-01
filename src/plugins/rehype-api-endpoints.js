// Gives API endpoints a coloured HTTP-method badge.
//
//  - A code block whose whole content is one `METHOD /path` line becomes an
//    endpoint bar:  [GET] /api/alerts
//  - Inline code that starts with `METHOD /` (the API tables) gets the method
//    wrapped in a small coloured label.
// Styling: src/css/custom.css → "API endpoints".
const METHOD_RE = /^(GET|POST|PUT|PATCH|DELETE)\s+(\/\S*)$/;
const INLINE_RE = /^(GET|POST|PUT|PATCH|DELETE)(\s+)(\/.*)$/;

const text = (node) =>
  node.type === 'text' ? node.value : (node.children || []).map(text).join('');

const methodBadge = (method) => ({
  type: 'element',
  tagName: 'span',
  properties: {className: ['api-method', `api-method--${method.toLowerCase()}`]},
  children: [{type: 'text', value: method}],
});

function transform(node, parent) {
  if (!node.children) return;
  node.children = node.children.map((child) => {
    if (child.type !== 'element') return child;

    // <pre><code>GET /api/x</code></pre>  →  endpoint bar
    if (child.tagName === 'pre' && child.children?.length === 1 && child.children[0].tagName === 'code') {
      const m = text(child).trim().match(METHOD_RE);
      if (m) {
        return {
          type: 'element',
          tagName: 'div',
          properties: {className: ['api-endpoint']},
          children: [
            methodBadge(m[1]),
            {type: 'element', tagName: 'code', properties: {}, children: [{type: 'text', value: m[2]}]},
          ],
        };
      }
    }

    // inline `GET /api/x` (not inside a <pre>)
    if (child.tagName === 'code' && parent?.tagName !== 'pre' && node.tagName !== 'pre') {
      const t = text(child);
      const m = t.match(INLINE_RE);
      if (m && child.children.length === 1 && child.children[0].type === 'text') {
        return {
          type: 'element',
          tagName: 'span',
          properties: {className: ['api-inline']},
          children: [
            methodBadge(m[1]),
            {type: 'element', tagName: 'code', properties: {}, children: [{type: 'text', value: m[3]}]},
          ],
        };
      }
    }

    transform(child, node);
    return child;
  });
}

module.exports = function rehypeApiEndpoints() {
  return (tree) => transform(tree, null);
};
