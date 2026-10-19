import sys
import time

try:
    from memory_usage_monitor import MemoryUsageMonitor
except ImportError:
    import tracemalloc

    class MemoryUsageMonitor:
        def start(self):
            tracemalloc.start()

        def get_max_memory_usage(self):
            return tracemalloc.get_traced_memory()[1] / (1024 * 1024)

        def stop_monitoring(self):
            pass

        def join(self):
            tracemalloc.stop()

# ---------------------------------------------------------------------------
# Global parameters (mirrors Java's static fields)
# ---------------------------------------------------------------------------
K = 80000
maxlen = 10
mingap = 0
maxgap = 0
minsup = 0
Maxseqlen = 1

SDB_num = 0
SDB = []
AlphabetSize = 1
Alphabet = {}

candidate = []
temp_HBT = {}           # pos -> list[list[int]]
All_HBTS = {}           # Pattern(2-tuple) -> HBTableSet (list[dict pos -> list[list[int]]], one dict per sequence)
position = []           # unused scratch list (kept for fidelity with original, never populated)
record = []             # list[set[int]], index 0..maxlen-1


class Sequence:
    __slots__ = ("id", "S", "length")

    def __init__(self, id_, S, length):
        self.id = id_
        self.S = S
        self.length = length


# ---------------------------------------------------------------------------
# ReadFile
# ---------------------------------------------------------------------------
def read_file(fixed_minsup, filename):
    global SDB_num, minsup, AlphabetSize, Maxseqlen

    frequent_item = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("Failed to open the file.")
        sys.exit(0)

    i = 0
    for line in lines:
        if i >= K:
            break
        char_array = [ch for ch in line.strip() if not ch.isspace()]
        if not char_array:
            continue
        SDB.append(Sequence(i, char_array, len(char_array)))
        if len(char_array) > Maxseqlen:
            Maxseqlen = len(char_array)
        for item in char_array:
            Alphabet[item] = Alphabet.get(item, 0) + 1
        i += 1

    SDB_num = i
    minsup = int(fixed_minsup)
    AlphabetSize = len(Alphabet)

    for item, count in Alphabet.items():
        if count >= minsup:
            frequent_item.append((item,))

    return frequent_item


# ---------------------------------------------------------------------------
# Build_PositionMap
# ---------------------------------------------------------------------------
def build_position_map(frequent_item, PositionList, IndexMap):
    frequent_first_items = {p[0] for p in frequent_item}

    for i in range(SDB_num):
        PositionArray = {}
        for j, item in enumerate(SDB[i].S):
            PositionArray.setdefault(item, []).append(j)

        length = 0
        for item in sorted(PositionArray.keys()):
            positions = PositionArray[item]
            if item in frequent_first_items and positions:
                PositionList[i].extend(positions)
                IndexMap[i][item] = length
                length += len(positions)

def generate_candidate(candidate_list, length, frequent):
    if length == 1:
        for p in frequent[0]:
            for q in frequent[0]:
                candidate_list.append((p[0], q[0]))
    else:
        for p in frequent[length - 1]:
            for q in frequent[length - 1]:
                flag = False
                for i in range(length - 1):
                    if p[i] != q[i + 1]:
                        flag = True
                        break
                if not flag:
                    new_pattern = q + (p[length - 1],)
                    candidate_list.append(new_pattern)

def gap_match(PositionList, IndexMap, cand, frequent):
    first_item, second_item = cand[0], cand[1]
    support = 0
    HBTS = [dict() for _ in range(SDB_num)]  # HBTableSet

    for i in range(SDB_num):
        if SDB[i].length == 0:
            continue
        idx_i = IndexMap[i]
        if first_item not in idx_i or second_item not in idx_i:
            continue

        keys = list(idx_i.keys())
        pos_list = PositionList[i]

        first_pos = []
        found = 0
        for key in keys:
            if found == 1:
                first_pos.extend(pos_list[idx_i[first_item]:idx_i[key]])
                found = 2
                break
            if key == first_item:
                found = 1
        if found == 1:
            first_pos.extend(pos_list[idx_i[first_item]:])

        second_pos = []
        found = 0
        for key in keys:
            if found == 1:
                second_pos.extend(pos_list[idx_i[second_item]:idx_i[key]])
                found = 2
                break
            if key == second_item:
                found = 1
        if found == 1:
            second_pos.extend(pos_list[idx_i[second_item]:])

        CT = {}
        for pos in first_pos:
            for j in range(mingap, maxgap + 1):
                c = pos + j + 1
                CT.setdefault(c, []).append(pos)

        # store matched positions into HBT
        hbt_i = HBTS[i]
        for c in second_pos:
            if c not in CT:
                continue
            for pos in CT[c]:
                if pos not in hbt_i:
                    hbt_i[pos] = [[c]]
                else:
                    hbt_i[pos].append([c])

        # filter to non-overlapping combinations
        rec0, rec1 = record[0], record[1]
        for pos in list(hbt_i.keys()):
            occ_list = hbt_i[pos]
            if not occ_list:
                del hbt_i[pos]
                continue
            for occ in occ_list:
                if pos not in rec0 and occ[0] not in rec1:
                    support += 1
                    rec0.add(pos)
                    rec1.add(occ[0])
                    break

        position.clear()
        rec0.clear()
        rec1.clear()

    if support >= minsup:
        frequent[1].append(cand)
        All_HBTS[cand] = HBTS

