# Exploration: ZMK Keymap Extractor Improvements

## Current State

The ZMK keymap extractor (`zmk_extractor.py`) successfully extracts keymaps from Lily58 keyboard via ZMK Studio RPC serial protocol. The implementation is **functional** but has several limitations:

### Protocol Implementation
- **Transport**: Serial CDC-ACM at **12500 baud** (NOT 115200 as commonly assumed)
- **Framing**: SOF(0xAB)/ESC(0xAC)/EOF(0xAD) byte stuffing
- **Encoding**: Custom Protobuf encoder/decoder matching ZMK Studio TypeScript client v0.0.18
- **Flow**: Lock check → Unlock → Get behaviors → Get keymap → Decode → Format

### Data Extraction Results
- **Layers**: 4 layers extracted successfully
- **Bindings per layer**: 58 bindings each (Lily58 split layout: 6×12 keys + 2 thumb clusters = 74 keys, but protocol reports 58 active positions)
- **Metadata**: `availableLayers: 0`, `maxLayerNameLength: 20`

### Key Issues Identified

#### 1. Layer Names Are Empty
```json
{
  "id": 0,
  "name": "",  // ← Problem: ZMK Studio doesn't persist layer names
  "bindings": [...]
}
```
The firmware doesn't store layer names in the RPC response, so extracted keymaps have unnamed layers (`_layer`, `_layer`, `_layer`, `_layer` in devicetree output).

#### 2. Incomplete HID Keycode Mapping
Standard keycodes map correctly:
```python
0x04: "A", 0x05: "B", ..., 0x28: "ENTER", 0x29: "ESC"
```

But many codes fall through to hex representation:
```
&kp C(0x500E2)      # Unknown keycode
&kp C(0x200002D)     # Unknown keycode
&kp C(0x200001E)     # Unknown keycode
```

#### 3. Complex Modifiers Not Properly Formatted
From the extracted output:
```dts
&mt LCTRL(LALT(LGUI(RSHFT) C(0x200002D)  # ← BROKEN: Nested modifiers
```
The current implementation:
```python
def modifier_to_zmk(mod):
    names = []
    for bit, name in sorted(MODIFIER_FLAGS.items()):
        if mod & bit:
            names.append(name)
    if not names:
        return f"0x{mod:X}"
    return "(".join(names) + (")" if len(names) > 1 else "")
```
Doesn't handle complex combinations properly.

#### 4. Consumer Keys Partially Mapped
Only a subset of consumer keys are mapped:
```python
consumer_names = {
    0xE2: "C_MUTE",
    0xE9: "C_VOL_UP",
    0xEA: "C_VOL_DN",
    # ... only ~10 keys
}
```
Missing: media controls, system controls, power management, etc.

#### 5. Behavior Mapping is Hardcoded
```python
BEHAVIOR_MAP = {
    1: "bootloader",
    2: "caps_word",
    3: "kp",
    # ... 22 behaviors hardcoded
}
```
Behavior IDs are dynamically assigned by firmware but mapping is static.

#### 6. Architecture Is Monolithic
`zmk_extractor.py` (1291 lines) mixes:
- Protobuf encoding/decoding
- Serial communication
- Protocol framing
- Data mapping
- Output formatting
- CLI interface

No clear separation of concerns.

#### 7. Limited Output Formats
Only two formats:
- **JSON**: Raw extracted data with numeric IDs
- **.keymap**: ZMK devicetree syntax

Missing: CSV, YAML, human-readable text.

#### 8. No Verification Mechanism
No automated way to verify:
- Decoded keycodes are correct
- Extracted keymap matches original
- Protocol parsing is complete

---

## Affected Areas

- **`zmk_extractor.py`** (1291 lines) — Main extractor with protocol, mapping, and formatting
- **`keymap_extracted.json`** — Raw output showing layer name issue
- **`keymap_extracted.keymap`** — Devicetree output with formatting problems
- **`openspec/config.yaml`** — SDD configuration with testing disabled
- **Documentation** — No reference docs for current protocol behavior

---

## Approaches

### 1. **Conservative Enhancement** (Low Risk, Low Effort)

**Description**: Fix immediate pain points without restructuring.

**Pros**:
- Minimal code changes
- Low risk of breaking existing functionality
- Quick wins for users

**Cons**:
- Doesn't address architectural debt
- Mappings remain hardcoded
- No new output formats

**Effort**: Low (2-3 days)

**Specific Changes**:
1. Read layer names from `config/lily58.keymap` (if exists)
2. Expand HID keycode mapping from ZMK headers
3. Fix `modifier_to_zmk()` to handle complex combinations
4. Add 50+ more consumer key mappings
5. Add `--verbose` flag for protocol debugging

---

### 2. **Refactored Architecture** (Medium Risk, Medium Effort)

**Description**: Separate concerns into distinct modules.

**Pros**:
- Clear separation of concerns
- Easier to test and maintain
- Enables pluggable formatters

**Cons**:
- Requires refactoring working code
- Higher risk of introducing bugs
- More complex build system

**Effort**: Medium (1 week)

**New Structure**:
```
zmk_extractor/
├── __init__.py
├── protocol/
│   ├── __init__.py
│   ├── framing.py      # SOF/ESC/EOF framing
│   ├── protobuf.py     # Encoder/decoder
│   └── rpc.py         # ZMK Studio RPC client
├── mapping/
│   ├── __init__.py
│   ├── keycodes.py     # HID keycode lookup
│   ├── behaviors.py    # Behavior ID resolution
│   └── consumer.py    # Consumer key mapping
├── formatter/
│   ├── __init__.py
│   ├── json_formatter.py
│   ├── dts_formatter.py
│   ├── csv_formatter.py
│   └── yaml_formatter.py
├── extractor.py        # Main orchestration
└── cli.py             # Argument parsing
```

