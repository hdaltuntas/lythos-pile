"use strict";
/* Lythos Pile — the browser interface.
 *
 * The forms are built from the schema the server sends: field keys, labels,
 * units and defaults are declared once, in Python. Nothing here holds a second
 * copy of a label, so changing the language means fetching the schema again and
 * redrawing the forms.
 *
 * Every input lives in one flat object (S.values). That object is what is sent
 * to the server, and what a saved project file is made of. A field can declare
 * when it applies — "only for Janbu's base", "only when the modulus is
 * entered" — and the form redraws itself whenever a value another field
 * depends on changes, so what is on the screen is the method that is actually
 * running.
 *
 * Three modules share the page: the pile and its group, the rock socket, and
 * the study. Each keeps its own view and figure; the report carries whatever
 * has been analysed.
 */

/* --------------------------------------------------------------- state */
const S = {
  meta: null,             // /api/meta
  values: {},             // current value of every field
  module: "inputs",       // inputs | socket | study
  view: { inputs: "summary", socket: "summary", study: "study" },
  analysis: null,         // last pile analysis payload
  socket: null,           // last rock socket payload
  study: null,            // last study payload
  figure: { inputs: "section", socket: "socket_section", study: "hist" },
  output: "",
  selected: { soil: 0, study: 0 },
  variables: [],          // inputs a study may vary
  poll: null,
  plotVersion: 0,         // so a redrawn figure is not served from the cache
  watched: new Set(),     // keys other fields' visibility depends on
};

const $ = (id) => document.getElementById(id);
const el = (tag, attrs = {}, ...children) => {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") node.className = v;
    else if (k === "html") node.innerHTML = v;
    else if (k === "text") node.textContent = v;
    else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
    else if (v !== null && v !== undefined && v !== false) node.setAttribute(k, v);
  }
  for (const c of children) if (c) node.append(c);
  return node;
};
const T = (key) => (S.meta && S.meta.strings[key]) || key;

/* ------------------------------------------------------------- server */
async function api(path, body) {
  const options = body === undefined
    ? {}
    : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) };
  const response = await fetch(path, options);
  const data = await response.json();
  if (data.error) throw new Error(data.error);
  return data;
}

function status(message, isError = false) {
  $("statusMsg").textContent = message || "";
  $("statusBar").classList.toggle("error", !!isError);
}

function busy(on, note) {
  $("progressBar").style.width = on ? "65%" : "0";
  if (note !== undefined) status(note);
  for (const id of ["btnAnalyse", "btnSocket", "btnStudy", "btnReport"]) {
    const node = $(id);
    if (node) node.disabled = on;
  }
  $("btnCancel").disabled = !on;
}

function progress(done, total) {
  const pct = total > 0 ? Math.round((100 * done) / total) : 0;
  $("progressBar").style.width = `${pct}%`;
}

async function download(path, body, filename) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.error || response.statusText);
  }
  const url = URL.createObjectURL(await response.blob());
  const link = el("a", { href: url, download: filename });
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

/* --------------------------------------------------- conditional fields */
/* A field or group applies when every one of its conditions holds. */
function applies(item) {
  for (const condition of item.when || []) {
    const value = S.values[condition.key];
    if (!condition.in.some((wanted) => wanted === value)) return false;
  }
  return true;
}

/* Which keys other fields watch: changing one of them redraws the forms. */
function collectWatched() {
  S.watched = new Set();
  for (const part of ["project", "pile", "options", "socket", "study"]) {
    for (const group of S.meta.schema[part].groups) {
      for (const item of [group, ...group.fields]) {
        for (const condition of item.when || []) S.watched.add(condition.key);
      }
    }
  }
}