def merge_hbtable(HBT1, HBT2, temp_hbt):
    for pos, occ_list in HBT1.items():
        target = temp_hbt.get(pos)
        if target is None:
            continue
        for left_occ in occ_list:
            last = left_occ[-1]
            right_list = HBT2.get(last)
            if right_list is None:
                continue
            for right_occ in right_list:
                target.append([left_occ[0], right_occ[0]])

def calculate_support(HBTS1, HBTS2, length):
    support = 0
    rec0, recN = record[0], record[length - 1]

    for i in range(SDB_num):
        hbt1_i = HBTS1[i]
        hbt2_i = HBTS2[i]
        for pos in list(hbt1_i.keys()):
            matched = False
            for left_occ in hbt1_i[pos]:
                common_pos = left_occ[-1]
                right_list = hbt2_i.get(common_pos)
                if right_list is None:
                    continue
                for right_occ in right_list:
                    flag = pos in rec0 or right_occ[0] in recN
                    if not flag:
                        for l in range(1, length - 1):
                            if left_occ[l - 1] in record[l]:
                                flag = True
                                break
                    if not flag:
                        support += 1
                        rec0.add(pos)
                        for l in range(1, length - 1):
                            record[l].add(left_occ[l - 1])
                        recN.add(right_occ[0])
                        matched = True
                        break
                if matched:
                    break

        for k in range(length):
            record[k].clear()
        if support >= minsup:
            break

    return support

