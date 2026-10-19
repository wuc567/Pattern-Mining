from collections import defaultdict
from typing import List, Dict, Tuple, Iterable, Set, Optional
import bisect, time, os
import multiprocessing as mp
from pathlib import Path

class _CaseInsensitiveSet(set):
    def __contains__(self, item):
        if super().__contains__(item):
            return True
        return super().__contains__(item.swapcase()) or \
               any(item.lower() == m.lower() for m in self)
    def __or__(self, other):
        return _CaseInsensitiveSet(set(self) | set(other))
    def __ror__(self, other):
        return _CaseInsensitiveSet(set(other) | set(self))


# -------------------------
# 1) Inputs
# -------------------------
def _read_letters(s: str) -> str:
    return "".join(ch for ch in s.strip() if ch.isalpha())

def _read_file_sequences(path: str) -> List[str]:
    assert os.path.exists(path), f"File not found: {path}"
    seqs: List[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = "".join(ch for ch in line.strip() if ch.isalpha())
            if s:
                seqs.append(s)
    assert seqs, "No sequences parsed from file."
    return seqs

# -------------------------
# 2) Preparation
# -------------------------
def build_index_and_prefixGamma(seqs: List[str], Gamma: Set[str]):
    pos: List[Dict[str, List[int]]] = []
    prefGamma: List[List[int]] = []
    for s in seqs:
        pmap: Dict[str, List[int]] = defaultdict(list)
        pg = [0] * (len(s) + 1)
        gcount = 0
        for i, ch in enumerate(s):
            pmap[ch].append(i)
            if ch in Gamma:
                gcount += 1
            pg[i+1] = gcount
        pos.append(pmap)
        prefGamma.append(pg)
    return pos, prefGamma

def build_BSL(seqs: List[str], pos, prefGamma, alphabet: Iterable[str]):
    BSL    = [defaultdict(list) for _ in seqs]
    n_seqs = len(seqs)
    alphabet = [a for a in alphabet
                if any(a in pos[sid] for sid in range(n_seqs))]

    for sid in range(n_seqs):
        pmap  = pos[sid]
        pg    = prefGamma[sid]
        bsl_s = BSL[sid]
        for a in alphabet:
            if a not in pmap:
                continue
            A = pmap[a]
            for b in alphabet:
                if b not in pmap:
                    continue
                B            = pmap[b]
                pairs        = bsl_s[(a, b)]
                bisect_right = bisect.bisect_right
                for i in A:
                    jstart = bisect_right(B, i)
                    ip1    = i + 1
                    pg_ip1 = pg[ip1]
                    for j in B[jstart:]:
                        if j > ip1 and pg[j] > pg_ip1:
                            continue
                        pairs.append((i, j))
    return BSL

# -------------------------
# 3) Support calculation
# -------------------------
def _layers_for_sequence(pattern: List[str], BSL_sid):
    return [BSL_sid.get((pattern[k], pattern[k+1]), []) for k in range(len(pattern)-1)]

def _enumerate_chains_in_sequence(layers: List[List[Tuple[int, int]]]) -> List[tuple]:
    if any(len(L) == 0 for L in layers):
        return []
    n = len(layers)
    next_by_start: List[Dict[int, List[int]]] = []
    for L in layers[1:]:
        m: Dict[int, List[int]] = defaultdict(list)
        for idx, (i2, _) in enumerate(L):
            m[i2].append(idx)
        next_by_start.append(m)
    chains: List[tuple] = []
    stack = [(0, ei, ()) for ei in range(len(layers[0]))]
    while stack:
        li, ei, cur = stack.pop()
        edge      = layers[li][ei]
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

        # Push EXCLUDE-branch first (bottom of stack -> runs last).
        stack.append(("visit", idx + 1, count))

        if not conflict:
            for j in range(m):
                used_at_index[j].add(occ[j])
            stack.append(("undo", occ))
            stack.append(("visit", idx + 1, count + 1))

    if timed_out:
        _TIMED_OUT_PATTERNS.append((best, n))
    return best

def _max_disjoint_paths(layers: List[List[Tuple[int, int]]]) -> int:
    if any(not L for L in layers):
        return 0
    m = len(layers) + 1

    # Keep only nodes lying on some full path (forward, then backward pass).
    fw = [{a for a, _ in layers[0]}]
    for k in range(m - 1):
        nxt = {b for a, b in layers[k] if a in fw[k]}
        if not nxt:
            return 0
        fw.append(nxt)
    keep: List[Set[int]] = [set() for _ in range(m)]
    keep[m - 1] = fw[m - 1]
    for k in range(m - 2, -1, -1):
        keep[k] = {a for a, b in layers[k] if a in fw[k] and b in keep[k + 1]}

    S, T = 0, 1
    node_in: Dict[Tuple[int, int], int] = {}
    N = 2
    for j in range(m):
        for p in keep[j]:
            node_in[(j, p)] = N     # in-node = N, out-node = N + 1
            N += 2

    adj: List[List[int]] = [[] for _ in range(N)]
    to: List[int] = []
    cap: List[int] = []

    def add(u: int, v: int) -> None:
        adj[u].append(len(to)); to.append(v); cap.append(1)
        adj[v].append(len(to)); to.append(u); cap.append(0)

    for j in range(m):
        for p in keep[j]:
            nid = node_in[(j, p)]
            add(nid, nid + 1)                  # node capacity 1
            if j == 0:
                add(S, nid)
            if j == m - 1:
                add(nid + 1, T)
    for k in range(m - 1):
        kk, kn = keep[k], keep[k + 1]
        for a, b in layers[k]:
            if a in kk and b in kn:
                add(node_in[(k, a)] + 1, node_in[(k + 1, b)])

    flow = 0
    while True:
        level = [-1] * N
        level[S] = 0
        queue = [S]
        for u in queue:
            lu = level[u] + 1
            for e in adj[u]:
                v = to[e]
                if cap[e] and level[v] < 0:
                    level[v] = lu
                    queue.append(v)
        if level[T] < 0:
            return flow

        it = [0] * N
        while True:                            # extract paths from the level graph
            path: List[int] = []
            u = S
            while u != T:
                a = adj[u]
                advanced = False
                while it[u] < len(a):
                    e = a[it[u]]
                    v = to[e]
                    if cap[e] and level[v] == level[u] + 1:
                        path.append(e)
                        u = v
                        advanced = True
                        break
                    it[u] += 1
                if not advanced:
                    if not path:
                        break
                    e = path.pop()
                    u = to[e ^ 1]
                    it[u] += 1
            if u != T:
                break
            for e in path:
                cap[e] -= 1
                cap[e ^ 1] += 1
            flow += 1

def support_in_sequence(pattern: List[str], sid: int, BSL, pos) -> int:
    if len(pattern) == 1:
        return len(pos[sid].get(pattern[0], []))
    return _max_disjoint_paths(_layers_for_sequence(pattern, BSL[sid]))

def _support_in_sequence_by_chains(pattern: List[str], sid: int, BSL, pos) -> int:
    if len(pattern) == 1:
        return len(pos[sid].get(pattern[0], []))
    layers = _layers_for_sequence(pattern, BSL[sid])
    chains = _enumerate_chains_in_sequence(layers)
    return _select_max_nonoverlapping(chains)

def support(pattern: Iterable[str], seqs, BSL, pos, PATTERN_ALPHABET) -> int:
    p = list(pattern)
    if any(c not in PATTERN_ALPHABET for c in p):
        return 0
    total = 0
    pattern_str = "".join(p)
    for sid in range(len(seqs)):
        n_flagged_before = len(_TIMED_OUT_PATTERNS)
        total += support_in_sequence(p, sid, BSL, pos)
        if len(_TIMED_OUT_PATTERNS) > n_flagged_before:
            best_found, n_occ = _TIMED_OUT_PATTERNS[-1]
            _TIMED_OUT_PATTERNS[-1] = (pattern_str, sid, best_found, n_occ)
    return total

# -------------------------
# 4) Candidate generation 
# -------------------------
def generate_k2_from_fp1(fp1_items: Iterable[str], BSL) -> List[str]:
    items = sorted(set(fp1_items))
    out: Set[str] = set()
    for a in items:
        for b in items:
            out.add(a + b)
    return sorted(out)

def build_prefix_index(patterns_k: Iterable[str], k: int) -> Dict[str, List[str]]:
    mp: Dict[str, List[str]] = defaultdict(list)
    for p in patterns_k:
        if len(p) == k:
            mp[p[:k-1]].append(p)
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
            out.add(p + q[-1])  
    return sorted(out)

_TIMED_OUT_PATTERNS: List[tuple] = []  
_worker_seqs = None
_worker_BSL = None
_worker_pos = None
_worker_PATTERN_ALPHABET = None

def _init_worker(seqs, BSL, pos, PATTERN_ALPHABET):
    global _worker_seqs, _worker_BSL, _worker_pos, _worker_PATTERN_ALPHABET
    _worker_seqs = seqs
    _worker_BSL = BSL
    _worker_pos = pos
    _worker_PATTERN_ALPHABET = PATTERN_ALPHABET

def _support_worker(pattern_str: str) -> Tuple[str, int]:
    sup = support(list(pattern_str), _worker_seqs, _worker_BSL,
                  _worker_pos, _worker_PATTERN_ALPHABET)
    return (pattern_str, sup)

def _parallel_support_map(pool, patterns: List[str], level_label: str = "") -> List[Tuple[str, int]]:
    if not patterns:
        return []
    results = []
    total = len(patterns)
    chunksize = max(1, min(2000, total // 200))
    t_start = time.perf_counter()
    last_print = t_start
    print_every = max(10, total // 200)
    for i, (pat, sup) in enumerate(pool.imap(_support_worker, patterns, chunksize=chunksize), 1):
        results.append((pat, sup))
        now = time.perf_counter()
        if i % print_every == 0 or i == total or (now - last_print) > 5:
            print(f"  [{level_label}] {i}/{total} done -- last: {pat!r} sup={sup} "
                  f"(elapsed {now - t_start:.1f}s)", flush=True)
            last_print = now
    return results
def main():
    print("1. Please enter the input source file name (including path):")
    in_path = input().strip()

    print("2. Please enter the strong character set:")
    Gamma_str = _read_letters(input())

    print("3. Please enter the meduim character set:")
    Lambda_str = _read_letters(input())

    print("4. Please enter the week character set:")
    Omega_str = _read_letters(input())

    print("5. Please enter mim_sup:")
    try:
        MIN_SUP = int(input().strip())
    except Exception:
        MIN_SUP = 5

    print("\nThe algorithm has started running. Please wait.\n")

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
                ok = psapi.GetProcessMemoryInfo(
                    handle, ctypes.byref(counters), counters.cb
                )
                if ok:
                    return counters.PeakWorkingSetSize / (1024 * 1024)
                import subprocess
                pid = os.getpid()
                out = subprocess.check_output(
                    ["wmic", "process", "where", f"ProcessId={pid}",
                     "get", "WorkingSetSize"],
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

    Gamma  = _CaseInsensitiveSet(Gamma_str)
    Lambda = _CaseInsensitiveSet(Lambda_str)
    Omega  = _CaseInsensitiveSet(Omega_str)
    PATTERN_ALPHABET = Gamma | Lambda

    seqs = _read_file_sequences(in_path)
    pos, prefGamma = build_index_and_prefixGamma(seqs, Gamma)
    BSL = build_BSL(seqs, pos, prefGamma, PATTERN_ALPHABET)

    prep_mem_mb = max(0.0, _current_memory_mb() - mem_start_mb)

    n_workers = max(1, (os.cpu_count() or 1))
    all_patterns: List[Tuple[str, int]] = []
    results_by_k: Dict[int, List[Tuple[str, int]]] = {}
    candidates_by_k: Dict[int, int] = {}
    num_calculations = 0

    with mp.Pool(processes=n_workers, initializer=_init_worker,
                 initargs=(seqs, BSL, pos, PATTERN_ALPHABET)) as pool:
        _all_seq_chars: Set[str] = set()
        for _s in seqs:
            _all_seq_chars.update(_s)
        cands1 = sorted(c for c in _all_seq_chars if c in PATTERN_ALPHABET)
        candidates_by_k[1] = len(cands1)
        results = _parallel_support_map(pool, cands1, "k=1")
        num_calculations += len(cands1)
        fp1 = [(p, s) for p, s in results if s >= MIN_SUP]
        results_by_k[1] = sorted(fp1, key=lambda x: (-x[1], x[0]))
        all_patterns.extend(results_by_k[1])

        # NTSG-NoPruning: PIC and PIP both disabled. Candidates are tracked
        # separately from frequent patterns, and extension always uses the
        # FULL candidate set from the previous level, not just the frequent
        # subset -- this is what "no pruning" actually means (not merely
        # skipping the BSL feasibility pre-check).
        candidate_patterns_by_k: Dict[int, List[str]] = {1: cands1}

        # k = 2: generated from ALL k=1 candidates, not just frequent ones
        cands2 = generate_k2_from_fp1(cands1, BSL)
        candidate_patterns_by_k[2] = cands2
        candidates_by_k[2] = len(cands2)
        results = _parallel_support_map(pool, cands2, "k=2")
        num_calculations += len(cands2)
        freq2 = [(p, s) for p, s in results if s >= MIN_SUP]
        results_by_k[2] = sorted(freq2, key=lambda x: (-x[1], x[0]))
        all_patterns.extend(results_by_k[2])
        k = 2
        while True:
            kpatterns = candidate_patterns_by_k.get(k, [])
            if not kpatterns:
                break
            idx = build_prefix_index(kpatterns, k)
            cands = candidate_join_k_to_kplus1(kpatterns, k, idx, BSL)
            candidate_patterns_by_k[k + 1] = cands
            candidates_by_k[k + 1] = len(cands)
            if not cands:
                break
            results = _parallel_support_map(pool, cands, f"k={k+1}")
            num_calculations += len(cands)
            next_freq = [(p, s) for p, s in results if s >= MIN_SUP]
            k += 1
            results_by_k[k] = sorted(next_freq, key=lambda x: (-x[1], x[0]))
            all_patterns.extend(results_by_k[k])
            if not next_freq:
                break

    total_candidates = sum(candidates_by_k.values())
    elapsed_s = time.perf_counter() - t0
    elapsed_ms = elapsed_s * 1000.0

    current_mem_mb = _current_memory_mb()
    peak_mem_mb = current_mem_mb  # peak RSS already reflects the run's high-water mark

    _script_dir = Path(__file__).resolve().parent
    _output_dir = _script_dir / "NP_Scailabilty"
    _output_dir.mkdir(parents=True, exist_ok=True)
    _input_stem = Path(in_path).stem
    _timestamp = time.strftime("%Y%m%d_%H%M%S")
    out_path = str(_output_dir / f"NP-100cloi-8000{_input_stem}_{_timestamp}.txt")

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
                    f"LOWER BOUNDS (never overcounted), but may be undercounts. This typically "
                    f"happens for patterns with repeated characters (e.g. 'ggg') in sequences with "
                    f"many overlapping occurrences.\n\n")
            f.write("Affected patterns (name, sequence id, best found within budget, total occurrences):\n")
            for p, sid, best, n in _TIMED_OUT_PATTERNS:
                f.write(f"  {p}\tseq#{sid}\tfound {best} of {n} occurrences before budget\n")
            f.write("\n")
        f.write(f"The number of candidate patterns : {total_candidates}\n")
        f.write(f"The number of frequent patterns  : {len(all_patterns)}\n")
        f.write(f"The number of calculations       : {num_calculations}\n\n")
        f.write(f"Worker processes used             : {n_workers}\n\n")
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
    print(f"  Worker processes    : {n_workers}")
    print()
    print(f"  Time (s)            : {elapsed_s:.6f} s")
    print(f"  Time (ms)           : {elapsed_ms:.10f} ms")
    print()
    print(f"  Memory - prep phase : {prep_mem_mb:.4f} MB")
    print(f"  Memory - current    : {current_mem_mb:.4f} MB")
    print(f"  Memory - peak       : {peak_mem_mb:.4f} MB")
    print("=" * 50)
    print("\nOpen the output file to see the complete, untruncated results.")

if __name__ == "__main__":
    main()

# strong = hilkmftwv
# Meduim = rcqgpsyn
# Week  =  adeuox
# protein dataset