from collections import defaultdict
from typing import List, Dict, Tuple, Iterable, Set, Optional
import bisect, time, os
from pathlib import Path

# -------------------------
# 1) Inputs
# -------------------------
def _read_letters(s: str) -> str:
    return "".join(ch for ch in s.strip().lower() if ch.isalpha())

def _read_file_sequences(path: str) -> List[str]:
    assert os.path.exists(path), f"File not found: {path}"
    seqs: List[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = "".join(ch for ch in line.strip() if ch.isalpha()).lower()
            if s:
                seqs.append(s)
    assert seqs, "No sequences parsed from file."
    return seqs

print("1. Please enter the input source file name (including path):")
in_path = input().strip()

print("2. Please enter the strong character set:")
Gamma_str = _read_letters(input())

print("3. Please enter the meduim character set:")
Lambda_str = _read_letters(input())

print("4. Please enter the week character set:")
Omega_str  = _read_letters(input())

print("5. Please enter mim_sup:")
try:
    MIN_SUP = int(input().strip())
except:
    MIN_SUP = 5

print("\nNTSG-NoBSL (No Binomial Search List variant) has started running. Please wait...........\n")

t0 = time.perf_counter()

def _current_memory_mb() -> float:
    if os.name == "nt":
        try:
            import ctypes
            from ctypes import wintypes

            class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
                _fields_ = [
                    ("cb", wintypes.DWORD),
                    ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t),
                ]

            counters = PROCESS_MEMORY_COUNTERS()
            counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
            psapi = ctypes.windll.psapi
            kernel32 = ctypes.windll.kernel32
            psapi.GetProcessMemoryInfo.argtypes = [
                wintypes.HANDLE,
                ctypes.POINTER(PROCESS_MEMORY_COUNTERS),
                wintypes.DWORD,
            ]
            psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
            kernel32.GetCurrentProcess.restype = wintypes.HANDLE

            handle = kernel32.GetCurrentProcess()
            ok = psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb)
            if ok:
                return counters.PeakWorkingSetSize / (1024 * 1024)
            import subprocess
            pid = os.getpid()
            out = subprocess.check_output(
                ["wmic", "process", "where", f"ProcessId={pid}", "get", "WorkingSetSize"],
                stderr=subprocess.DEVNULL, text=True, timeout=5,
            )
            for line in out.splitlines():
                line = line.strip()
                if line.isdigit():
                    return int(line) / (1024 * 1024)
            return 0.0
        except Exception:
            return 0.0
    else:
        try:
            import resource
            return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
        except Exception:
            return 0.0

mem_start_mb = _current_memory_mb()

# -------------------------
# 2) Three-way sets (NTSG)
# -------------------------
Gamma  = set(Gamma_str)
Lambda = set(Lambda_str)
Omega  = set(Omega_str)
PATTERN_ALPHABET = Gamma | Lambda

# -------------------------
# 3) Preparation: index only (NO BSL construction -- this is the ablation)
# -------------------------
def build_index(seqs: List[str]):
    pos_all: List[Dict[str, List[int]]] = []
    prefGamma_all: List[List[int]] = []
    for s in seqs:
        pmap: Dict[str, List[int]] = {}
        pg = [0] * (len(s) + 1)
        gcount = 0
        for i, ch in enumerate(s):
            pmap.setdefault(ch, []).append(i)
            if ch in Gamma:
                gcount += 1
            pg[i + 1] = gcount
        pos_all.append(pmap)
        prefGamma_all.append(pg)
    return pos_all, prefGamma_all

seqs = _read_file_sequences(in_path)
SEQ_LEN_SUFFIX = [0] * (len(seqs) + 1)
for _i in range(len(seqs) - 1, -1, -1):
    SEQ_LEN_SUFFIX[_i] = SEQ_LEN_SUFFIX[_i + 1] + len(seqs[_i])

pos_all, prefGamma_all = build_index(seqs)
BSL = None  

prep_mem_mb = max(0.0, _current_memory_mb() - mem_start_mb)

# -------------------------
# 4) Support calculation (NONOVERLAP, direct scan, no BSL)
# -------------------------
num_calculations = 0
_TIMED_OUT_PATTERNS: List[tuple] = []  

def _direct_layer(a: str, b: str, sid: int) -> List[Tuple[int, int]]:

    pmap = pos_all[sid]
    pg = prefGamma_all[sid]
    if a not in pmap or b not in pmap:
        return []
    A = pmap[a]
    B = pmap[b]
    pairs = []
    for i in A:
        required_gc = pg[i + 1]
        lo = bisect.bisect_right(B, i)
        for j in B[lo:]:
            if pg[j] == required_gc:
                pairs.append((i, j))
            elif pg[j] > required_gc:
                break  # prefix count only increases -- no valid j ahead
    return pairs

