import argparse
import math
import time
from collections import Counter
from pathlib import Path


NA = -1


class STNode:
    __slots__ = (
        "start",
        "depth",
        "label",
        "parent",
        "slink",
        "child",
        "is_candidate",
        "left_max",
        "visited",
        "leaf_count",
    )

    def __init__(self, start=0, depth=0, label=0):
        self.start = start
        self.depth = depth
        self.label = label
        self.parent = None
        self.slink = None
        self.child = {}
        self.is_candidate = False
        self.left_max = True
        self.visited = False
        self.leaf_count = 0

    def get_child(self, label):
        return self.child.get(label)

    def set_suffix_link(self, node):
        self.slink = node

    def add_child(self, node, label):
        self.child[label] = node
        node.label = label
        node.parent = self


class WaveletNode:
    __slots__ = (
        "size",
        "bits",
        "rank1_prefix",
        "lo",
        "hi",
        "left",
        "right",
    )

    def __init__(self, lo, hi):
        self.size = 0
        self.bits = []
        self.rank1_prefix = []
        self.lo = lo
        self.hi = hi
        self.left = None
        self.right = None


class WaveletTreeInt:

    def __init__(self, values):
        if not values:
            self.sigma = 0
            self._root = None
            return

        self.sigma = max(values) + 1
        max_bits = max((self.sigma - 1).bit_length(), 1)
        self._root = self._build(values, 0, (1 << max_bits) - 1, max_bits - 1)

    def _build(self, values, lo, hi, bit_position):
        node = WaveletNode(lo, hi)
        node.size = len(values)
        if lo == hi or not values:
            return node

        bits = []
        rank1_prefix = []
        left_values = []
        right_values = []
        ones = 0

        for value in values:
            bit = (value >> bit_position) & 1
            bits.append(bit)
            if bit:
                ones += 1
                right_values.append(value)
            else:
                left_values.append(value)
            rank1_prefix.append(ones)

        node.bits = bits
        node.rank1_prefix = rank1_prefix
        middle = (lo + hi) // 2
        if left_values:
            node.left = self._build(
                left_values,
                lo,
                middle,
                bit_position - 1,
            )
        if right_values:
            node.right = self._build(
                right_values,
                middle + 1,
                hi,
                bit_position - 1,
            )
        return node

    def root(self):
        return self._root

    @staticmethod
    def is_leaf(node):
        return node.lo == node.hi

    @staticmethod
    def expand(node):
        return node.left, node.right

    @staticmethod
    def bit_vector(node):
        return node.bits

    @staticmethod
    def rank_bit(bit, index, node):
        if index < 0 or node.size == 0:
            return 0
        if index >= node.size:
            index = node.size - 1
        ones = node.rank1_prefix[index]
        return ones if bit else index + 1 - ones

    @staticmethod
    def select_bit(bit, occurrence, node):
        if occurrence <= 0:
            raise ValueError("Wavelet-tree select uses one-based occurrences")

        available = WaveletTreeInt.rank_bit(bit, node.size - 1, node)
        if occurrence > available:
            raise ValueError(
                f"Bit {bit} does not occur {occurrence} times in this node"
            )

        low = 0
        high = node.size - 1
        while low < high:
            middle = (low + high) // 2
            if WaveletTreeInt.rank_bit(bit, middle, node) >= occurrence:
                high = middle
            else:
                low = middle + 1
        return low


