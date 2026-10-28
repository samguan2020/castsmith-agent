export function characters(builds) {
  return newest(builds.filter(build => build.status === "succeeded"
    && !build.character_build_id && hasArtifact(build, "character.glb")));
}

function newest(builds) {
  return [...builds].sort((a, b) => (b.completed_at || b.created_at || "")
    .localeCompare(a.completed_at || a.created_at || ""));
}

function hasArtifact(build, name) {
  return build.artifacts?.some(artifact => artifact.name === name) ?? false;
}

export function clips(builds, characterId, rig) {
  return newest(builds.filter(build => build.status === "succeeded"
    && build.character_build_id === characterId && (build.kind === "rig_test") === rig))
    .flatMap(build => (build.request?.motions || []).flatMap((motion, index) =>
      hasArtifact(build, `motion-${index}.glb`)
        ? [{ key: `${build.id}:${index}`, build, motion, index }] : []));
}

export function artifactUrl(buildId, name) {
  return `/api/builds/${encodeURIComponent(buildId)}/artifacts/${encodeURIComponent(name)}`;
}

export function downloadEntries(character, clip) {
  if (!character) return [];
  if (clip && (clip.build.kind === "rig_test" || clip.build.character_build_id !== character.id)) {
    throw new Error("The downloaded motion must belong to the current character and must not be RigTest");
  }
  const entries = [];
  function add(build, files) {
    for (const [name, label] of files) {
      if (build.status === "succeeded" && hasArtifact(build, name)) {
        entries.push({ name, label, buildId: build.id, url: artifactUrl(build.id, name) });
      }
    }
  }
  add(character, [
    ["character.glb", "Character GLB"],
    ["preview.png", "Character preview PNG"],
    ["manifest.json", "Character manifest"],
  ]);
  if (clip) add(clip.build, [
    [`motion-${clip.index}.glb`, "Character motion GLB"],
    [`source-motion-${clip.index}.glb`, "SayMotion source GLB"],
    [`quality-${clip.index}.json`, "Motion quality report"],
    ["manifest.json", "Motion manifest"],
  ]);
  return entries;
}

export function choose(entries, requested, label) {
  if (requested && !entries.some(entry => entry.key === requested)) {
    throw new Error(`${label} version is missing, unfinished or does not belong to the current character: ${requested}`);
  }
  return requested || entries[0]?.key || "";
}

