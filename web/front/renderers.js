export function showPlaceholder(element, message) {
  element.innerHTML = `<p class="placeholder">${message}</p>`;
}

export function renderList(container, items, formatter) {
  container.innerHTML = "";
  if (!Array.isArray(items) || !items.length) {
    showPlaceholder(container, "No hay datos disponibles");
    return;
  }

  const fragment = document.createDocumentFragment();
  items.slice().reverse().forEach((item) => {
    const li = document.createElement("li");
    li.textContent = formatter(item);
    fragment.appendChild(li);
  });
  container.appendChild(fragment);
}

export function abbreviateTeam(name) {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return name;

  let short = parts[0];
  if (parts.length > 1) {
    let second = parts[1].replace(/[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]/g, "");
    second = second.slice(0, 2);
    if (second) {
      short = `${parts[0]} ${second}.`;
    }
  }

  if (short.length <= 10) return short;
  let truncated = short.slice(0, 9);
  if (truncated.endsWith(" ") || (short.length > 9 && short[9] === " ")) {
    return truncated.trimEnd();
  }
  return `${truncated}.`;
}