class OPST:

    def __init__(self, sequence, range_threshold=512):
        self.w = list(sequence)
        self.n = len(self.w)
        self.range_threshold = range_threshold
        self.terminate_label = 2 * self.n + 1
        self.wavelet_flag = False
        self.wavelet_tree = None
        self.wavelet_time = 0.0
        self.node_count = 1
        self.maximal_candidate_node_count = 0

        self.root = STNode(label=self.terminate_label)
        self.root.set_suffix_link(self.root)
        self._construct()

    @staticmethod
    def _order_encode(values):
        ranks = {value: rank for rank, value in enumerate(sorted(set(values)))}
        return [ranks[value] for value in values]

    def _construct_wavelet_tree(self):
        start = time.perf_counter()
        encoded = self._order_encode(self.w)
        self.wavelet_tree = WaveletTreeInt(encoded)
        self.wavelet_time = time.perf_counter() - start
        self.wavelet_flag = True

    def maximum_position(self, node, left, right):
        wt = self.wavelet_tree
        if wt.is_leaf(node):
            return right

        if wt.rank_bit(1, left, node) == wt.rank_bit(1, right, node):
            child = wt.expand(node)[0]
            child_position = self.maximum_position(
                child,
                wt.rank_bit(0, left, node) - 1,
                wt.rank_bit(0, right, node) - 1,
            )
            return wt.select_bit(0, child_position + 1, node)

        child = wt.expand(node)[1]
        child_position = self.maximum_position(
            child,
            wt.rank_bit(1, left, node) - 1,
            wt.rank_bit(1, right, node) - 1,
        )
        return wt.select_bit(1, child_position + 1, node)

    def predecessor_wavelet(self, node, left, right):
        if left == right:
            return NA
        if self.wavelet_tree.is_leaf(node):
            return right

        bit = self.wavelet_tree.bit_vector(node)[right + 1]
        child = self.wavelet_tree.expand(node)[bit]
        position = self.predecessor_wavelet(
            child,
            self.wavelet_tree.rank_bit(bit, left, node) - 1,
            self.wavelet_tree.rank_bit(bit, right, node) - 1,
        )
        if position != NA:
            return self.wavelet_tree.select_bit(bit, position + 1, node)

        if (
            bit == 0
            or self.wavelet_tree.rank_bit(0, left, node)
            == self.wavelet_tree.rank_bit(0, right, node)
        ):
            return NA

        left_child = self.wavelet_tree.expand(node)[0]
        maximum = self.maximum_position(
            left_child,
            self.wavelet_tree.rank_bit(0, left, node) - 1,
            self.wavelet_tree.rank_bit(0, right, node) - 1,
        )
        return self.wavelet_tree.select_bit(0, maximum + 1, node)

    def predecessor_naive(self, left, right):
        if not self.w or right < 0:
            return NA

        target = self.w[right]
        predecessor_index = NA
        start = max(left, 0)
        for index in range(start, right):
            value = self.w[index]
            if value <= target and (
                predecessor_index == NA
                or value >= self.w[predecessor_index]
            ):
                predecessor_index = index
        return predecessor_index

    def last_code(self, left, right):
        if right - left < self.range_threshold:
            predecessor = self.predecessor_naive(left, right)
        else:
            if not self.wavelet_flag:
                self._construct_wavelet_tree()
            predecessor = self.predecessor_wavelet(
                self.wavelet_tree.root(),
                left - 1,
                right - 1,
            )

        successor = 0 if predecessor < 0 else int(self.w[predecessor] == self.w[right])
        if predecessor != NA:
            predecessor -= left
        return predecessor, successor

    def last_code_int(self, left, right):
        if right == self.n:
            return self.terminate_label
        predecessor, successor = self.last_code(left, right)
        return predecessor * 2 + successor

    def _construct(self):
        node = self.root
        depth = 0

        for start in range(self.n):
            while start + depth < self.n and depth == node.depth:
                child = node.get_child(self.last_code_int(start, start + depth))
                if child is None:
                    break

                node = child
                depth += 1
                while (
                    start + depth < self.n
                    and node.start + depth < self.n
                    and depth < node.depth
                    and self.last_code(node.start, node.start + depth)
                    == self.last_code(start, start + depth)
                ):
                    depth += 1

            if depth < node.depth:
                node = self.create_node(node, depth)
            self.create_leaf(start, node, depth)

            if node.slink is None:
                self.compute_suffix_link(node)
            node = node.slink
            depth = max(depth - 1, 0)

    def compute_suffix_link(self, node):
        depth = node.depth
        copy_node = node
        while copy_node.parent.slink is None:
            copy_node = copy_node.parent

        suffix = copy_node.parent.slink
        while suffix.depth < depth - 1:
            label = self.last_code_int(
                node.start + 1,
                node.start + suffix.depth + 1,
            )
            suffix = suffix.get_child(label)

        if suffix.depth > depth - 1:
            suffix = self.create_node(suffix, depth - 1)
        node.set_suffix_link(suffix)

    def create_node(self, node, depth):
        start = node.start
        parent = node.parent
        new_label = self.last_code_int(start, start + parent.depth)
        old_label = self.last_code_int(start, start + depth)
        new_node = STNode(start, depth, new_label)
        new_node.add_child(node, old_label)
        parent.add_child(new_node, new_label)
        self.node_count += 1
        return new_node

    def create_leaf(self, start, node, depth):
        label = self.last_code_int(start, start + depth)
        leaf = STNode(start, self.n - start + 1, label)
        node.add_child(leaf, label)
        self.node_count += 1

    def max_tau_dfs(self, tau):
        stack = [self.root]
        tau_minus_one = tau - 1
        self.maximal_candidate_node_count = 0

        while stack:
            node = stack[-1]
            if not node.visited:
                node.visited = True
                stack.extend(node.child.values())
                continue

            stack.pop()
            if not node.child:
                node.leaf_count = 1
            elif len(node.child) > 1:
                child_is_frequent = False
                for child in node.child.values():
                    node.leaf_count += child.leaf_count
                    child_is_frequent = (
                        child_is_frequent or child.leaf_count > tau_minus_one
                    )
                if node.leaf_count > tau_minus_one and not child_is_frequent:
                    node.is_candidate = True
                    self.maximal_candidate_node_count += 1
            else:
                node.leaf_count = next(iter(node.child.values())).leaf_count

            if node.is_candidate and node.slink is not None:
                ancestor = node.slink
                while ancestor is not None and ancestor.left_max:
                    ancestor.left_max = False
                    ancestor = ancestor.parent
            node.visited = False

    def max_find_nodes(self):
        result = {}
        stack = [self.root]
        while stack:
            node = stack[-1]
            if not node.visited:
                node.visited = True
                stack.extend(node.child.values())
                continue

            if node.is_candidate and node.left_max:
                result[node] = node.leaf_count
            node.visited = False
            node.is_candidate = False
            node.left_max = True
            node.leaf_count = 0
            stack.pop()
        return result

    # Names retained as aliases for direct comparison with the official C++ API.
    MaxTauDFS = max_tau_dfs
    MaxFindNodes = max_find_nodes
    LastCode = last_code
    LastCodeInt = last_code_int
    ComputeSuffixLink = compute_suffix_link