def _enumerate_chains_in_sequence(pattern: List[str], sid: int) -> List[tuple]:
    layers = [_direct_layer(pattern[k], pattern[k + 1], sid) for k in range(len(pattern) - 1)]
    if any(len(L) == 0 for L in layers):
        return []
    n = len(layers)
    next_by_start: List[Dict[int, List[int]]] = []
    for L in layers[1:]:
        m = defaultdict(list)
        for idx, (i2, _) in enumerate(L):
            m[i2].append(idx)
        next_by_start.append(m)
    chains: List[tuple] = []
    stack = [(0, ei, ()) for ei in range(len(layers[0]))]
    while stack:
        li, ei, cur = stack.pop()
        edge = layers[li][ei]
        new_chain = cur + (edge,)
        if li == n - 1:
            chains.append(new_chain)
        else:
            j = edge[1]
            for nxt_ei in next_by_start[li].get(j, []):
                stack.append((li + 1, nxt_ei, new_chain))
    return chains

def _select_max_nonoverlapping(chains: List[tuple]) -> int:
    if not chains:
        return 0

    m = len(chains[0]) + 1

    if m == 2:
        adj: Dict[int, List[int]] = defaultdict(list)
        for ch in chains:
            a, b = ch[0]
            adj[a].append(b)
        match_right: Dict[int, int] = {}

        def try_augment(a: int, visited: Set[int]) -> bool:
            for b in adj[a]:
                if b in visited:
                    continue
                visited.add(b)
                if b not in match_right or try_augment(match_right[b], visited):
                    match_right[b] = a
                    return True
            return False

        count = 0
        for a in adj:
            visited: Set[int] = set()
            if try_augment(a, visited):
                count += 1
        return count

    occs: List[Tuple[int, ...]] = []
    for ch in chains:
        occ = (ch[0][0],) + tuple(e[1] for e in ch)
        occs.append(occ)

    n = len(occs)

    def _conflicts_pair(a: Tuple[int, ...], b: Tuple[int, ...]) -> bool:
        return any(a[j] == b[j] for j in range(m))
    conflict_count = [
        sum(1 for j in range(n) if i != j and _conflicts_pair(occs[i], occs[j]))
        for i in range(n)
    ]
    order = sorted(range(n), key=lambda i: -conflict_count[i])
    occs = [occs[i] for i in order]

    used_at_index: List[Set[int]] = [set() for _ in range(m)]
    best = 0

    t_start = time.perf_counter()
    TIME_BUDGET_S = 5.0
    timed_out = False

    stack: List[tuple] = [("visit", 0, 0)]
    steps = 0

    while stack:
        frame = stack.pop()

        if frame[0] == "undo":
            occ_to_undo = frame[1]
            for j in range(m):
                used_at_index[j].discard(occ_to_undo[j])
            continue

        _, idx, count = frame

        steps += 1
        if steps % 256 == 0 and (time.perf_counter() - t_start) > TIME_BUDGET_S:
            timed_out = True
            break

        if count + (n - idx) <= best:
            continue
        if idx == n:
            if count > best:
                best = count
            continue

        occ = occs[idx]
        conflict = any(occ[j] in used_at_index[j] for j in range(m))

        stack.append(("visit", idx + 1, count))

        if not conflict:
            for j in range(m):
                used_at_index[j].add(occ[j])
            stack.append(("undo", occ))
            stack.append(("visit", idx + 1, count + 1))

    if timed_out:
        _TIMED_OUT_PATTERNS.append((best, n))
    return best

def support_in_sequence(pattern: List[str], sid: int, BSL) -> int:
    if len(pattern) == 1:
        return len(pos_all[sid].get(pattern[0], []))
    chains = _enumerate_chains_in_sequence(pattern, sid)
    return _select_max_nonoverlapping(chains)

def support(pattern: Iterable[str], seqs, BSL) -> int:
    global num_calculations
    p = list(pattern)
    if any(c not in PATTERN_ALPHABET for c in p):
        return 0
    num_calculations += 1
    n_seqs = len(seqs)
    plen = max(1, len(p))
    total = 0
    pattern_str = "".join(p)
    for sid in range(n_seqs):
        n_flagged_before = len(_TIMED_OUT_PATTERNS)
        total += support_in_sequence(p, sid, BSL)
        if len(_TIMED_OUT_PATTERNS) > n_flagged_before:
            best_found, n_occ = _TIMED_OUT_PATTERNS[-1]
            _TIMED_OUT_PATTERNS[-1] = (pattern_str, sid, best_found, n_occ)
        remaining_upper_bound = SEQ_LEN_SUFFIX[sid + 1] // plen
        if total + remaining_upper_bound < MIN_SUP:
            return total
    return total