/* -------------------------------------------------------- form building */
function fieldNode(field) {
  const id = "f_" + field.key;
  const value = S.values[field.key];

  if (field.kind === "check") {
    const input = el("input", {
      type: "checkbox", id,
      onchange: (e) => { setValue(field.key, e.target.checked); },
    });
    input.checked = !!value;
    return el("div", { class: "field check" }, input, el("label", { for: id, text: field.label }));
  }

  let input;
  if (field.kind === "select") {
    input = el("select", { id, onchange: (e) => setValue(field.key, e.target.value) });
    for (const option of field.options || []) {
      input.append(el("option", { value: option.value, text: option.label }));
    }
    input.value = value ?? (field.options && field.options[0] && field.options[0].value);
  } else if (field.kind === "text") {
    input = el("input", {
      type: "text", id,
      oninput: (e) => { S.values[field.key] = e.target.value; },
    });
    input.value = value ?? "";
  } else {
    input = el("input", {
      type: "number", id,
      step: field.step || (field.decimals === 0 ? 1 : Math.pow(10, -(field.decimals ?? 2))),
      min: field.min, max: field.max,
      oninput: (e) => {
        const raw = e.target.value.trim();
        S.values[field.key] = raw === "" ? null : parseFloat(raw);
      },
      onchange: () => { if (field.key === "nx" || field.key === "ny") refreshVariables(); },
    });
    input.value = value === null || value === undefined ? "" : value;
  }

  const label = el("label", { for: id }, document.createTextNode(field.label));
  if (field.unit) label.append(el("span", { class: "unit", text: field.unit }));
  return el("div", { class: "field" }, label, input);
}

/* A value another field's visibility depends on redraws the forms. */
function setValue(key, value) {
  S.values[key] = value;
  if (S.watched.has(key)) renderForms();
  if (key === "nx" || key === "ny") refreshVariables();
}

function groupNode(group) {
  const box = el("fieldset", {}, el("legend", { text: group.title }));
  for (const field of group.fields) {
    if (applies(field)) box.append(fieldNode(field));
  }
  if (group.note) box.append(el("div", { class: "note", text: group.note }));
  return box;
}

function renderForm(host, groups) {
  host.replaceChildren(...groups.filter(applies).map(groupNode));
}

function renderForms() {
  renderForm($("projectForm"), S.meta.schema.project.groups);
  renderForm($("pileForm"), S.meta.schema.pile.groups);
  renderForm($("optionsForm"), S.meta.schema.options.groups);
  renderForm($("socketForm"), S.meta.schema.socket.groups);
  renderForm($("studyForm"), S.meta.schema.study.groups);
}

/* ------------------------------------------------------------ input tables */
const TABLES = {
  soil: { values: "soil_profile", head: "soilHead", body: "soilBody", schema: "soil" },
  study: { values: "study_variables", head: "studyHead", body: "studyBody", schema: "study_vars" },
};

function columnsOf(name) {
  const columns = S.meta.schema[TABLES[name].schema].columns.map((c) => ({ ...c }));
  if (name === "study") {
    // The inputs on offer depend on the soil layers.
    columns[0] = { ...columns[0], options: S.variables };
  }
  return columns;
}

function renderTable(name) {
  const spec = TABLES[name];
  const columns = columnsOf(name);
  const clayOnly = S.meta.schema.soil.clay_only || [];
  const sandOnly = S.meta.schema.soil.sand_only || [];
  $(spec.head).replaceChildren(...columns.map((c) => el("th", { text: c.label })));

  const rows = S.values[spec.values] || (S.values[spec.values] = []);
  const body = $(spec.body);
  body.replaceChildren();
  rows.forEach((row, index) => {
    const tr = el("tr", {
      class: index === S.selected[name] ? "selected" : "",
      onclick: () => {
        if (S.selected[name] === index) return;
        S.selected[name] = index;
        for (const [i, node] of Array.from(body.children).entries()) {
          node.classList.toggle("selected", i === index);
        }
      },
    });
    const granular = name === "soil" && row.behaviour !== "cohesive";
    const cohesive = name === "soil" && row.behaviour === "cohesive";
    for (const column of columns) {
      let input;
      if (column.kind === "select") {
        input = el("select", {
          onchange: (e) => {
            row[column.key] = e.target.value;
            if (name === "study" && column.key === "path") {
              seedVariable(row);
              renderTable("study");
            }
            if (name === "soil" && column.key === "behaviour") {
              renderTable("soil");
              refreshVariables();
            }
          },
        });
        for (const option of column.options || []) {
          input.append(el("option", { value: option.value, text: option.label }));
        }
        input.value = row[column.key] ?? (column.options[0] ? column.options[0].value : "");
        row[column.key] = input.value;
      } else {
        input = el("input", {
          type: column.kind === "number" ? "number" : "text",
          step: "any",
          oninput: (e) => {
            const raw = e.target.value;
            row[column.key] = column.kind === "number"
              ? (raw === "" ? null : parseFloat(raw))
              : raw;
          },
          onchange: () => {
            if (name === "soil" && column.key === "name") refreshVariables();
          },
        });
        input.value = row[column.key] ?? "";
      }
      const off = (granular && clayOnly.includes(column.key)) ||
        (cohesive && sandOnly.includes(column.key));
      input.disabled = off;
      tr.append(el("td", { class: off ? "off" : "" }, input));
    }
    body.append(tr);
  });
}

