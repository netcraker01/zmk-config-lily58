# Investigación de Layouts Óptimos para Lily58 (ZMK)

## Resumen Ejecutivo

Este documento compila investigación sobre layouts ergonómicos para teclados split Lily58, enfocándose en minimizar el uso del ratón y maximizar la productividad. Se recomienda **Miryoku** como layout base por su diseño ergonómico minimalista, con personalizaciones específicas para programación y uso en español.

---

## 1. Layouts Populares para Lily58/Corne/Splits

### 1.1 Miryoku (Recomendado)

**URL:** https://github.com/manna-harbour/miryoku

**Filosofía:**
- Ergonómico, minimal, ortogonal, universal
- 36 teclas (sin contar combos)
- Homerow mods con hold-tap
- Navegación integrada en layer de symbols

**Estructura de layers:**
```
Layer 0: BASE ( Colemak-DH recomendado)
Layer 1: NAV (Navegación + Mouse)
Layer 2: SYM (Symbols/Números)
Layer 3: FUNCT (Function keys)
Layer 4: NUMPAD (Numpad)
Layer 5: EXTRA (Aditional)
```

**Características clave:**
- Homerow mods (A=Gui, S=Alt, D=Ctrl, F=Shift)
- Thumb clusters para layers
- Combos para teclas faltantes
- Soporte nativo para ZMK

### 1.2 Otras Alternativas Populares

| Layout | Descripción | Ventajas |
|--------|-------------|----------|
| **Colemak-DH** | Reubicación home row | Mejor ergonomía que QWERTY |
| **Workman** | Optimizado para ortolineal | Balance entre frecuencia y alternancia de manos |
| **BEPO** | Optimizado para francés | Distribución de teclas eficiente |
| **QWERTY Español** | Traditional + caps especial | Familiar, Ñ incluida |

---

## 2. Layers y Combinaciones Clave - Diseño Recomendado

### Layer 0: BASE (QWERTY/Colemak-DH)

```
// Izquierda                           // Derecha
ESC  1   2   3   4   5                6   7   8   9   0   GRAVE
TAB  Q   W   E   R   T                Y   U   I   O   P   MINUS
LCTL A   S   D   F   G                H   J   K   L   ;   QUOTE
LSFT Z   X   C   V   B       MUTE     N   M   ,   .   /   RSHIFT
                LALT LGUI MO1 SPACE  ENT MO2 BSPC RGUI
```

**Homerow Mods (Hold-Tap):**
```dts
&hm LGUI A    // A tap, LGUI hold
&hm LALT S    // S tap, LALT hold
&hm LCTL D    // D tap, LCTL hold
&hm LSFT F    // F tap, LSFT hold
```

### Layer 1: NAV (Navegación y Mouse)

```
// Izquierda                           // Derecha
ESC  F1  F2  F3  F4  F5               F6  F7  F8  F9  F10 BSPC
TAB  ESC MUTE PSCR  -   =             PGUP HOME UP  END  DEL SLCK
LCTL CAPS INS  VOLDN VOLU PGDN        LEFT DOWN RGHT PGDN ENTER
LSFT     PAUSE PLAY STOP               WH_U BTN1 MS_U WH_D RSHIFT
                LALT LGUI TRANS SPACE ENT TRANS BSPC RGUI
```

**Navegación:**
- `H J K L` = Vim-style (Left/Down/Up/Right)
- `Home/End/PgUp/PgDn` accesibles

### Layer 2: SYM (Símbolos y Números)

```
// Izquierda                           // Derecha
ESC  !   @   #   $   %                ^   &   *   (   )   GRAVE
TAB  1   2   3   4   5                6   7   8   9   0   MINUS
LCTL !   @   #   $   %                ^   &   *   (   )   PLUS
LSFT     [   {   }   ]                _   +   {   }   |   RSHIFT
                LALT LGUI MO1  SPACE ENT TRANS BSPC RGUI
```

### Layer 3: FUNCT (Function Keys + Sistema)

