import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import { artifactUrl, characters, choose, clips, downloadEntries } from "../web/preview.js";

function build(id, extra = {}) {
  return {
    id, status: "succeeded", completed_at: id, request: { asset_id: "dancer", motions: [] },
    artifacts: [{ name: "character.glb" }], ...extra,
  };
}

function animation(id, parent, kind = "motion") {
  return build(id, {
    kind, character_build_id: parent,
    artifacts: [{ name: "motion-0.glb" }],
    request: { motions: [{ name: "dance" }, { name: "unfinished" }] },
  });
}

test("characters only include completed character artifacts, newest first", () => {
  assert.deepEqual(characters([
    build("b"), build("a"), build("c", { status: "draft" }), animation("d", "b"),
  ]).map(item => item.id), ["b", "a"]);
});

test("RigTest and creative clips stay separate and pin the exact character version", () => {
  const builds = [
    animation("m1", "c1"), animation("m2", "c2"), animation("r1", "c1", "rig_test"),
    animation("r2", "c2", "rig_test"), animation("failed", "c1"),
  ];
  builds.at(-1).status = "failed";
  assert.deepEqual(clips(builds, "c1", false).map(item => item.key), ["m1:0"]);
  assert.deepEqual(clips(builds, "c1", true).map(item => item.key), ["r1:0"]);
  assert.deepEqual(clips(builds, "missing", false), []);
});

test("exact version links never silently fall back to another asset", () => {
  const entries = [{ key: "new" }, { key: "old" }];
  assert.equal(choose(entries, "old", "motion"), "old");
  assert.equal(choose(entries, "", "motion"), "new");
  assert.equal(choose([], "", "motion"), "");
  assert.throws(() => choose(entries, "wrong", "motion"), /wrong/);
});

test("artifact paths are encoded", () => {
  assert.equal(artifactUrl("a/b", "motion 0.glb"), "/api/builds/a%2Fb/artifacts/motion%200.glb");
});

test("downloads include only saved artifacts for the pinned creative clip", () => {
  const character = build("c1", {
    artifacts: [{ name: "character.glb" }, { name: "preview.png" }, { name: "manifest.json" }],
  });
  const motion = animation("m1", "c1");
  motion.artifacts = ["motion-0.glb", "motion-1.glb", "source-motion-1.glb", "quality-1.json", "manifest.json"]
    .map(name => ({ name }));
  const entries = downloadEntries(character, { build: motion, index: 1 });
  assert.equal(entries.length, 7);
  assert.ok(entries.some(entry => entry.url === "/api/builds/c1/artifacts/character.glb"));
  assert.ok(entries.some(entry => entry.url === "/api/builds/m1/artifacts/motion-1.glb"));
  assert.ok(entries.some(entry => entry.url === "/api/builds/m1/artifacts/source-motion-1.glb"));
  assert.ok(entries.every(entry => !entry.url.endsWith("/motion-0.glb")));
  assert.ok(entries.every(entry => entry.buildId === "c1" || entry.buildId === "m1"));
});

test("downloads exclude missing artifacts and refuse RigTest or unrelated characters", () => {
  const character = build("c1");
  assert.deepEqual(downloadEntries(), []);
  assert.equal(downloadEntries(character).length, 1);
  assert.equal(downloadEntries(character, { build: animation("m1", "c1"), index: 0 }).length, 2);
  assert.throws(() => downloadEntries(character, { build: animation("r1", "c1", "rig_test"), index: 0 }), /RigTest/);
  assert.throws(() => downloadEntries(character, { build: animation("m2", "c2"), index: 0 }), /当前人物/);
});

test("preview is a two-by-two grid with window introductions and no controls", async () => {
  const html = await readFile(new URL("../web/index.html", import.meta.url), "utf8");
  assert.equal((html.match(/<section /g) || []).length, 3);
  for (const id of ["character", "rig", "motion"]) {
    assert.ok(html.includes(`<section id="${id}" aria-labelledby="${id}-title">`));
  }
  for (const id of ["character", "rig", "target", "source"]) {
    assert.ok(html.includes(`id="${id}-viewer" class="viewport"`));
    assert.ok(html.includes(`id="${id}-title">`));
  }
  assert.equal((html.match(/class="preview-copy"/g) || []).length, 4);
  assert.match(html, /RigTest · 绑定测试/);
  assert.match(html, /循环抬胳膊、抬腿/);
  assert.match(html, /这不是舞蹈动作/);
  assert.match(html, /grid-template-columns: repeat\(2, minmax\(0, 1fr\)\)/);
  assert.match(html, /grid-template-rows: repeat\(2, minmax\(0, 1fr\)\)/);
  assert.ok(html.includes('<footer aria-label="游戏资产下载">'));
  assert.ok(html.includes('<ul id="asset-links">'));
  assert.doesNotMatch(html, /<(?:form|textarea|label|select|button|input|output|header)\b|\/start|paid_confirmed/);
});