export async function startPreview() {
  const $ = id => document.getElementById(id);
  const { MotionViewer } = await import("/static/viewer.js");
  let builds = [];
  let library = [];
  let characterViewer;
  let shownCharacter = "";
  let shownDownloads = "";
  let refreshing = false;
  const requested = new URL(location.href).searchParams;
  const desired = {
    character: requested.get("character") || "",
    rig: requested.get("rig") ? `${requested.get("rig")}:0` : "",
    motion: requested.get("motion")
      ? `${requested.get("motion")}:${requested.get("clip") || "0"}` : "",
  };

  function group(names) {
    const state = { key: "", token: 0, viewers: [], ready: false };
    function time(time, duration) {
      if (!state.ready) return;
      const fraction = duration ? time / duration : 0;
      const primary = $(names[0] + "-viewer");
      primary.dataset.time = String(time);
      primary.dataset.progress = String(fraction);
      for (const [index, other] of state.viewers.slice(1).entries()) {
        other.seek(fraction);
        other.playing = false;
        $(names[index + 1] + "-viewer").dataset.time = String(other.action?.time ?? 0);
        $(names[index + 1] + "-viewer").dataset.progress = String(fraction);
      }
    }
    state.clear = () => {
      state.token++;
      state.key = "";
      state.ready = false;
      state.viewers.forEach(viewer => viewer.unload());
      names.forEach(name => {
        $(name + "-viewer").dataset.state = "empty";
        delete $(name + "-viewer").dataset.buildId;
        delete $(name + "-viewer").dataset.time;
        delete $(name + "-viewer").dataset.progress;
        $(name + "-error").textContent = "No preview clip is available for this character version.";
      });
    };
    state.load = async entry => {
      if (state.key === entry.key) return;
      const token = ++state.token;
      state.key = entry.key;
      state.ready = false;
      names.forEach(name => {
        $(name + "-viewer").dataset.state = "loading";
        $(name + "-viewer").dataset.buildId = entry.build.id;
        $(name + "-error").textContent = "";
      });
      try {
        if (!state.viewers.length) {
          for (const [index, name] of names.entries()) {
            state.viewers.push(new MotionViewer($(name + "-viewer"), index === 0 ? time : () => {},
              message => {
                $(name + "-error").textContent = message;
                $(name + "-viewer").dataset.state = "error";
                state.viewers.forEach(viewer => { viewer.playing = false; });
                state.ready = false;
                state.key = "";
              }));
          }
        }
        const loaded = await Promise.all(state.viewers.map(async (viewer, index) => {
          const name = names[index];
          $(name + "-error").textContent = "";
          const source = index === 1;
          if (source && !hasArtifact(entry.build, `source-motion-${entry.index}.glb`)) {
            viewer.unload();
            $(name + "-viewer").dataset.state = "empty";
            $(name + "-error").textContent = "This version has no saved SayMotion source motion.";
            return false;
          }
          const url = source
            ? `/api/builds/${encodeURIComponent(entry.build.id)}/sources/${entry.index}`
            : artifactUrl(entry.build.id, `motion-${entry.index}.glb`);
          try {
            const result = await viewer.load(url, true);
            if (token === state.token) {
              viewer.playing = false;
              $(name + "-viewer").dataset.state = result ? "ready" : "error";
            }
            return result;
          } catch (error) {
            if (token === state.token) {
              $(name + "-error").textContent = error.message;
              $(name + "-viewer").dataset.state = "error";
            }
            return false;
          }
        }));
        if (token !== state.token) return;
        state.ready = loaded[0];
        if (loaded[0]) state.viewers[0].playing = true;
      } catch (error) {
        if (token === state.token) {
          $(names[0] + "-error").textContent = error.message;
          $(names[0] + "-viewer").dataset.state = "error";
          state.key = "";
        }
      }
    };
    return state;
  }

  const rig = group(["rig"]);
  const motion = group(["target", "source"]);

  function renderDownloads(character, clip) {
    const entries = downloadEntries(character, clip);
    const key = entries.map(entry => entry.url).join("|");
    if (key === shownDownloads) return;
    shownDownloads = key;
    $("asset-links").replaceChildren(...entries.map(entry => {
      const link = document.createElement("a");
      link.href = entry.url;
      link.download = entry.name;
      link.textContent = entry.label;
      link.title = `${entry.buildId} / ${entry.name}`;
      const item = document.createElement("li");
      item.append(link);
      return item;
    }));
    $("asset-note").textContent = entries.length
      ? "Download the displayed versions; RigTest is excluded from game assets. Downloading is not quality acceptance. Request appearance or motion changes in chat; earlier versions are preserved."
      : "No downloadable assets yet. Links for the displayed versions will appear here after generation.";
  }

  function updateUrl() {
    const url = new URL(location.href);
    for (const key of ["character", "rig", "motion", "clip"]) url.searchParams.delete(key);
    if (desired.character) url.searchParams.set("character", desired.character);
    if (desired.rig) url.searchParams.set("rig", desired.rig.split(":")[0]);
    if (desired.motion) {
      const [id, index] = desired.motion.split(":");
      url.searchParams.set("motion", id);
      url.searchParams.set("clip", index);
    }
    history.replaceState(null, "", url);
  }

  async function render() {
    const entries = characters(builds).map(build => ({ key: build.id }));
    if (!desired.character) {
      desired.character = entries.find(entry =>
        library.some(item => item.selected_build_id === entry.key))?.key || "";
    }
    desired.character = choose(entries, desired.character, "Character");
    const character = builds.find(build => build.id === desired.character);
    if (!desired.character) {
      $("character-viewer").dataset.state = "empty";
      $("character-error").textContent = "No completed character yet. Create one in chat.";
    }
    if (shownCharacter !== desired.character) {
      shownCharacter = desired.character;
      $("character-error").textContent = "";
      $("character-viewer").dataset.buildId = desired.character;
      $("character-viewer").dataset.state = "loading";
      try {
        if (!characterViewer) characterViewer = new MotionViewer($("character-viewer"), () => {},
          message => {
            $("character-error").textContent = message;
            $("character-viewer").dataset.state = "error";
          });
        const loaded = await characterViewer.load(artifactUrl(desired.character, "character.glb"), null);
        $("character-viewer").dataset.state = loaded ? "ready" : "error";
      } catch (error) {
        $("character-error").textContent = error.message;
        $("character-viewer").dataset.state = "error";
      }
    }
    let selectedMotion;
    for (const [id, state, isRig] of [["rig", rig, true], ["motion", motion, false]]) {
      const entries = clips(builds, desired.character, isRig);
      desired[id] = choose(entries, desired[id], id);
      const selected = entries.find(entry => entry.key === desired[id]);
      if (!isRig) selectedMotion = selected;
      if (selected) await state.load(selected);
      else state.clear();
    }
    renderDownloads(character, selectedMotion);
    updateUrl();
  }

  async function refresh() {
    if (refreshing) return;
    refreshing = true;
    try {
      const responses = await Promise.all(["/api/builds", "/api/library"].map(async path => {
        const response = await fetch(path, { cache: "no-store" });
        if (!response.ok) throw new Error(`Preview request failed (${response.status}): ${path}`);
        return response.json();
      }));
      builds = responses[0].builds;
      library = responses[1].characters;
      await render();
      $("page-error").textContent = "";
    } catch (error) {
      renderDownloads();
      $("page-error").textContent = error.message;
    } finally {
      refreshing = false;
    }
  }

  await refresh();
  const section = requested.get("section");
  if (["character", "rig", "motion"].includes(section)) $(section).scrollIntoView();
  const timer = setInterval(refresh, 5000);
  window.addEventListener("pagehide", event => {
    if (event.persisted) return;
    clearInterval(timer);
    characterViewer?.dispose();
    [...rig.viewers, ...motion.viewers].forEach(viewer => viewer.dispose());
  });
}

if (typeof document !== "undefined") {
  startPreview().catch(error => {
    document.getElementById("page-error").textContent = `Preview initialization failed: ${error.message}`;
  });
}