```
// Izquierda                           // Derecha
ESC  F1  F2  F3  F4  F5               F6  F7  F8  F9  F10 F11
TAB       F12  CAPS PSCR SLCK PAUS    BT_CLR BT1 BT2 BT3 BT4 BT5
LCTL      APP  INS  DEL  MENU                        CAPS
LSFT                                          RESET
                LALT LGUI MO1  SPACE ENT MO2 BSPC RGUI
```

---

## 3. Atajos Específicos

### 3.1 Captura de Pantalla

**Windows (Win+Shift+S):**
```dts
screenshot_win: screenshot_win {
    compatible = "zmk,behavior-macro";
    #binding-cells = <0>;
    wait-ms = <10>;
    tap-ms = <10>;
    bindings
        = <&macro_press &kp LGUI>
        , <&macro_tap &kp LS(LSG(N3))>
        , <&macro_release &kp LGUI>;
};
```

**macOS (Cmd+Shift+4 para selección):**
```dts
screenshot_mac_sel: screenshot_mac_sel {
    compatible = "zmk,behavior-macro";
    #binding-cells = <0>;
    wait-ms = <10>;
    tap-ms = <10>;
    bindings
        = <&macro_press &kp LGUI>
        , <&macro_press &kp LSHFT>
        , <&macro_tap &kp N4>
        , <&macro_release &kp LSHFT>
        , <&macro_release &kp LGUI>;
};
```

**macOS (Cmd+Shift+3 pantalla completa):**
```dts
screenshot_mac_full: screenshot_mac_full {
    compatible = "zmk,behavior-macro";
    #binding-cells = <0>;
    wait-ms = <10>;
    tap-ms = <10>;
    bindings
        = <&macro_press &kp LGUI>
        , <&macro_press &kp LSHFT>
        , <&macro_tap &kp N3>
        , <&macro_release &kp LSHFT>
        , <&macro_release &kp LGUI>;
};
```

### 3.2 Cambio de Aplicaciones (Alt+Tab / Cmd+Tab)

**Con Alt/Gui (Windows/macOS):**
```dts
app_switch_next: app_switch_next {
    compatible = "zmk,behavior-macro";
    #binding-cells = <0>;
    wait-ms = <50>;
    tap-ms = <50>;
    bindings
        = <&macro_press &kp LALT>
        , <&macro_pause_for_release>
        , <&macro_tap &kp TAB>
        , <&macro_release &kp LALT>;
};

app_switch_prev: app_switch_prev {
    compatible = "zmk,behavior-macro";
    #binding-cells = <0>;
    wait-ms = <50>;
    tap-ms = <50>;
    bindings
        = <&macro_press &kp LALT>
        , <&macro_press &kp LSHFT>
        , <&macro_pause_for_release>
        , <&macro_tap &kp TAB>
        , <&macro_release &kp LSHFT>
        , <&macro_release &kp LALT>;
};
```

### 3.3 Control de Ventanas (Windows Snap)

```dts
// Windows: Win+Left/Right/Up/Down para snap
win_snap_left: win_snap_left {
    compatible = "zmk,behavior-macro";
    #binding-cells = <0>;
    bindings
        = <&macro_press &kp LGUI>
        , <&macro_tap &kp LEFT>
        , <&macro_release &kp LGUI>;
};

win_snap_right: win_snap_right {
    compatible = "zmk,behavior-macro";
    #binding-cells = <0>;
    bindings
        = <&macro_press &kp LGUI>
        , <&macro_tap &kp RIGHT>
        , <&macro_release &kp LGUI>;
};
```

---

## 4. Configuración de Mouse Keys

### Habilitar Mouse Keys

En tu archivo `.conf`:
```
CONFIG_ZMK_POINTING=y
```

### Layer de Mouse

```dts
#include <dt-bindings/zmk/pointing.h>

mouse_layer {
    bindings = <
    //      MS_U (arriba)
    // MS_L    MS_D    MS_R
    // (izq)  (abajo)  (der)
    
    &trans      &mmv MOVE_UP    &trans
    &mmv LEFT   &mmv MOVE_DOWN  &mmv RIGHT    &trans
    &msc LEFT   &mkp MB1        &msc RIGHT    &trans
    &msc UP     &msc DOWN       &trans
                &mkp MB2        &mkp MB3
    >;
};
```