**Benefits**:
- Can query firmware for behavior names instead of hardcoding
- Keycode mappings can be generated from ZMK headers
- Formatters are pluggable

---

### 3. **Dynamic Behavior Resolution** (Medium Risk, Medium Effort)

**Description**: Query firmware for behavior details instead of static mapping.

**Pros**:
- Behavior names always match firmware
- Supports custom behaviors
- Future-proof

**Cons**:
- Slower extraction (more RPC calls)
- Requires keyboard to be connected
- Falls back to static mapping if unavailable

**Effort**: Medium (3-4 days)

**Implementation**:
```python
def get_behavior_map(client):
    """Query firmware for behavior names"""
    behavior_ids = client.get_behaviors_list()
    behavior_map = {}

    for bid in behavior_ids:
        details = client.get_behavior_details(bid)
        if details:
            behavior_map[bid] = details['name']

    # Fallback to static map for unmapped behaviors
    behavior_map.update(STATIC_BEHAVIOR_MAP)
    return behavior_map
```

---

### 4. **Multi-Format Export with Verification** (Low Risk, Medium Effort)

**Description**: Add CSV/YAML export and verification against original.

**Pros**:
- Enables data analysis in spreadsheet tools
- YAML is human-readable and git-friendly
- Verification ensures correctness

**Cons**:
- Requires parsing original keymap file
- May not match 1:1 (original vs extracted)
- Adds complexity

**Effort**: Medium (3-4 days)

**CSV Format**:
```csv
layer,key_index,behavior,param1,param2,formatted_key
0,0,kp,458793,0,ESC
0,1,kp,458782,0,N1
0,2,kp,458783,0,N2
```

**Verification**:
```python
def verify_extraction(extracted, original_file):
    """Compare extracted bindings with original keymap"""
    # Parse devicetree keymap
    original = parse_keymap(original_file)

    # Compare behavior IDs and parameters
    for layer in range(4):
        for key in range(58):
            assert extracted[layer][key]['behaviorId'] == original[layer][key]['behaviorId']
            assert extracted[layer][key]['param1'] == original[layer][key]['param1']
```

---

### 5. **Comprehensive Overhaul** (High Risk, High Effort)

**Description**: Refactor architecture + dynamic resolution + multi-format + verification.

**Pros**:
- Clean, maintainable codebase
- Future-proof behavior handling
- Multiple output formats
- Automated verification

**Cons**:
- High risk of breaking existing functionality
- Long development time
- Requires extensive testing
- May not be worth effort for a single-tool project

**Effort**: High (2-3 weeks)

---

## Recommendation

**Adopt Approach 2 (Refactored Architecture) + Approach 3 (Dynamic Behavior Resolution) as Phase 1**

**Rationale**:

1. **Architectural debt is blocking**: Current monolithic structure makes adding features difficult and risky. Refactoring first reduces future risk.

2. **Dynamic resolution is more robust**: Hardcoded behavior IDs are fragile. Querying the firmware ensures correctness even when ZMK changes.

3. **Reasonable effort**: 1-2 weeks for meaningful improvements without over-engineering.

4. **Phase 2 can add**: Multi-format export and verification after Phase 1 is stable.

**Why NOT the other approaches**:

- **Approach 1 (Conservative)**: Too tactical. Doesn't address root causes.
- **Approach 4 (Multi-format only)**: Premature optimization without architectural foundation.
- **Approach 5 (Overhaul)**: Too much risk for a tool that already works. Better to iterate.

---

## Risks

### Technical Risks

1. **Breaking existing functionality**: Refactoring protocol code could introduce bugs that prevent extraction
   - **Mitigation**: Preserve original file as reference, add integration tests with real keyboard

2. **Behavior RPC calls are slow**: Querying 22+ behaviors at 12500 baud adds significant time
   - **Mitigation**: Cache behavior map, allow fallback to static mapping

3. **Keymap parsing complexity**: Devicetree syntax is complex, verification may not match 1:1
   - **Mitigation**: Use fuzzy matching, focus on behavior ID and param validation

4. **Firmware changes**: ZMK Studio protocol may change in future versions
   - **Mitigation**: Document protocol version, add version detection

### Project Risks

1. **User doesn't have original keymap**: Layer name resolution requires reading `config/lily58.keymap`
   - **Mitigation**: Provide fallback to semantic naming (layer_0, layer_1, etc.)

2. **Limited testing environment**: Only one keyboard type (Lily58) available for testing
   - **Mitigation**: Use mock data for unit tests, document assumptions

3. **Over-engineering**: Spending too much time on a simple extraction tool
   - **Mitigation**: Time-box each phase, ship incrementally

---

## Ready for Proposal

**YES** — The exploration has identified clear problems, multiple approaches, and a recommended path forward.

**What the orchestrator should tell the user**:

> "I've explored the ZMK keymap extractor and identified several improvement opportunities:
>
> **Key findings**:
> - Layer names are empty (ZMK Studio doesn't persist them)
> - HID keycode mapping is incomplete (~50% of codes fall through to hex)
> - Complex modifiers break formatting (e.g., `LCTRL(LALT(...))`)
> - Consumer keys are only partially mapped
> - Behavior IDs are hardcoded instead of dynamic
> - Code is monolithic (1291 lines in one file)
>
> **Recommended approach**:
> Phase 1: Refactor into modules + dynamic behavior resolution (1-2 weeks)
> Phase 2: Add multi-format export + verification (optional)
>
> This balances immediate fixes with long-term maintainability.
>
> Should I proceed to create a detailed proposal with specifications and design?"
