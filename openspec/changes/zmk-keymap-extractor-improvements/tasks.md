# Tasks: ZMK Keymap Extractor Improvements

## Phase 1: Foundation & Infrastructure

- [x] 1.1 Create directory structure: `zmk/protocol/`, `zmk/mapping/`, `zmk/formatter/`, `zmk/tests/`
- [x] 1.2 Create `requirements.txt` with dependencies: click>=8.0, pyyaml, pyserial
- [x] 1.3 Extract framing logic to `zmk/protocol/framing.py` (SOF/ESC/EOF)
- [x] 1.4 Extract protobuf encoder/decoder to `zmk/protocol/protobuf.py`
- [x] 1.5 Create `zmk/protocol/rpc.py` with RPC request/response encoding

## Phase 2: Protocol Module

- [x] 2.1 Implement `zmk/protocol/serial.py` with CDC-ACM client at 12500 baud
- [x] 2.2 Add frame/unframe functions in `framing.py` with ESC handling
- [x] 2.3 Implement encode/decode in `protobuf.py` with ZIGZAG varint encoding
- [x] 2.4 Create RPC client in `rpc.py` with lock/unlock/getBehaviors/getKeymap methods
- [x] 2.5 Write unit tests: `zmk/tests/test_protocol.py` (framing, encoding)

## Phase 3: Mapping Module

- [x] 3.1 Create `zmk/mapping/keycodes.py` with HID Usage Page 7 table (0x04-0xFF)
- [x] 3.2 Add Consumer Page 0x0C keycodes to `keycodes.py` (C_MUTE, C_VOL_UP, etc.)
- [x] 3.3 Implement `zmk/mapping/modifiers.py` with MODIFIER_FLAGS decoding
- [x] 3.4 Create `zmk/mapping/behaviors.py` with dynamic resolution and JSON cache
- [x] 3.5 Implement `zmk/mapping/layers.py` with semantic naming (BASE, NAV, SYM, ADJUST)
- [x] 3.6 Write unit tests: `zmk/tests/test_mapping.py` (keycodes, modifiers)

## Phase 4: Formatter Module

- [x] 4.1 Create `zmk/formatter/__init__.py` with OutputFormatter interface
- [x] 4.2 Implement `zmk/formatter/devicetree.py` for .keymap format
- [x] 4.3 Implement `zmk/formatter/json.py` for JSON export
- [x] 4.4 Implement `zmk/formatter/yaml.py` for YAML export
- [x] 4.5 Implement `zmk/formatter/csv.py` with layer/key_index columns

## Phase 5: Extractor Core

- [x] 5.1 Create `zmk_studio/extractor/keymap_extractor.py` with KeymapExtractor class
- [x] 5.2 Implement RPC client abstraction in KeymapExtractor
- [x] 5.3 Add keymap extraction logic with error handling
- [x] 5.4 Implement behavior map resolution with cache fallback
- [x] 5.5 Add layer name resolution (original → semantic → sequential)

## Phase 6: CLI Implementation

- [x] 6.1 Refactor `zmk/extractor.py` as CLI using click 8.x+
- [x] 6.2 Add `extract` subcommand with --format, --output, --verbose options
- [x] 6.3 Add `export` subcommand for format conversion
- [x] 6.4 Add `list-behaviors` subcommand with --cache-file option
- [x] 6.5 Add `cache-clear` subcommand for cache management
- [x] 6.6 Add `verify` subcommand for keymap comparison

## Phase 7: Migration & Legacy

- [ ] 7.1 Copy protocol code from `zmk_extractor.py` to new modules
- [ ] 7.2 Copy mapping code from `zmk_extractor.py` to `mapping/`
- [ ] 7.3 Copy formatter code from `zmk_extractor.py` to `formatter/`
- [ ] 7.4 Update all imports in new modules
- [ ] 7.5 Rename `zmk_extractor.py` to `zmk_extractor_legacy.py` as backup

## Phase 8: Testing & Verification

- [x] 8.1 Test extraction with real keyboard (COM8) at 12500 baud
- [x] 8.2 Verify extracted keymap matches original devicetree (DIFFERENT - keyboard has ZMK Studio changes)
- [x] 8.3 Test behavior cache persistence across runs
- [x] 8.4 Test all export formats (JSON, YAML, CSV, devicetree)
- [ ] 8.5 Verify modifier decoding produces human-readable output
- [ ] 8.6 Run `verify` subcommand against `config/lily58.keymap`

## Phase 9: Documentation

- [ ] 9.1 Create `PROTOCOL.md` documenting ZMK Studio protocol (framing, encoding)
- [ ] 9.2 Write README with usage examples for all CLI subcommands
- [ ] 9.3 Document behavior caching strategy in `README`
- [ ] 9.4 Add docstrings to all public functions and classes
- [ ] 9.5 Create migration guide from legacy extractor

## Phase 10: Cleanup & Polish

- [ ] 10.1 Remove dead code from `zmk_extractor_legacy.py`
- [ ] 10.2 Verify code complexity reduced (<500 lines per file)
- [ ] 10.3 Check all CLI options work correctly
- [ ] 10.4 Final verification: all success criteria from proposal met
- [ ] 10.5 Update `openspec/changes/zmk-keymap-extractor-improvements/state.yaml`
