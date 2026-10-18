"""Single-purpose authorized V1 release; never move an existing tag."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import zipfile

REPO = "Doquocdung1609/DeFiStress"
TARGET = "2b505813d35d3cf6f4414585f9dd50f3b4281ac2"
TAG = "v1.0.0-scientific-baseline"
RUN = 39147469533
ARTIFACT = 12143897506
DIGEST = "9ea08fa155237bb460054bd28fc63ef0cca8a6bf1041fd3d0b19aba40cbade04"


def api(path, payload=None, optional=False):
    args = ["gh", "api", f"repos/{REPO}/{path}"]
    if payload is not None:
        args += ["--method", "POST", "--input", "-"]
    result = subprocess.run(args, input=json.dumps(payload) if payload is not None else None,
                            text=True, capture_output=True, check=False)
    if result.returncode:
        if optional and "HTTP 404" in result.stderr:
            return None
        raise RuntimeError(result.stderr)
    return json.loads(result.stdout)


def main():
    for number, merge in [(25, "45679b9e9abb4a7840db27482f9e757b85d8549b"), (26, TARGET)]:
        pr = api(f"pulls/{number}")
        assert pr["merged"] and pr["merge_commit_sha"] == merge
    ci = api(f"actions/runs/{RUN}")
    assert ci["head_sha"] == TARGET and ci["event"] == "push"
    assert ci["status"] == "completed" and ci["conclusion"] == "success"
    jobs = {j["name"]: j["conclusion"] for j in api(f"actions/runs/{RUN}/jobs?per_page=100")["jobs"]}
    assert all(jobs.get(n) == "success" for n in ["backend-and-simulation", "frontend", "real-rpc-config"])
    assert jobs.get("real-rpc-smoke") in {"skipped", "success"}
    art = api(f"actions/artifacts/{ARTIFACT}")
    assert art["workflow_run"]["head_sha"] == TARGET
    assert art["digest"] == "sha256:" + DIGEST and not art["expired"]
    # gh handles GitHub's authenticated redirect without printing credentials.
    data = subprocess.run(["gh", "api", f"repos/{REPO}/actions/artifacts/{ARTIFACT}/zip"],
                          capture_output=True, check=True).stdout
    assert hashlib.sha256(data).hexdigest() == DIGEST
    z = zipfile.ZipFile(io.BytesIO(data))
    assert z.testzip() is None
    suites = list(ET.fromstring(z.read("full-pytest.xml")).iter("testsuite"))
    assert sum(int(s.get("tests", 0)) for s in suites) == 226
    assert all(int(s.get(k, 0)) == 0 for s in suites for k in ["failures", "errors", "skipped"])
    env = json.loads(z.read("environment-verified.json"))
    assert env["source_commit"] == TARGET and env["run_id"] == str(RUN)
    assert env["clean_install"] == "PASS" and env["pip_check"] == "PASS"
    assert env["clean_distribution_versions_match"] and len(env["packages"]) == 105
    assert env["lock_sha256"] == "edc53ad79a7b9924bd8a9c889e053547dc620a9b1482a3551b150fcd1e08f4ff"
    assert json.loads(z.read("source-preservation.json"))["changed_paths"] == []
    records = json.loads(z.read("large-artifacts.json"))["records"]
    assert len(records) == 91 and sum(r["size_bytes"] for r in records) == 309463168
    assert all(r["status"] == "FULL_BYTES_VERIFIED" for r in records)
    assert api(f"compare/9bccafa06e289ab991535c16dc681db856bc0560...{TARGET}")["files"] == []

    ref = api(f"git/ref/tags/{TAG}", optional=True)
    if ref is None:
        obj = api("git/tags", {"tag": TAG, "message": (
            "Commander-authorized DeFiStress V1 scientific baseline. "
            f"Exact release source {TARGET}; post-merge CI {RUN} SUCCESS. "
            "Scientific lock 3f6e5302483681209e2408531eb5a15389f9fded; "
            "Blueprint 8de52bebabef376be700836e6f93a92d7394d2c3. "
            "See release notes for scientific and reproduction limitations."),
            "object": TARGET, "type": "commit"})
        api("git/refs", {"ref": "refs/tags/" + TAG, "sha": obj["sha"]})
        ref = api(f"git/ref/tags/{TAG}")
    assert ref["object"]["type"] == "tag", "Existing tag is not annotated; refuse to move it"
    tag = api("git/tags/" + ref["object"]["sha"])
    assert tag["object"] == {"type": "commit", "sha": TARGET, "url": f"https://api.github.com/repos/{REPO}/git/commits/{TARGET}"}
    assert tag["tag"] == TAG

    release = api(f"releases/tags/{TAG}", optional=True)
    if release is None:
        notes = Path("docs/research_v2/phase00/release/RELEASE_NOTES.md").read_text(encoding="utf-8")
        release = api("releases", {"tag_name": TAG, "target_commitish": TARGET,
            "name": "DeFiStress V1.0.0 — Scientific Baseline", "body": notes,
            "draft": False, "prerelease": False, "make_latest": "false"})
    assert not release["draft"] and release["tag_name"] == TAG
    assert api(f"git/ref/tags/{TAG}")["object"]["sha"] == tag["sha"]
    result = {"status": "V1_RELEASE_TAG_CREATED_AND_VERIFIED", "source_commit": TARGET,
              "annotated_tag_object": tag["sha"], "tag_url": f"https://github.com/{REPO}/tree/{TAG}",
              "release_url": release["html_url"], "release_id": release["id"],
              "postmerge_ci": ci["html_url"], "ci_artifact_sha256": DIGEST,
              "pytest": {"passed": 226, "failed": 0, "errors": 0, "skipped": 0},
              "source_modified": False, "tag_moved": False}
    Path("V1_RELEASE_RECEIPT.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