function blankRow(name) {
  if (name === "soil") {
    const last = (S.values.soil_profile || []).slice(-1)[0];
    return last ? { ...last } : { ...S.meta.schema.soil.rows[0] };
  }
  const first = S.variables[0];
  return seedVariable({
    path: first ? first.value : "", mode: "range", dist: "normal", cov: 0.1, n_points: 5,
  });
}

/* A new or re-pointed study variable starts around the project's own value. */
function seedVariable(row) {
  const choice = S.variables.find((c) => c.value === row.path);
  const base = choice && Number.isFinite(choice.base) ? choice.base : 1;
  const round = (x) => Math.round(x * 1000) / 1000;
  row.label = choice ? choice.label : row.path;
  row.min = round(base * 0.8);
  row.max = round(base * 1.2);
  if (row.max <= row.min) row.max = round(row.min + 1);
  row.mean = round(base);
  return row;
}

function addRow(name) {
  const key = TABLES[name].values;
  (S.values[key] = S.values[key] || []).push(blankRow(name));
  S.selected[name] = S.values[key].length - 1;
  renderTable(name);
  if (name === "soil") refreshVariables();
}

function removeRow(name) {
  const rows = S.values[TABLES[name].values] || [];
  const minimum = name === "soil" ? 1 : 0;
  if (rows.length <= minimum) return;
  rows.splice(S.selected[name], 1);
  S.selected[name] = Math.max(0, S.selected[name] - 1);
  renderTable(name);
  if (name === "soil") refreshVariables();
}

async function refreshVariables() {
  try {
    const data = await api("/api/variables", { values: S.values });
    S.variables = data.choices || [];
    // A variable keeps the label of the input it addresses.
    for (const row of S.values.study_variables || []) {
      const choice = S.variables.find((c) => c.value === row.path);
      if (choice) row.label = choice.label;
    }
    if (S.module === "study") renderTable("study");
  } catch {
    /* the list is a convenience; a failure here must not stop the analysis */
  }
}

/* ------------------------------------------------------------ views */
const VIEWS = {
  inputs: [["summary", "view_summary"], ["text", "view_text"], ["figures", "view_figures"]],
  socket: [["summary", "view_summary"], ["text", "view_text"], ["figures", "view_figures"]],
  study: [["study", "view_study"], ["figures", "view_figures"], ["text", "view_text"]],
};

function renderTabs() {
  $("viewTabs").replaceChildren(...VIEWS[S.module].map(([key, label]) =>
    el("button", {
      text: T(label),
      class: S.view[S.module] === key ? "active" : "",
      onclick: () => { S.view[S.module] = key; renderTabs(); renderView(); },
    })));
}

function placeholder(text) {
  return el("div", { class: "placeholder", text });
}

function plotImage(target, kind, output) {
  const query = `target=${target}&kind=${kind}` +
    (output ? `&output=${encodeURIComponent(output)}` : "") + `&v=${S.plotVersion}`;
  return el("img", { src: `/api/plot?${query}`, alt: kind });
}

function dataTable(columns, rows, options = {}) {
  const body = rows.map((row) => {
    const tr = el("tr", { class: (row.primary ? "primary " : "") + (row.muted ? "muted" : "") });
    (row.cells || row).forEach((cell, index) => {
      const state = row.states ? row.states[index] : "";
      tr.append(el("td", { class: state || "", text: cell }));
    });
    return tr;
  });
  return el("table", { class: "data" },
    el("thead", {}, el("tr", {}, ...columns.map((c) => el("th", { text: c })))),
    el("tbody", {}, ...body));
}

function cardRow(cards) {
  return el("div", { class: "cards" }, ...cards.map((card) =>
    el("div", { class: "card " + (card.state || "") },
      el("small", { text: card.title }),
      el("b", { text: card.value }),
      el("span", { class: "sub", text: card.sub || "" }))));
}

function warningBox(warnings) {
  if (!warnings || !warnings.length) return null;
  return el("div", { class: "warnings" },
    el("h3", { text: T("warnings_title") }),
    el("ul", {}, ...warnings.map((w) => el("li", { text: w }))));
}