# -------------------------
# 5) Candidate generation
# -------------------------
def pair_feasible_direct(a: str, b: str) -> bool:
    for sid in range(len(seqs)):
        if _direct_layer(a, b, sid):
            return True
    return False

_feasible_pairs: Set[tuple] = set()
for _a in PATTERN_ALPHABET:
    for _b in PATTERN_ALPHABET:
        if pair_feasible_direct(_a, _b):
            _feasible_pairs.add((_a, _b))

def bsl_feasible_every_pair(c: str, BSL) -> bool:
    for i in range(len(c) - 1):
        if (c[i], c[i + 1]) not in _feasible_pairs:
            return False
    return True

def generate_k2_from_fp1(fp1_items: Iterable[str], BSL) -> List[str]:
    items = sorted(set(fp1_items))
    out: Set[str] = set()
    for a in items:
        for b in items:
            c = a + b
            if bsl_feasible_every_pair(c, BSL):
                out.add(c)
    return sorted(out)

def build_prefix_index(patterns_k: Iterable[str], k: int) -> Dict[str, List[str]]:
    mp: Dict[str, List[str]] = defaultdict(list)
    for p in patterns_k:
        if len(p) == k:
            mp[p[:k - 1]].append(p)
    return mp

def candidate_join_k_to_kplus1(patterns_k: Iterable[str], k: int, prefix_index, BSL) -> List[str]:
    out: Set[str] = set()
    for p in patterns_k:
        if len(p) != k:
            continue
        sfx = p[1:]
        bucket = prefix_index.get(sfx)
        if not bucket:
            continue
        for q in bucket:
            c = p + q[-1]
            new_pair = (p[-1], q[-1])
            if new_pair in _feasible_pairs:
                out.add(c)
    return sorted(out)

# -------------------------
# 6) Mining loop (k = 1 -> )
# -------------------------
all_patterns:    List[Tuple[str, int]]            = []
results_by_k:    Dict[int, List[Tuple[str, int]]] = {}
candidates_by_k: Dict[int, int]                   = {}

def sequential_map(patterns, level_label=""):
    results = []
    total = len(patterns)
    t_batch = time.perf_counter()
    for i, pat in enumerate(patterns, 1):
        sup = support(list(pat), seqs, BSL)
        results.append((pat, sup))
        if i % 50 == 0 or i == total:
            print(f"  [{level_label}] {i}/{total} done -- last: {pat!r} sup={sup} "
                  f"(elapsed {time.perf_counter()-t_batch:.1f}s)", flush=True)
            t_batch = time.perf_counter()
    return results

cands1 = sorted(PATTERN_ALPHABET)
candidates_by_k[1] = len(cands1)
results = sequential_map(cands1, "k=1")
fp1 = [(p, s) for p, s in results if s >= MIN_SUP]
results_by_k[1] = sorted(fp1, key=lambda x: (-x[1], x[0]))
all_patterns.extend(results_by_k[1])

k1_items = [p for p, _ in results_by_k.get(1, [])]
if k1_items:
    cands2 = generate_k2_from_fp1(k1_items, BSL)
    candidates_by_k[2] = len(cands2)
    results = sequential_map(cands2, "k=2")
    freq2 = [(p, s) for p, s in results if s >= MIN_SUP]
else:
    candidates_by_k[2] = 0
    freq2 = []
results_by_k[2] = sorted(freq2, key=lambda x: (-x[1], x[0]))
all_patterns.extend(results_by_k[2])

k = 2
while True:
    kpatterns = [p for p, _ in results_by_k.get(k, [])]
    if not kpatterns:
        break
    idx = build_prefix_index(kpatterns, k)
    cands = candidate_join_k_to_kplus1(kpatterns, k, idx, BSL)
    candidates_by_k[k + 1] = len(cands)
    if not cands:
        break
    results = sequential_map(cands, f"k={k+1}")
    next_freq = [(p, s) for p, s in results if s >= MIN_SUP]
    if not next_freq:
        break
    k += 1
    results_by_k[k] = sorted(next_freq, key=lambda x: (-x[1], x[0]))
    all_patterns.extend(results_by_k[k])