def mining_patterns(cand, frequent):
    length = len(cand)
    support = 0
    substr = [(cand[i], cand[i + 1]) for i in range(length - 1)]

    if length == 3:
        support = calculate_support(All_HBTS[substr[0]], All_HBTS[substr[1]], 3)
        if support >= minsup:
            frequent[length - 1].append(cand)
        return

    if length == 4:
        s0, s1, s2 = substr[0], substr[1], substr[2]
        rec0, recN = record[0], record[length - 1]

        for i in range(SDB_num):
            Length = SDB[i].length
            merge_hbtable(All_HBTS[s0][i], All_HBTS[s1][i], temp_HBT)

            hbt_s0_i = All_HBTS[s0][i]
            hbt_s2_i = All_HBTS[s2][i]
            matched = False
            for pos in list(hbt_s0_i.keys()):
                if matched:
                    break
                for left_occ in temp_HBT[pos]:
                    common = left_occ[-1]
                    right_list = hbt_s2_i.get(common)
                    if right_list is None:
                        continue
                    for right_occ in right_list:
                        flag = pos in rec0 or right_occ[0] in recN
                        if not flag:
                            for l in range(1, length - 1):
                                if left_occ[l - 1] in record[l]:
                                    flag = True
                                    break
                        if not flag:
                            support += 1
                            rec0.add(pos)
                            for l in range(1, length - 1):
                                record[l].add(left_occ[l - 1])
                            recN.add(right_occ[0])
                            matched = True
                            break
                    if matched:
                        break

            for j in range(Length):
                temp_HBT[j].clear()
            for j in range(length):
                record[j].clear()
            if support >= minsup:
                frequent[length - 1].append(cand)
                break
        return

    if length >= 5:
        s0 = substr[0]
        s_last = substr[length - 2]
        rec0, recN = record[0], record[length - 1]

        for i in range(SDB_num):
            Length = SDB[i].length
            merge_hbtable(All_HBTS[s0][i], All_HBTS[substr[1]][i], temp_HBT)

            for l in range(2, length - 2):
                s_l_i = All_HBTS[substr[l]][i]
                hbt_s0_i = All_HBTS[s0][i]
                for pos in list(hbt_s0_i.keys()):
                    temp_list = [list(occ) for occ in temp_HBT[pos]]
                    temp_HBT[pos].clear()
                    for left_occ in temp_list:
                        last = left_occ[-1]
                        right_list = s_l_i.get(last)
                        if right_list is None:
                            continue
                        for right_occ in right_list:
                            occ = list(left_occ)
                            occ.append(right_occ[0])
                            temp_HBT[pos].append(occ)

            hbt_s0_i = All_HBTS[s0][i]
            hbt_slast_i = All_HBTS[s_last][i]
            matched = False
            for pos in list(hbt_s0_i.keys()):
                if matched:
                    break
                for left_occ in temp_HBT[pos]:
                    last = left_occ[-1]
                    right_list = hbt_slast_i.get(last)
                    if right_list is None:
                        continue
                    for right_occ in right_list:
                        flag = pos in rec0 or right_occ[0] in recN
                        if not flag:
                            for l2 in range(1, length - 1):
                                if left_occ[l2 - 1] in record[l2]:
                                    flag = True
                                    break
                        if not flag:
                            support += 1
                            rec0.add(pos)
                            for l2 in range(1, length - 1):
                                record[l2].add(left_occ[l2 - 1])
                            recN.add(right_occ[0])
                            matched = True
                            break
                    if matched:
                        break

            for j in range(Length):
                temp_HBT[j].clear()
            for j in range(length):
                record[j].clear()
            if support >= minsup:
                frequent[length - 1].append(cand)
                break
        return


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def get_inputs():
    if len(sys.argv) == 5:
        filepath = sys.argv[1]
        mingap_ = int(sys.argv[2])
        maxgap_ = int(sys.argv[3])
        fixed_minsup_ = int(sys.argv[4])
    else:
        filepath = input("Path to character-sequence dataset: ").strip()
        mingap_ = int(input("mingap: ").strip())
        maxgap_ = int(input("maxgap: ").strip())
        fixed_minsup_ = int(input("minsup (fixed absolute number): ").strip())
    return filepath, mingap_, maxgap_, fixed_minsup_


def main():
    global mingap, maxgap

    print("Welcome to the MNSPM!")

    filepath, mingap, maxgap, fixed_minsup = get_inputs()

    frequent_item = read_file(fixed_minsup, filepath)
    print(f"Fixed minsup: {minsup}, sequences: {SDB_num}, "
          f"alphabet size: {AlphabetSize}, 1-frequent items: {len(frequent_item)}")

    PositionList = [[] for _ in range(SDB_num)]
    IndexList = [dict() for _ in range(SDB_num)]
    build_position_map(frequent_item, PositionList, IndexList)

    frequent = [[] for _ in range(maxlen)]
    frequent[0] = frequent_item

    for _ in range(maxlen):
        record.append(set())
    for i in range(Maxseqlen):
        temp_HBT[i] = []

    monitor = MemoryUsageMonitor()
    monitor.start()
    begintime = time.time()

    candidate_num = 0
    generate_candidate(candidate, 1, frequent)
    candidate_num += len(candidate)
    for cand in candidate:
        gap_match(PositionList, IndexList, cand, frequent)
    candidate.clear()

    length = 2
    while length < maxlen and frequent[length - 1]:
        generate_candidate(candidate, length, frequent)
        candidate_num += len(candidate)
        length += 1
        for cand in candidate:
            mining_patterns(cand, frequent)
        candidate.clear()

    endtime = time.time()
    max_memory_usage = monitor.get_max_memory_usage()
    monitor.stop_monitoring()
    monitor.join()

    print(filepath)
    pattern_num = 0
    for l in range(maxlen):
        if not frequent[l]:
            break
        pattern_num += len(frequent[l])

    print(f"The number of candidate patterns: {candidate_num}")
    print(f"The number of frequent patterns: {pattern_num}")
    print(f"The number of infrequent patterns:{candidate_num - pattern_num}")

    print(f"Time used: {endtime - begintime:.2f}s")
    print(f"Memory used: {max_memory_usage:.2f}MB")


if __name__ == "__main__":
    main()
