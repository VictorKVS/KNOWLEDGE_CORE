# -*- coding: utf-8 -*-
"""
FATHER / KNOWLEDGE_CORE
Regulatory importer v5 (stage-safe Windows paths).

Fixes from v3/v4:
- Git-tracked law files use SHA-only short filenames, so Windows/Git path length is safe.
- Empty (0-byte) "documents" are blocked from publication and recorded in manifests.
- Reuses an existing KNOWLEDGE_CORE clone even if the only untracked files are from a previous failed import.
- Stages only files created by the current run, so stale overlong filenames from prior failed runs are ignored.
- Source files are never deleted or moved.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

INVENTORY = Path(r"C:\Users\1\Documents\Codex\2026-08-26\new-chat\outputs\library_inventory.csv")
BRANCH = "agent/local-laws-gost-kb-import"
REMOTE = "https://github.com/VictorKVS/KNOWLEDGE_CORE.git"
PREFERRED_REPO = Path(r"G:\1\KNOWLEDGE_CORE")
G1 = Path(r"G:\1")
LOCAL_PACK = Path(r"G:\1\REGULATORY_SOURCE_PACK\RU_REGULATORY_ALL")
ALLOWED_EXT = {".pdf", ".doc", ".docx", ".odt", ".rtf", ".txt", ".html", ".htm", ".xml"}
KNOWN_NUMERIC_STEMS = {"4","21","30","63","77","92","98","117","126","137","140","141","149","152","178","179","180","187","211","230","235","239","240","246","303","323","340","356","378","687","785","819","954","1119","1154","1284","1981"}
GOST_RX = re.compile(r"(?i)(?:^|[^А-ЯA-Z])(?:ГОСТ|GOST)\s*(?:Р|R)?\s*(?:(?:ИСО|ISO)(?:[/_\- ](?:МЭК|IEC))?\s*)?(?:ТО\s*)?\d{4,6}(?:[.\-]\d+)*(?:-\d{2,4})?")
LAW_PATTERNS = [re.compile(x) for x in [r"(?i)\b\d{1,4}\s*[-–—]?\s*ФЗ\b",r"(?i)Федеральн\w*\s+закон",r"(?i)Постановлен\w*\s+Правительств",r"(?i)\bПП\s*РФ\b",r"(?i)Указ\s+Президент",r"(?i)Распоряжен\w*\s+Правительств",r"(?i)Приказ\s+(?:ФСТЭК|ФСБ|Роскомнадзор|РКН|Минздрав|Минтранс|Минпромторг|Минэкономразвит\w*|Минэнерго|Минцифры|СФР|Росфинмониторинг)",r"(?i)(?:ФСТЭК|ФСБ|РКН|Роскомнадзор).*?(?:№|N)\s*\d+"]]
GOST_ID_PATTERNS = [re.compile(x) for x in [r"(?i)(ГОСТ\s*Р\s*ИСО[/_ ]?МЭК\s*ТО\s*\d{4,6}(?:[.\-]\d+)*(?:-\d{2,4})?)",r"(?i)(ГОСТ\s*Р\s*ИСО[/_ ]?МЭК\s*\d{4,6}(?:[.\-]\d+)*(?:-\d{2,4})?)",r"(?i)(ГОСТ\s*Р\s*\d{4,6}(?:[.\-]\d+)*(?:-\d{2,4})?)",r"(?i)(ГОСТ\s*\d{4,6}(?:[.\-]\d+)*(?:-\d{2,4})?)",r"(?i)(GOST[-_ ]?R[-_ ]?\d{4,6}(?:[.\-]\d+)*(?:[-_]\d{2,4})?)"]]
IMPORT_PREFIX = "security-knowledge/corpus/ru-local-regulatory-import/"

def step(text):
    print("\n" + "="*72 + "\n" + text + "\n" + "="*72)

def run(args, cwd=None, check=True):
    p = subprocess.run([str(x) for x in args], cwd=str(cwd) if cwd else None, text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if p.stdout: print(p.stdout, end="" if p.stdout.endswith("\n") else "\n")
    if check and p.returncode != 0: raise RuntimeError(f"Command failed ({p.returncode}): {' '.join(map(str,args))}")
    return p

def capture(args,cwd=None):
    p=subprocess.run([str(x) for x in args],cwd=str(cwd) if cwd else None,text=True,encoding="utf-8",errors="replace",stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    return p.stdout.strip() if p.returncode==0 else ""

def sha256_file(path,chunk=8*1024*1024):
    h=hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b=f.read(chunk)
            if not b: break
            h.update(b)
    return h.hexdigest()

def safe_piece(s,max_len=72):
    s=re.sub(r'[<>:"/\\|?*]+',"_",s); s=re.sub(r"\s+"," ",s).strip().rstrip(".")
    return (s or "REVIEW")[:max_len].rstrip()

def local_pack_name(kind,identity,digest,ext): return f"{kind}__{safe_piece(identity,72)}__{digest[:12]}{ext.lower()}"
def git_law_name(digest,ext): return f"{digest}{ext.lower()}"

def read_inventory(path):
    raw=path.read_text(encoding="utf-8-sig",errors="replace"); lines=raw.splitlines(); first=lines[0] if lines else ""; counts={";":first.count(";"),",":first.count(","),"\t":first.count("\t")}; delim=max(counts,key=counts.get); print(f"CSV delimiter: {repr(delim)}"); return list(csv.DictReader(lines,delimiter=delim))

def row_value(row,names):
    low={str(k).lower():v for k,v in row.items()}
    for n in names:
        if n in row and row[n] is not None: return str(row[n])
        v=low.get(n.lower())
        if v is not None: return str(v)
    return ""

def detect_kind(filename,full_path):
    if GOST_RX.search(filename): return "GOST"
    if any(rx.search(filename) for rx in LAW_PATTERNS): return "LAW"
    if "\\библиотека\\разобрать\\" in full_path.replace("/","\\").lower() and Path(filename).stem in KNOWN_NUMERIC_STEMS: return "LAW"
    return None

def detect_identity(kind,filename):
    if kind=="GOST":
        for rx in GOST_ID_PATTERNS:
            m=rx.search(filename)
            if m: return re.sub(r"\s+"," ",m.group(1).replace("_"," ")).strip().upper()
        return "GOST_IDENTITY_REVIEW_REQUIRED"
    m=re.search(r"(?i)(\d{1,4})\s*[-–—]?\s*ФЗ",filename)
    if m:return f"{m.group(1)}-ФЗ"
    m=re.search(r"(?i)(?:ПП\s*РФ|Постановлен\w*\s+Правительств\w*).*?(?:№|N)?\s*(\d{1,5})",filename)
    if m:return f"ПП РФ №{m.group(1)}"
    m=re.search(r"(?i)Приказ\s+([^№N\d]{2,50}).*?(?:№|N)?\s*(\d{1,5})",filename)
    if m:return f"ПРИКАЗ {re.sub(r'\s+',' ',m.group(1)).strip()} №{m.group(2)}"
    return "LAW_IDENTITY_REVIEW_REQUIRED"

def is_git_repo(path): return path.exists() and (path/".git").exists()
def origin_ok(path): return "VictorKVS/KNOWLEDGE_CORE" in capture(["git","remote","get-url","origin"],cwd=path).replace("\\","/")
def status_paths(path):
    out=capture(["git","status","--porcelain","-uall"],cwd=path); return [line[3:].strip().strip('"').replace("\\","/") for line in out.splitlines() if len(line)>=4]
def generated_only_dirty(path):
    paths=status_paths(path); return bool(paths) and all(p.startswith(IMPORT_PREFIX) for p in paths)

def prepare_repo():
    candidates=[]
    if is_git_repo(PREFERRED_REPO): candidates.append(PREFERRED_REPO)
    if G1.exists():
        for pat in ("KNOWLEDGE_CORE_IMPORT_*","KNOWLEDGE_CORE_GIT*"): candidates += [p for p in G1.glob(pat) if p.is_dir() and is_git_repo(p)]
    candidates=sorted({str(p).lower():p for p in candidates}.values(),key=lambda p:p.stat().st_mtime,reverse=True)
    for repo in candidates:
        if not origin_ok(repo): continue
        dirty=status_paths(repo)
        if dirty and not generated_only_dirty(repo): continue
        print(f"Candidate clone: {repo}"); run(["git","fetch","origin",BRANCH],cwd=repo)
        head=capture(["git","rev-parse","HEAD"],cwd=repo); remote_head=capture(["git","rev-parse",f"origin/{BRANCH}"],cwd=repo)
        if dirty:
            if head==remote_head: print("Reusing clone with only prior generated import files; they are NOT deleted."); return repo
            continue
        sw=run(["git","switch",BRANCH],cwd=repo,check=False)
        if sw.returncode!=0: run(["git","switch","-c",BRANCH,"--track",f"origin/{BRANCH}"],cwd=repo)
        run(["git","pull","--ff-only","origin",BRANCH],cwd=repo); return repo
    ts=datetime.now().strftime("%Y%m%d-%H%M%S"); repo=G1/f"KNOWLEDGE_CORE_IMPORT_{ts}"; run(["git","clone","--branch",BRANCH,"--single-branch",REMOTE,repo]); return repo

def copy_verified(src,dst,expected):
    dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists() and dst.stat().st_size>0 and sha256_file(dst)==expected:return
    shutil.copy2(src,dst)
    if sha256_file(dst)!=expected: raise RuntimeError(f"SHA-256 mismatch after copy: {src} -> {dst}")

def write_csv(path,rows,fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter=";"); w.writeheader(); [w.writerow({k:r.get(k,"") for k in fields}) for r in rows]

def write_jsonl(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text("".join(json.dumps(r,ensure_ascii=False,separators=(",",":"))+"\n" for r in rows),encoding="utf-8")

def main():
    step("FATHER REGULATORY IMPORT V5 — STAGE-SAFE")
    if not INVENTORY.exists(): raise FileNotFoundError(f"Inventory not found: {INVENTORY}")
    if shutil.which("git") is None: raise RuntimeError("Git not found in PATH.")
    step("1. PREPARE KNOWLEDGE_CORE"); repo=prepare_repo(); print(f"Using repository: {repo}")
    step("2. READ INVENTORY"); rows=read_inventory(INVENTORY); print(f"Inventory rows: {len(rows)}")
    step("3. FIND + HASH LAWS AND GOSTS"); candidates=[]; hashed=0
    for row in rows:
        full=row_value(row,["full_path","path","fullname","FullName"])
        if not full: continue
        name=row_value(row,["filename","name","Name"]) or Path(full).name
        ext=(row_value(row,["extension","ext","Extension"]) or Path(full).suffix).lower()
        if ext not in ALLOWED_EXT: continue
        kind=detect_kind(name,full)
        if not kind: continue
        ident=detect_identity(kind,name); src=Path(full)
        if not src.exists(): candidates.append(dict(kind=kind,identity=ident,filename=name,source=full,exists=False,size_bytes=0,sha256="")); continue
        digest=sha256_file(src); candidates.append(dict(kind=kind,identity=ident,filename=name,source=full,exists=True,size_bytes=src.stat().st_size,sha256=digest)); hashed+=1
        if hashed%20==0: print(f"Hashed: {hashed}")
    print(f"Regulatory candidates: {len(candidates)}")
    step("4. BUILD LOCAL PACK + DEDUP"); LOCAL_PACK.mkdir(parents=True,exist_ok=True); ts=datetime.now().strftime("%Y%m%d-%H%M%S"); git_root=repo/"security-knowledge"/"corpus"/"ru-local-regulatory-import"; run_root=git_root/"runs"/ts; law_root=git_root/"laws"; manifest_root=run_root/"manifests"; seen={}; local=[]; public=[]; created=[]
    stats={"generated_at":datetime.now().astimezone().isoformat(),"inventory_rows":len(rows),"regulatory_candidates":len(candidates),"law_candidate_files":0,"gost_candidate_files":0,"unique_sha256_files":0,"exact_duplicate_files":0,"empty_files_blocked":0,"missing_source_files":0,"unique_bytes":0,"github_law_files":0,"github_binary_too_large":0,"gost_public_binary_files":0,"source_files_deleted":0,"source_files_moved":0}
    for item in sorted(candidates,key=lambda x:(x["kind"],x["identity"],x["source"])):
        stats["gost_candidate_files" if item["kind"]=="GOST" else "law_candidate_files"]+=1
        if not item["exists"]: stats["missing_source_files"]+=1; continue
        if item["size_bytes"]==0: stats["empty_files_blocked"]+=1; continue
        d=item["sha256"]
        if d in seen: stats["exact_duplicate_files"]+=1; continue
        ext=Path(item["filename"]).suffix.lower(); packed=local_pack_name(item["kind"],item["identity"],d,ext); seen[d]=packed; src=Path(item["source"]); copy_verified(src,LOCAL_PACK/packed,d); stats["unique_sha256_files"]+=1; stats["unique_bytes"]+=item["size_bytes"]
        local.append({"kind":item["kind"],"identity":item["identity"],"sha256":d,"size_bytes":item["size_bytes"],"source_path":item["source"],"source_name":item["filename"],"packed_name":packed,"duplicate_of":"","status":"LOCAL_COPIED_SHA256_VERIFIED"})
        if item["kind"]=="GOST": policy="METADATA_ONLY_PUBLIC_REPO"
        elif item["size_bytes"]<=95000000:
            policy="PUBLIC_NPA_FILE"; tracked=law_root/d[:2]/git_law_name(d,ext); copy_verified(src,tracked,d); created.append(tracked); stats["github_law_files"]+=1
        else: policy="GITHUB_BINARY_TOO_LARGE"; stats["github_binary_too_large"]+=1
        public.append({"kind":item["kind"],"identity":item["identity"],"sha256":d,"size_bytes":item["size_bytes"],"original_filename":item["filename"],"source_path_redacted":True,"github_policy":policy,"status":"REGISTERED"})
    step("5. WRITE MANIFESTS"); write_csv(LOCAL_PACK/"_manifest.csv",local,["kind","identity","sha256","size_bytes","source_path","source_name","packed_name","duplicate_of","status"]); write_jsonl(LOCAL_PACK/"_manifest.jsonl",local); (LOCAL_PACK/"_stats.json").write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding="utf-8"); write_csv(manifest_root/"regulatory-manifest.csv",public,["kind","identity","sha256","size_bytes","original_filename","source_path_redacted","github_policy","status"]); write_jsonl(manifest_root/"regulatory-manifest.jsonl",public); (manifest_root/"stats.json").write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding="utf-8"); (run_root/"README.md").write_text(f"# Local RU regulatory import — {ts}\n\nStage-safe v5. Full GOST binaries remain local. Source files deleted: 0. Source files moved: 0.\n",encoding="utf-8")
    step("6. COMMIT + PUSH")
    if not capture(["git","config","user.name"],cwd=repo): run(["git","config","user.name","VictorKVS"],cwd=repo)
    if not capture(["git","config","user.email"],cwd=repo): run(["git","config","user.email","VictorKVS@users.noreply.github.com"],cwd=repo)
    run(["git","add","--",str(run_root.relative_to(repo))],cwd=repo)
    rel=[str(p.relative_to(repo)) for p in created]
    for i in range(0,len(rel),20):
        batch=rel[i:i+20]
        if batch: run(["git","add","--",*batch],cwd=repo)
    staged=capture(["git","diff","--cached","--name-only"],cwd=repo)
    if staged: run(["git","commit","-m",f"Import local regulatory corpus {ts}"],cwd=repo); run(["git","push","origin",BRANCH],cwd=repo); print("GitHub PUSH: OK")
    else: print("Nothing new to commit.")
    step("7. FINISHED"); print(json.dumps(stats,ensure_ascii=False,indent=2)); print(f"LOCAL PACK: {LOCAL_PACK}"); print(f"GIT REPOSITORY: {repo}")

if __name__=="__main__": main()
