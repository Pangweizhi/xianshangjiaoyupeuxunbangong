const ALLOWED_TAGS = new Set([
  "A",
  "B",
  "BLOCKQUOTE",
  "BR",
  "CODE",
  "DIV",
  "EM",
  "H1",
  "H2",
  "H3",
  "H4",
  "H5",
  "H6",
  "HR",
  "I",
  "LI",
  "OL",
  "P",
  "PRE",
  "S",
  "SPAN",
  "STRONG",
  "SUB",
  "SUP",
  "UL"
]);

const ALLOWED_ATTRS = new Set(["href", "target", "rel", "title", "class"]);

function escapeHtml(value: string) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function normalizeText(value: string) {
  return value
    .replace(/\r\n/g, "\n")
    .replace(/\u00a0/g, " ")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

function convertMarkdownInline(value: string) {
  return value
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/__([^_]+)__/g, "<strong>$1</strong>")
    .replace(/\*([^*\n]+)\*/g, "<em>$1</em>")
    .replace(/_([^_\n]+)_/g, "<em>$1</em>")
    .replace(/`([^`\n]+)`/g, "<code>$1</code>");
}

function convertMarkdownBlocks(value: string) {
  const lines = value.split("\n");
  const output: string[] = [];
  let index = 0;

  while (index < lines.length) {
    const line = lines[index].trimEnd();
    const trimmed = line.trim();

    if (!trimmed) {
      index += 1;
      continue;
    }

    if (/^```/.test(trimmed)) {
      const codeLines: string[] = [];
      index += 1;
      while (index < lines.length && !/^```/.test(lines[index].trim())) {
        codeLines.push(lines[index]);
        index += 1;
      }
      if (index < lines.length) {
        index += 1;
      }
      output.push(`<pre><code>${escapeHtml(codeLines.join("\n"))}</code></pre>`);
      continue;
    }

    if (/^[-*+]\s+/.test(trimmed)) {
      const items: string[] = [];
      while (index < lines.length && /^[-*+]\s+/.test(lines[index].trim())) {
        items.push(`<li>${convertMarkdownInline(escapeHtml(lines[index].trim().replace(/^[-*+]\s+/, "")))}</li>`);
        index += 1;
      }
      output.push(`<ul>${items.join("")}</ul>`);
      continue;
    }

    if (/^\d+\.\s+/.test(trimmed)) {
      const items: string[] = [];
      while (index < lines.length && /^\d+\.\s+/.test(lines[index].trim())) {
        items.push(`<li>${convertMarkdownInline(escapeHtml(lines[index].trim().replace(/^\d+\.\s+/, "")))}</li>`);
        index += 1;
      }
      output.push(`<ol>${items.join("")}</ol>`);
      continue;
    }

    if (/^>\s?/.test(trimmed)) {
      const quoteLines: string[] = [];
      while (index < lines.length && /^>\s?/.test(lines[index].trim())) {
        quoteLines.push(lines[index].trim().replace(/^>\s?/, ""));
        index += 1;
      }
      output.push(`<blockquote><p>${convertMarkdownInline(escapeHtml(quoteLines.join("\n")))}</p></blockquote>`);
      continue;
    }

    const paragraphLines: string[] = [];
    while (
      index < lines.length &&
      lines[index].trim() &&
      !/^```/.test(lines[index].trim()) &&
      !/^[-*+]\s+/.test(lines[index].trim()) &&
      !/^\d+\.\s+/.test(lines[index].trim()) &&
      !/^>\s?/.test(lines[index].trim())
    ) {
      paragraphLines.push(lines[index]);
      index += 1;
    }
    output.push(`<p>${convertMarkdownInline(escapeHtml(paragraphLines.join("\n"))).replace(/\n/g, "<br>")}</p>`);
  }

  return output.join("");
}

function sanitizeHtml(value: string) {
  const parser = new DOMParser();
  const doc = parser.parseFromString(`<div>${value}</div>`, "text/html");
  const root = doc.body.firstElementChild;
  if (!root) {
    return escapeHtml(value).replace(/\n/g, "<br>");
  }

  const walk = (node: Node): string => {
    if (node.nodeType === Node.TEXT_NODE) {
      return escapeHtml(node.textContent || "");
    }
    if (node.nodeType !== Node.ELEMENT_NODE) {
      return "";
    }

    const element = node as HTMLElement;
    const tagName = element.tagName.toUpperCase();
    const children = Array.from(element.childNodes).map((child) => walk(child)).join("");

    if (!ALLOWED_TAGS.has(tagName)) {
      return children;
    }

    if (tagName === "BR" || tagName === "HR") {
      return `<${tagName.toLowerCase()} />`;
    }

    const attrs: string[] = [];
    for (const attr of Array.from(element.attributes)) {
      const name = attr.name.toLowerCase();
      const rawValue = attr.value;
      if (name.startsWith("on") || !ALLOWED_ATTRS.has(name)) {
        continue;
      }
      if (name === "href") {
        const normalized = rawValue.trim();
        if (!/^(https?:|mailto:|\/)/i.test(normalized)) {
          continue;
        }
        attrs.push(`href="${escapeHtml(normalized)}"`);
        continue;
      }
      if (name === "target") {
        const normalized = rawValue.trim();
        if (!["_blank", "_self", "_parent", "_top"].includes(normalized)) {
          continue;
        }
        attrs.push(`target="${escapeHtml(normalized)}"`);
        if (!element.getAttribute("rel")) {
          attrs.push('rel="noopener noreferrer"');
        }
        continue;
      }
      attrs.push(`${name}="${escapeHtml(rawValue)}"`);
    }

    return `<${tagName.toLowerCase()}${attrs.length ? ` ${attrs.join(" ")}` : ""}>${children}</${tagName.toLowerCase()}>`;
  };

  return Array.from(root.childNodes).map((child) => walk(child)).join("");
}

export function renderRichText(content?: string) {
  const normalized = normalizeText(content || "");
  if (!normalized) {
    return "";
  }

  const html = /<[^>]+>/.test(normalized) ? normalized : convertMarkdownBlocks(normalized);
  return sanitizeHtml(html).replace(/<p><\/p>/g, "");
}