function updatePicker() {
  const showFigures = S.view[S.module] === "figures";
  $("picker").hidden = !showFigures;
  if (!showFigures) return;

  const figure = $("figure");
  const module = S.module;
  if (module === "inputs" || module === "socket") {
    const payload = module === "inputs" ? S.analysis : S.socket;
    const keys = (payload && payload.figures) || [];
    figure.replaceChildren(...keys.map((key) =>
      el("option", { value: key, text: S.meta.figure_labels[key] || key })));
    if (!keys.includes(S.figure[module])) S.figure[module] = keys[0] || "";
    figure.value = S.figure[module];
    $("outputWrap").hidden = true;
  } else {
    const views = (S.study && S.study.views) || [];
    figure.replaceChildren(...views.map((view) =>
      el("option", { value: view, text: S.meta.study_view_labels[view] || view })));
    if (!views.includes(S.figure.study)) S.figure.study = views[0] || "hist";
    figure.value = S.figure.study;

    const outputs = (S.study && S.study.outputs) || [];
    $("outputWrap").hidden = outputs.length === 0;
    const output = $("output");
    output.replaceChildren(...outputs.map((o) =>
      el("option", { value: o.value, text: o.label })));
    if (!outputs.some((o) => o.value === S.output)) {
      S.output = outputs.length ? outputs[0].value : "";
    }
    output.value = S.output;
  }
}

function summaryView(payload, tableTitle, target, figures) {
  const parts = [cardRow(payload.cards)];
  const warnings = warningBox(payload.warnings);
  if (warnings) parts.push(warnings);
  if (payload.table) {
    parts.push(el("h2", { text: T(tableTitle) }));
    parts.push(dataTable(payload.table.columns, payload.table.rows));
  }
  for (const figure of figures) parts.push(plotImage(target, figure));
  return parts;
}

function renderView() {
  const view = $("view");
  const which = S.view[S.module];
  updatePicker();

  if (S.module === "inputs") {
    if (!S.analysis) return view.replaceChildren(placeholder(T("no_results")));
    if (which === "summary") {
      return view.replaceChildren(...summaryView(S.analysis, "methods_title", "analysis",
        ["section", "length"]));
    }
    if (which === "text") return view.replaceChildren(el("pre", { text: S.analysis.text }));
    return view.replaceChildren(plotImage("analysis", S.figure.inputs));
  }

  if (S.module === "socket") {
    if (!S.socket) return view.replaceChildren(placeholder(T("no_socket")));
    if (which === "summary") {
      return view.replaceChildren(...summaryView(S.socket, "socket_table_title", "socket",
        ["socket_length", "socket_settlement"]));
    }
    if (which === "text") return view.replaceChildren(el("pre", { text: S.socket.text }));
    return view.replaceChildren(plotImage("socket", S.figure.socket));
  }

  if (!S.study) return view.replaceChildren(placeholder(T("no_study")));
  if (which === "figures") {
    return view.replaceChildren(plotImage("study", S.figure.study, S.output));
  }
  if (which === "text") return view.replaceChildren(el("pre", { text: S.study.text }));

  const parts = [el("pre", { text: S.study.text })];
  if (S.study.table && S.study.table.rows.length) {
    parts.push(el("h2", { text: T("study_vars_group") }));
    parts.push(dataTable(S.study.table.columns, S.study.table.rows));
    if (S.study.table.truncated) {
      parts.push(el("div", { class: "note", text: T("study_table_note") }));
    }
  }
  view.replaceChildren(...parts);
}

/* ------------------------------------------------------------- actions */
async function runAnalysis() {
  busy(true, T("running_analysis"));
  try {
    const data = await api("/api/analyse", { values: S.values });
    S.analysis = data;
    S.plotVersion += 1;
    switchModule("inputs");
    // Whatever view was open stays open: re-analysing after a change of
    // language should not drag the reader back to the summary.
    if (!VIEWS.inputs.some(([key]) => key === S.view.inputs)) S.view.inputs = "summary";
    renderTabs();
    renderView();
    status(`${T("analysis_complete")} ${data.headline}`);
  } catch (error) {
    S.analysis = null;
    renderView();
    status(`${T("error")}: ${error.message}`, true);
  } finally {
    busy(false);
  }
}

async function runSocket() {
  busy(true, T("running_analysis"));
  try {
    const data = await api("/api/socket", { values: S.values });
    S.socket = data;
    S.plotVersion += 1;
    switchModule("socket");
    if (!VIEWS.socket.some(([key]) => key === S.view.socket)) S.view.socket = "summary";
    renderTabs();
    renderView();
    status(`${T("socket_complete")} ${data.headline}`);
  } catch (error) {
    S.socket = null;
    renderView();
    status(`${T("error")}: ${error.message}`, true);
  } finally {
    busy(false);
  }
}