class WindowOPSTMOPPMiner:


    def __init__(self, window_len, step=None, min_sup=12, range_threshold=512):
        if window_len <= 0:
            raise ValueError("window_len must be positive")
        if step is not None and step <= 0:
            raise ValueError("step must be positive")
        if min_sup <= 1:
            raise ValueError("Official OPST requires min_sup (tau) > 1")
        if range_threshold <= 0:
            raise ValueError("range_threshold must be positive")

        self.window_len = window_len
        self.step = window_len if step is None else step
        self.min_sup = min_sup
        self.range_threshold = range_threshold

        self.window_results = []
        self.window_support_results = []
        self.window_level_results = []
        self.window_frequent_level_results = []
        self.window_stats = []
        self.mopp_set = set()
        self.mopp_support = {}
        self.Flist = []
        self.level_counts = []

        self.candidate_generated_count = 0
        self.operation = 0
        self.reset_stats()

    def reset_stats(self):
        self.candidate_checked_count = 0
        self.fusion_count = 0
        self.cached_fusion_hit_count = 0
        self.support_calc_count = 0
        self.frequent_count = 0
        self.all_frequent_count = 0
        self.all_frequent_level_counts = []
        self.runtime = 0.0
        self.construction_time = 0.0
        self.mining_time = 0.0
        self.wavelet_time = 0.0
        self.tree_node_count = 0
        self.maximal_candidate_node_count = 0

    @staticmethod
    def canonical_pattern(values):
        ranks = {
            value: rank + 1
            for rank, value in enumerate(sorted(set(values)))
        }
        return tuple(ranks[value] for value in values)

    def decode_maximal_nodes(self, window_data, maximal_nodes):
        patterns = {}
        for node, support in maximal_nodes.items():
            end = node.start + node.depth
            values = window_data[node.start:end]
            pattern = self.canonical_pattern(values)
            patterns[pattern] = support
        return patterns

    @staticmethod
    def counts_by_length(patterns):
        if not patterns:
            return []
        counts = Counter(len(pattern) for pattern in patterns)
        maximum_length = max(counts)
        return [counts.get(length, 0) for length in range(1, maximum_length + 1)]

    @staticmethod
    def count_all_strict_frequent_opps(op_tree, min_sup, window_length):

        counts = Counter()
        stack = [op_tree.root]
        while stack:
            node = stack.pop()
            stack.extend(node.child.values())
            if node is op_tree.root or node.leaf_count < min_sup:
                continue

            first_depth = max(node.parent.depth + 1, 2)
            last_depth = min(node.depth, window_length - node.start)
            for depth in range(first_depth, last_depth + 1):
                representative = op_tree.w[node.start : node.start + depth]
                if len(set(representative)) == depth:
                    counts[depth] += 1

        if not counts:
            return 0, []
        maximum_length = max(counts)
        level_counts = [
            counts.get(length, 0)
            for length in range(2, maximum_length + 1)
        ]
        return sum(level_counts), level_counts

    def mine_window(self, window_data, window_id=1):
        self.reset_stats()
        start = time.perf_counter()
        values = list(window_data)

        construction_start = time.perf_counter()
        op_tree = OPST(values, self.range_threshold)
        self.construction_time = time.perf_counter() - construction_start

        mining_start = time.perf_counter()
        op_tree.MaxTauDFS(self.min_sup)
        (
            self.all_frequent_count,
            self.all_frequent_level_counts,
        ) = self.count_all_strict_frequent_opps(
            op_tree,
            self.min_sup,
            len(values),
        )
        maximal_nodes = op_tree.MaxFindNodes()
        self.mining_time = time.perf_counter() - mining_start

        maximal_patterns = self.decode_maximal_nodes(values, maximal_nodes)
        self.mopp_support = maximal_patterns
        self.mopp_set = set(maximal_patterns)
        self.Flist = list(self.mopp_set)
        self.level_counts = self.counts_by_length(self.mopp_set)

        self.frequent_count = len(self.mopp_set)
        self.wavelet_time = op_tree.wavelet_time
        self.tree_node_count = op_tree.node_count
        self.maximal_candidate_node_count = op_tree.maximal_candidate_node_count
        self.runtime = time.perf_counter() - start

        window_mopp = set(self.mopp_set)
        self.window_results.append(window_mopp)
        self.window_support_results.append(dict(maximal_patterns))
        self.window_level_results.append(self.level_counts.copy())
        self.window_frequent_level_results.append(
            self.all_frequent_level_counts.copy()
        )

        stats = self.stats_dict()
        stats["window_id"] = window_id
        stats["level_counts"] = self.level_counts.copy()
        stats["level_count_semantics"] = "maximal_patterns_by_length"
        stats["all_frequent_level_counts"] = self.all_frequent_level_counts.copy()
        stats["all_frequent_level_count_semantics"] = (
            "strict_rank_frequent_patterns_by_length_starting_at_length_2"
        )
        self.window_stats.append(stats)
        return window_mopp

    def run(self, data, dates=None):
        self.window_results.clear()
        self.window_support_results.clear()
        self.window_level_results.clear()
        self.window_frequent_level_results.clear()
        self.window_stats.clear()
        self.candidate_generated_count = 0
        self.operation = 0

        for window_id, (window_data, _) in enumerate(self.get_windows(data), 1):
            self.mine_window(window_data, window_id)
        return self.window_results

    def get_windows(self, data):
        for start in range(0, len(data) - self.window_len + 1, self.step):
            yield data[start : start + self.window_len], start

    def stats_dict(self):
        return {
            "candidate_generated_count": 0,
            "candidate_checked_count": 0,
            "fusion_count": 0,
            "cached_fusion_hit_count": 0,
            "support_calc_count": 0,
            "frequent_count": self.frequent_count,
            "mopp_count": self.frequent_count,
            "all_frequent_count": self.all_frequent_count,
            "runtime": self.runtime,
            "construction_time": self.construction_time,
            "mining_time": self.mining_time,
            "operation": 0,
            "wavelet_time": self.wavelet_time,
            "tree_node_count": self.tree_node_count,
            "maximal_candidate_node_count": self.maximal_candidate_node_count,
        }


