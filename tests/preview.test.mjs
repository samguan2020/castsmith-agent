import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import { artifactUrl, characters, choose, clips } from "../web/preview.js";

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
  assert.doesNotMatch(html, /<(?:form|textarea|label|select|button|input|output|header|footer)\b|\/start|paid_confirmed/);
});