async function runStudy() {
  busy(true, T("running_analysis"));
  try {
    const data = await api("/api/study", { values: S.values });
    if (!data.ok) throw new Error(data.error);
    S.study = null;
    switchModule("study");
    startPolling();
  } catch (error) {
    busy(false);
    status(`${T("error")}: ${error.message}`, true);
  }
}

async function cancelStudy() {
  try {
    await api("/api/cancel", {});
    status(T("cancelled"));
  } catch (error) {
    status(`${T("error")}: ${error.message}`, true);
  }
}

async function loadStudy() {
  try {
    const data = await api("/api/study");
    if (!data.ok) throw new Error(data.error);
    S.study = data;
    if (!data.outputs.some((o) => o.value === S.output)) {
      S.output = data.outputs.length ? data.outputs[0].value : "";
    }
    if (!data.views.includes(S.figure.study)) S.figure.study = data.views[0] || "hist";
    S.plotVersion += 1;
    renderTabs();
    renderView();
  } catch (error) {
    status(`${T("error")}: ${error.message}`, true);
  }
}

async function downloadReport() {
  busy(true, T("report_running"));
  try {
    const format = $("reportFormat").value || "pdf";
    await download("/api/report", { format }, `lythospile_report.${format}`);
    status(T("report_action") + " ✓");
  } catch (error) {
    status(`${T("error")}: ${error.message}`, true);
  } finally {
    busy(false);
  }
}

async function exportStudy(format) {
  try {
    await download("/api/export-study", { format }, `lythospile_study.${format}`);
    status(T("saved"));
  } catch (error) {
    status(`${T("error")}: ${error.message}`, true);
  }
}

/* --------------------------------------------------- background polling */
function startPolling() {
  if (S.poll) return;
  S.poll = setInterval(async () => {
    let state;
    try {
      state = await api("/api/state");
    } catch {
      return;
    }
    if (state.job === "running") {
      progress(state.done, state.total);
      if (state.total) {
        status(T("study_progress").replace("{done}", state.done).replace("{total}", state.total));
      }
      return;
    }
    clearInterval(S.poll);
    S.poll = null;
    busy(false);

    if (state.job === "error") {
      status(`${T("error")}: ${state.error}`, true);
      return;
    }
    if (state.has_study) {
      await loadStudy();
      $("btnCsv").disabled = false;
      $("btnXlsx").disabled = false;
    }
    if (state.note) status(state.note);
  }, 400);
}

/* ------------------------------------------------------------- layout */
function switchModule(name) {
  S.module = name;
  $("paneInputs").hidden = name !== "inputs";
  $("paneSocket").hidden = name !== "socket";
  $("paneStudy").hidden = name !== "study";
  for (const button of document.querySelectorAll("nav.modules button")) {
    button.classList.toggle("active", button.dataset.module === name);
  }
  if (name === "study") renderTable("study");
  renderTabs();
  renderView();
}

function applyMeta(meta) {
  S.meta = meta;
  document.documentElement.lang = meta.language;
  collectWatched();

  $("tagline").textContent = T("tagline");
  $("lblLanguage").textContent = T("language");
  $("btnOpen").textContent = T("open");
  $("btnSave").textContent = T("save");
  $("btnTheme").title = T("theme");
  $("lblReport").textContent = T("report_format");
  $("btnReport").textContent = T("report_action");
  $("tabInputs").textContent = T("tab_inputs");
  $("tabSocket").textContent = T("tab_socket");
  $("tabStudy").textContent = T("tab_study_inputs");
  $("btnSocket").textContent = T("run_socket_button");
  $("socketNote").textContent = T("socket_group_note");
  $("lblSoil").textContent = T("soil_group");
  $("soilNote").textContent = T("soil_note");
  $("lblStudyVars").textContent = T("study_vars_group");
  $("btnAnalyse").textContent = T("run_analysis_button");
  $("btnStudy").textContent = T("study_run");
  $("btnCancel").textContent = T("study_cancel");
  $("btnCsv").textContent = T("study_export_csv");
  $("btnXlsx").textContent = T("study_export_xlsx");
  $("lblFigure").textContent = T("figure");
  $("lblOutput").textContent = T("output");
  for (const button of document.querySelectorAll("button.add")) button.textContent = T("add_row");
  for (const button of document.querySelectorAll("button.del")) button.textContent = T("del_row");

  const language = $("language");
  language.replaceChildren(...meta.languages.map((code) =>
    el("option", { value: code, text: code.toUpperCase() })));
  language.value = meta.language;

  const report = $("reportFormat");
  const previous = report.value;
  report.replaceChildren(...["pdf", "html", "docx"].map((format) =>
    el("option", { value: format, text: T("report_" + format) })));
  report.value = previous || "pdf";

  renderForms();
  renderTable("soil");
  renderTabs();
  renderView();
  status(T("ready"));
}