### Mouse Keys Avanzadas

```dts
// Velocidad personalizada
&mmv {
    time-to-max-speed-ms = <400>;
    acceleration-exponent = <1>;
};

// Scroll más lento
&msc {
    time-to-max-speed-ms = <800>;
    acceleration-exponent = <0>;
};
```

---

## 5. Configuración Avanzada ZMK

### 5.1 Homerow Mods Optimizados (Timeless)

```dts
#include <dt-bindings/zmk/keys.h>
#include <behaviors.dtsi>

/ {
    behaviors {
        // Homerow mods para mano izquierda
        hml: home_row_mod_left {
            compatible = "zmk,behavior-hold-tap";
            #binding-cells = <2>;
            flavor = "balanced";
            require-prior-idle-ms = <150>;
            tapping-term-ms = <280>;
            quick-tap-ms = <175>;
            bindings = <&kp>, <&kp>;
            hold-trigger-key-positions = <6 7 8 9 10 11>; // teclas derecha
            hold-trigger-on-release;
        };
        
        // Homerow mods para mano derecha
        hmr: home_row_mod_right {
            compatible = "zmk,behavior-hold-tap";
            #binding-cells = <2>;
            flavor = "balanced";
            require-prior-idle-ms = <150>;
            tapping-term-ms = <280>;
            quick-tap-ms = <175>;
            bindings = <&kp>, <&kp>;
            hold-trigger-key-positions = <0 1 2 3 4 5>; // teclas izquierda
            hold-trigger-on-release;
        };
    };
};
```

### 5.2 Combos Útiles

```dts
/ {
    combos {
        compatible = "zmk,combos";
        
        // ESC: presionar Q+W simultáneamente
        combo_esc {
            timeout-ms = <50>;
            key-positions = <1 2>; // Q y W (posiciones aproximadas)
            bindings = <&kp ESC>;
        };
        
        // CAPS: presionar A+S simultáneamente
        combo_caps {
            timeout-ms = <50>;
            key-positions = <13 14>; // A y S
            bindings = <&kp CAPS>;
        };
        
        // TAB: presionar J+K simultáneamente  
        combo_tab {
            timeout-ms = <50>;
            key-positions = <17 18>; // J y K
            bindings = <&kp TAB>;
        };
        
        // ENTER: presionar K+L simultáneamente
        combo_enter {
            timeout-ms = <50>;
            key-positions = <18 19>; // K y L
            bindings = <&kp RET>;
        };
        
        // Backspace: presionar U+I simultáneamente
        combo_bspc {
            timeout-ms = <50>;
            key-positions = <15 16>; // U e I
            bindings = <&kp BSPC>;
        };
        
        // Delete: presionar I+O simultáneamente
        combo_del {
            timeout-ms = <50>;
            key-positions = <16 17>; // I y O
            bindings = <&kp DEL>;
        };
    };
};
```

### 5.3 Conditional Layers (Tri-layer)

```dts
/ {
    conditional_layers {
        compatible = "zmk,conditional-layers";
        
        // Activar layer ADJUST cuando LOWER+RAISE están activos
        tri_layer {
            if-layers = <1 2>;
            then-layer = <3>;
        };
    };
};
```

### 5.4 One-Shot Modifiers (Sticky Keys)

```dts
/ {
    behaviors {
        // Sticky shift para capitalizar
        ss_shift: ss_shift {
            compatible = "zmk,behavior-sticky-key";
            #binding-cells = <1>;
            bindings = <&kp>;
            release-after-ms = <2000>;
            quick-release;
        };
        
        // Sticky ctrl
        ss_ctrl: ss_ctrl {
            compatible = "zmk,behavior-sticky-key";
            #binding-cells = <1>;
            bindings = <&kp>;
            release-after-ms = <2000>;
            quick-release;
        };
    };
};

// Uso en keymap
// &ss_shift LSHFT  // Tap una vez, shift actúa en siguiente tecla
```

### 5.5 Macros para Español