total_candidates = sum(candidates_by_k.values())
elapsed_s = time.perf_counter() - t0
elapsed_ms = elapsed_s * 1000.0
current_mem_mb = _current_memory_mb()
peak_mem_mb = current_mem_mb

# -------------------------
# 7) Output
# -------------------------
_script_dir = Path(__file__).resolve().parent
_output_dir = _script_dir / "Scaliablity-coli-NoBSL"
_output_dir.mkdir(parents=True, exist_ok=True)
_input_stem = Path(in_path).stem
_timestamp = time.strftime("%Y%m%d_%H%M%S")
out_path = str(_output_dir / f"coli-100_8000{_input_stem}_{_timestamp}.txt")

with open(out_path, "w", encoding="utf-8") as f:
    f.write("Mining Result:\n\n")
    for L in sorted(results_by_k):
        for p, s in results_by_k[L]:
            f.write(f"{p}\t{s}\n")
    f.write("\n")

    f.write("Level-wise Summary:\n")
    f.write(f"{'Level':<8} {'Candidates':>12} {'Frequent':>10}\n")
    f.write("-" * 32 + "\n")
    for L in sorted(results_by_k):
        nc = candidates_by_k.get(L, 0)
        nf = len(results_by_k[L])
        f.write(f"{L:<8} {nc:>12} {nf:>10}\n")
    f.write("-" * 32 + "\n")
    f.write(f"{'Total':<8} {total_candidates:>12} {len(all_patterns):>10}\n\n")

    f.write("=" * 50 + "\n")
    f.write("Performance Summary\n")
    f.write("=" * 50 + "\n")
    if _TIMED_OUT_PATTERNS:
        affected_patterns = sorted(set(p for p, sid, best, n in _TIMED_OUT_PATTERNS))
        f.write(f"\nNOTE: {len(_TIMED_OUT_PATTERNS)} pattern-sequence combination(s), covering "
                f"{len(affected_patterns)} distinct pattern(s), hit the time budget during "
                f"nonoverlapping selection. Their reported support values are safe, guaranteed "
                f"LOWER BOUNDS (never overcounted), but may be undercounts.\n\n")
        f.write("Affected patterns (name, sequence id, best found within budget, total occurrences):\n")
        for p, sid, best, n in _TIMED_OUT_PATTERNS:
            f.write(f"  {p}\tseq#{sid}\tfound {best} of {n} occurrences before budget\n")
        f.write("\n")
    f.write(f"The number of candidate patterns : {total_candidates}\n")
    f.write(f"The number of frequent patterns  : {len(all_patterns)}\n")
    f.write(f"The number of calculations       : {num_calculations}\n\n")
    f.write(f"The time-consuming               : {elapsed_s:.6f} s\n")
    f.write(f"The time-consuming               : {elapsed_ms:.10f} ms\n\n")
    f.write(f"Memory - preprocessing phase     : {prep_mem_mb:.4f} MB\n")
    f.write(f"Memory - current (end of run)    : {current_mem_mb:.4f} MB\n")
    f.write(f"Memory - peak (entire run)       : {peak_mem_mb:.4f} MB\n")

print(f"Done. All frequent patterns saved: {out_path}")
print()
print("Level-wise Summary:")
print(f"  {'Level':<6} {'Candidates':>12} {'Frequent':>10}")
print("  " + "-" * 30)
for L in sorted(results_by_k):
    nc = candidates_by_k.get(L, 0)
    nf = len(results_by_k[L])
    print(f"  {L:<6} {nc:>12} {nf:>10}")
print("  " + "-" * 30)
print(f"  {'Total':<6} {total_candidates:>12} {len(all_patterns):>10}")
print()
print("=" * 50)
print("Performance Summary")
print("=" * 50)
print(f"  Candidate patterns  : {total_candidates}")
print(f"  Frequent patterns   : {len(all_patterns)}")
print(f"  Calculations        : {num_calculations}")
print()
print(f"  Time (s)            : {elapsed_s:.6f} s")
print(f"  Time (ms)           : {elapsed_ms:.10f} ms")
print()
print(f"  Memory - prep phase : {prep_mem_mb:.4f} MB")
print(f"  Memory - current    : {current_mem_mb:.4f} MB")
print(f"  Memory - peak       : {peak_mem_mb:.4f} MB")
print("=" * 50)
print("\nOpen the output file to see the complete, untruncated results.")

# strong = hilkmftwv
# Meduim = rcqgpsyn
# Week  =  adeuox
# protein dataset
# Γ = HIJhij
# Λ = EFGefg
# Ω = ABCDabcd