async function setLanguage(code) {
  applyMeta(await api("/api/language", { lang: code }));
  await refreshVariables();
  const module = S.module;
  if (S.analysis) await runAnalysis();
  if (S.socket) await runSocket();
  if (S.study) await loadStudy();
  switchModule(module);
}

/* ------------------------------------------------------------ save / open */
async function saveProject() {
  try {
    await download("/api/project", { values: S.values }, "project.pile");
    status(T("saved"));
  } catch (error) {
    status(`${T("error")}: ${error.message}`, true);
  }
}

function openProject(file) {
  const reader = new FileReader();
  reader.onload = async () => {
    try {
      const project = JSON.parse(reader.result);
      const data = await api("/api/load", { project });
      S.values = data.values;
      S.analysis = null;
      S.socket = null;
      S.study = null;
      renderForms();
      renderTable("soil");
      await refreshVariables();
      renderTable("study");
      renderView();
      status(T("loaded"));
    } catch (error) {
      status(`${T("error")}: ${error.message}`, true);
    }
  };
  reader.readAsText(file);
}

/* ------------------------------------------------------------------ theme */
async function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  try {
    localStorage.setItem("lythospile-theme", theme);
  } catch { /* storage can be switched off in a private window */ }
  try {
    await api("/api/theme", { theme });           // the figures follow the page
    if (S.analysis || S.socket || S.study) {
      S.plotVersion += 1;
      renderView();
    }
  } catch { /* the page is themed either way */ }
}

function storedTheme() {
  try {
    return localStorage.getItem("lythospile-theme");
  } catch {
    return null;
  }
}

/* ------------------------------------------------------------- start-up */
async function start() {
  const theme = storedTheme();
  if (theme) document.documentElement.setAttribute("data-theme", theme);

  const meta = await api("/api/meta");
  S.values = JSON.parse(JSON.stringify(meta.defaults));
  applyMeta(meta);
  // Always tell the server: it keeps the theme of whichever page spoke last,
  // and the figures would otherwise follow that page rather than this one.
  await applyTheme(theme === "dark" ? "dark" : "light");
  await refreshVariables();

  $("language").addEventListener("change", (e) => setLanguage(e.target.value));
  $("btnTheme").addEventListener("click", () => applyTheme(
    document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark"));
  $("btnSave").addEventListener("click", saveProject);
  $("btnOpen").addEventListener("click", () => $("fileInput").click());
  $("fileInput").addEventListener("change", (e) => {
    if (e.target.files[0]) openProject(e.target.files[0]);
    e.target.value = "";
  });
  $("btnReport").addEventListener("click", downloadReport);
  $("btnAnalyse").addEventListener("click", runAnalysis);
  $("btnSocket").addEventListener("click", runSocket);
  $("btnStudy").addEventListener("click", runStudy);
  $("btnCancel").addEventListener("click", cancelStudy);
  $("btnCsv").addEventListener("click", () => exportStudy("csv"));
  $("btnXlsx").addEventListener("click", () => exportStudy("xlsx"));
  $("figure").addEventListener("change", (e) => { S.figure[S.module] = e.target.value; renderView(); });
  $("output").addEventListener("change", (e) => { S.output = e.target.value; renderView(); });
  for (const button of document.querySelectorAll("button.add")) {
    button.addEventListener("click", () => addRow(button.dataset.table));
  }
  for (const button of document.querySelectorAll("button.del")) {
    button.addEventListener("click", () => removeRow(button.dataset.table));
  }
  for (const button of document.querySelectorAll("nav.modules button")) {
    button.addEventListener("click", () => switchModule(button.dataset.module));
  }
  $("btnCancel").disabled = true;
  $("btnCsv").disabled = true;
  $("btnXlsx").disabled = true;
}

start().catch((error) => status("Error: " + error.message, true));