```dts
/ {
    macros {
        // Ñ
        enye: enye {
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            bindings = <&kp N WITH TILDE>;
        };
        
        // ¿
        question_inv: question_inv {
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            wait-ms = <10>;
            bindings = <&kp LS(RA(MINUS))>;
        };
        
        // ¡
        exclaim_inv: exclaim_inv {
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            wait-ms = <10>;
            bindings = <&kp LS(EQUAL)>;
        };
    };
};
```

---

## 6. Keymap Completo Recomendado para Lily58

```dts
/*
 * Lily58 Keymap Optimizado - Productividad Sin Ratón
 * Basado en principios de Miryoku + personalización español
 */
#include <behaviors.dtsi>
#include <dt-bindings/zmk/bt.h>
#include <dt-bindings/zmk/ext_power.h>
#include <dt-bindings/zmk/keys.h>
#include <dt-bindings/zmk/rgb.h>
#include <dt-bindings/zmk/pointing.h>

// ========== BEHAVIORS PERSONALIZADOS ==========

/ {
    // Homerow mods timeless
    behaviors {
        hm: homerow_mod {
            compatible = "zmk,behavior-hold-tap";
            #binding-cells = <2>;
            flavor = "balanced";
            require-prior-idle-ms = <150>;
            tapping-term-ms = <280>;
            quick-tap-ms = <175>;
            bindings = <&kp>, <&kp>;
        };
    };
    
    // ========== COMBOS ==========
    combos {
        compatible = "zmk,combos";
        
        combo_esc {
            timeout-ms = <50>;
            key-positions = <24 25>; // Q+W posición basada en keymap Lily58
            bindings = <&kp ESC>;
        };
        
        combo_enter {
            timeout-ms = <50>;
            key-positions = <40 41>; // J+K
            bindings = <&kp RET>;
        };
        
        combo_bspc {
            timeout-ms = <50>;
            key-positions = <38 39>; // H+J
            bindings = <&kp BSPC>;
        };
        
        combo_tab {
            timeout-ms = <50>;
            key-positions = <36 37>; // U+I
            bindings = <&kp TAB>;
        };
    };
    
    // ========== MACROS ==========
    macros {
        // Screenshot Windows
        scr_win: scr_win {
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            wait-ms = <10>;
            bindings
                = <&macro_press &kp LGUI>
                , <&macro_tap &kp LS(LSG(N3))>
                , <&macro_release &kp LGUI>;
        };
        
        // Alt+Tab
        alt_tab: alt_tab {
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            bindings
                = <&macro_press &kp LALT>
                , <&macro_tap &kp TAB>
                , <&macro_release &kp LALT>;
        };
        
        // Ctrl+F (buscar)
        ctrl_f: ctrl_f {
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            bindings
                = <&macro_press &kp LCTRL>
                , <&macro_tap &kp F>
                , <&macro_release &kp LCTRL>;
        };
    };
    
    // ========== CONDITIONAL LAYERS ==========
    conditional_layers {
        compatible = "zmk,conditional-layers";
        
        tri_layer {
            if-layers = <1 2>;
            then-layer = <3>;
        };
    };
    
    // ========== KEYMAP ==========
    keymap {
        compatible = "zmk,keymap";
        
        // Layer 0: BASE
        default_layer {
            display-name = "Base";
            bindings = <
                &kp ESC   &kp N1    &kp N2    &kp N3    &kp N4    &kp N5                          &kp N6   &kp N7    &kp N8    &kp N9    &kp N0     &kp GRAVE
                &kp TAB   &kp Q     &kp W     &kp E     &kp R     &kp T                           &kp Y    &kp U     &kp I     &kp O     &kp P      &kp MINUS
                &hm LCTL A &hm LALT S &hm LSFT D &hm LGUI F &kp G                    &kp H    &hm LGUI J &hm LSFT K &hm LALT L &kp SEMI  &kp SQT
                &kp LSHFT &kp Z     &kp X     &kp C     &kp V     &kp B    &kp C_MUTE   &rgb_ug RGB_TOG  &kp N    &kp M     &kp COMMA &kp DOT   &kp FSLH   &kp RSHFT
                                              &kp LALT  &kp LGUI  &mo 1   &kp SPACE     &kp RET          &mo 2    &kp BSPC  &kp RGUI
            >;
        };
        
        // Layer 1: NAV/MOUSE
        nav_layer {
            display-name = "Navigation";
            bindings = <
                &kp GRAVE &kp F1    &kp F2    &kp F3    &kp F4    &kp F5                          &kp F6    &kp F7   &kp F8    &kp F9    &kp F10    &kp F11
                &kp TAB   &kp ESC   &mmv UP   &kp PSCR  &kp INS   &kp CAPS                        &kp PGUP  &kp HOME &mmv UP   &kp END   &kp DEL    &kp F12
                &kp LCTL  &mmv LEFT &mmv DOWN &mmv RIGHT &kp DEL  &kp PGDN                        &mmv LEFT &mmv DOWN &mmv RIGHT &kp DOWN  &kp UP     &kp ENTER
                &kp LSHFT &kp PAUSE &kp C_PP  &kp C_VOL_UP &kp C_VOL_DN &trans &trans    &trans  &kp PGDN  &kp HOME &kp LEFT  &kp DOWN   &kp UP     &kp RSHFT
                                               &kp LALT  &kp LGUI  &trans    &trans        &kp RET         &mo 2     &kp BSPC  &mkp MB1
            >;
            sensor-bindings = <&inc_dec_kp C_VOL_UP C_VOL_DN &inc_dec_kp PG_UP PG_DN>;
        };
        
        // Layer 2: SYMBOLS/NUMBERS
        sym_layer {
            display-name = "Symbols";
            bindings = <
                &kp TILDE &kp EXCL  &kp AT    &kp HASH  &kp DOLLAR &kp PRCNT                       &kp CARET &kp AMPS &kp ASTRK &kp LPAR  &kp RPAR   &kp GRAVE
                &kp TAB   &kp N1    &kp N2    &kp N3    &kp N4      &kp N5                          &kp N6    &kp N7   &kp N8    &kp N9    &kp N0     &kp MINUS
                &kp LCTL  &kp EXCL  &kp AT    &kp HASH  &kp DOLLAR  &kp PRCNT                       &kp CARET &kp AMPS &kp ASTRK &kp LPAR  &kp RPAR   &kp PLUS
                &kp LSHFT &kp LBRC  &kp RBRC  &kp LCBR  &kp RCBR    &kp PIPE  &trans    &trans  &kp MINUS &kp PLUS &kp LBRC   &kp RBRC  &kp BSLH   &kp RSHFT
                                               &kp LALT  &kp LGUI    &mo 1     &kp SPACE    &kp RET         &trans    &kp BSPC  &kp RGUI
            >;
        };
        
        // Layer 3: ADJUST (tri-layer)
        adjust_layer {
            display-name = "Adjust";
            bindings = <
                &bt BT_CLR &bt BT_SEL 0 &bt BT_SEL 1 &bt BT_SEL 2 &bt BT_SEL 3 &bt BT_SEL 4           &trans    &trans   &trans    &trans    &trans     &trans
                &rgb_ug RGB_HUD &rgb_ug RGB_HUI &rgb_ug RGB_SAD &rgb_ug RGB_SAI &rgb_ug RGB_EFF &trans           &trans    &trans   &trans    &trans    &trans     &trans
                &trans    &rgb_ug RGB_BRD &rgb_ug RGB_BRI &trans &trans &trans                          &trans    &trans   &trans    &trans    &trans     &trans
                &trans    &trans    &trans    &trans    &trans    &trans    &trans    &trans  &trans    &trans   &trans    &trans    &trans     &trans
                                             &kp LALT  &kp LGUI  &trans    &trans        &trans          &trans    &trans    &trans
            >;
            sensor-bindings = <&inc_dec_kp C_VOL_UP C_VOL_DN>;
        };
        
        // Layers reservados para expansión
        extra1 { status = "reserved"; };
        extra2 { status = "reserved"; };
        extra3 { status = "reserved"; };
        extra4 { status = "reserved"; };
        extra5 { status = "reserved"; };
    };
};
```