def read_numeric_series(file_name):
    data = []
    with open(file_name, "r", encoding="utf-8") as stream:
        for line in stream:
            for token in line.replace(",", " ").split():
                try:
                    value = float(token)
                except ValueError:
                    continue
                if math.isfinite(value):
                    data.append(value)
    return data


def main():
    default_sample = Path(__file__).resolve().parent / "OPST-WOPP" / "sample.txt"
    parser = argparse.ArgumentParser(
        description="A pure OPST-Maximal run independently inside each window"
    )
    parser.add_argument("dataset", nargs="?", default=str(default_sample))
    parser.add_argument("--window-len", type=int, default=None)
    parser.add_argument("--step", type=int, default=None)
    parser.add_argument("--min-sup", type=int, default=2)
    parser.add_argument("--range-threshold", type=int, default=512)
    parser.add_argument("--print-patterns", action="store_true")
    args = parser.parse_args()

    data = read_numeric_series(args.dataset)
    if not data:
        raise ValueError(f"No numeric values read from {args.dataset}")

    window_len = args.window_len or len(data)
    step = args.step or window_len
    miner = WindowOPSTMOPPMiner(
        window_len=window_len,
        step=step,
        min_sup=args.min_sup,
        range_threshold=args.range_threshold,
    )

    start = time.perf_counter()
    miner.run(data)
    total_time = time.perf_counter() - start

    print(f"Execution time: {total_time:.6f} seconds")
    print(f"Window count: {len(miner.window_results)}")
    print(
        "Total maximal OPP count: "
        f"{sum(len(patterns) for patterns in miner.window_results)}"
    )
    print(
        "Total frequent OPP count "
        "(all frequent explicit/implicit loci, tied-rank patterns filtered): "
        f"{sum(stats['all_frequent_count'] for stats in miner.window_stats)}"
    )
    print(f"Last window MOPP count: {miner.frequent_count}")
    print(f"Last window MOPP counts by length: {miner.level_counts}")
    print(f"Last window frequent OPP count: {miner.all_frequent_count}")
    print(
        "Last window frequent OPP counts by length (starting at length 2): "
        f"{miner.all_frequent_level_counts}"
    )
    if miner.window_stats:
        print(f"Last window stats: {miner.window_stats[-1]}")
    if args.print_patterns and miner.window_support_results:
        print(f"Last window MOPPs: {miner.window_support_results[-1]}")


if __name__ == "__main__":
    main()