---

## 7. Mejores Prácticas Encontradas

### 7.1 Reducción de Uso del Ratón

1. **Homerow Mods:** Reemplazan la necesidad de mover las manos para modificadores
2. **Mouse Keys Layer:** Capa dedicada con movimiento de cursor
3. **Combos para acciones comunes:** ESC, TAB, ENTER accesibles sin mover manos
4. **Vim-style navigation:** H/J/K/L como flechas en layer NAV
5. **Macros para Windows Snap:** Control de ventanas sin ratón

### 7.2 Ergonomía

1. **Timeless homerow mods:** Configuración `require-prior-idle-ms` evita activaciones accidentales
2. **Thumbs para layers:** Space/Enter como thumb primary, layers como thumb secondary
3. **Combos con timeout corto (50ms):** Reduce errores
4. **Tapping term 280ms:** Balance entre velocidad de escritura y activación de mods

### 7.3 Productividad para Programación

1. **Layer SYM con símbolos agrupados:** Paréntesis, corchetes, llaves juntos
2. **Vim-style HJKL:** Consistente con editores Vim
3. **Macros para snippets frecuentes:** `ctrl+f`, `ctrl+s`, etc.
4. **Tri-layer para ajustes:** Lower+Raise activa Adjust sin acceso directo

### 7.4 Configuración para Español

1. **Layer EXTRA:** Ñ, ¿, ¡ en posición accesible
2. **Dead keys:** Configurar acentos con combos
3. **Locale:** Ajustar keymap según distribución (ES/ES_LATIN)

---

## 8. Recursos Adicionales

### Repositorios GitHub
- Miryoku ZMK: https://github.com/manna-harbour/miryoku_zmk
- ZMK Official: https://github.com/zmkfirmware/zmk
- Awesome Split Keyboards: https://github.com/diim/awesome-split-keyboards

### Comunidades
- Reddit r/ErgoMechKeyboards
- ZMK Discord: https://zmk.dev/community/discord/invite
- ZMK Documentation: https://zmk.dev/docs

### Herramientas
- ZMK Studio: https://zmk.studio (configuración visual)
- Keyboard Layout Editor: https://keyboard-layout-editor.com
- ZMK Power Profiler: https://zmk.dev/tools/power-profiler

---

## 9. Próximos Pasos Recomendados

1. **Probar Miryoku:** Clonar repo miryoku_zmk y personalizar
2. **Configurar Homerow Mods:** Implementar con `require-prior-idle-ms`
3. **Añadir Mouse Keys:** Habilitar `CONFIG_ZMK_POINTING=y`
4. **Crear Combos:** ESC, TAB, ENTER en posiciones accesibles
5. **Personalizar para Español:** Añadir Ñ, ¿, ¡ en layer extra
6. **Progresivamente:** Empezar con QWERTY familiar, luego probar Colemak-DH

---

## 10. Referencia Rápida de Códigos ZMK

```dts
// Behaviors comunes
&kp              // Key press
&mo LAYER        // Momentary layer (hold)
&lt LAYER KEY    // Layer-tap (hold=layer, tap=key)
&mt MOD KEY      // Mod-tap (hold=modifier, tap=key)
&sk MODIFIER     // Sticky key (one-shot mod)
&to LAYER        // Toggle layer

// Sticky layer
&sl LAYER        // Sticky layer (activa hasta próxima tecla)

// Keycodes útiles
C_MUTE, C_VOL_UP, C_VOL_DN    // Audio
RGB_TOG, RGB_HUI, RGB_SAI    // RGB
BT_SEL, BT_CLR              // Bluetooth

// Mouse keys (requiere CONFIG_ZMK_POINTING=y)
&mkp MB1, &mkp MB2, &mkp MB3  // Mouse buttons
&mmv MOVE_UP/DOWN/LEFT/RIGHT   // Mouse movement
&msc SCRL_UP/DOWN/LEFT/RIGHT   // Mouse scroll
```

---

*Documento generado como resultado de investigación para optimizar el teclado Lily58 con ZMK firmware.*