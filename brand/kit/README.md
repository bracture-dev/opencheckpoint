# OpenCheckpoint brand kit

**Selected identity: Nested / balanced, forest green.** This directory is the approved selection from the exploration round. Use these assets for OpenCheckpoint; the other exploration directories are design studies.

[Preview the identity](index.html).

## Meaning

Two open layers lead into a compact, solid record. They suggest a larger body of work condensed into the context needed to continue. The offset edges preserve a sense of derivation, while four-unit gaps keep the parts distinct at small sizes. The mark represents compact, structured task state—not a transcript archive or a grant of authority.

Name: **OpenCheckpoint**, one word, capital O and C. Never pluralize the name. Tagline: **Pick up where another AI left off.** Voice: informative, plain and precise. Describe what the format records and enables; avoid claims of magic, lossless compression or automatic permission.

## Which asset to use

| Use | File |
|---|---|
| Main identity | lockup-horizontal-light.svg or lockup-horizontal-dark.svg |
| Centered placement | lockup-stacked-light.svg or lockup-stacked-dark.svg |
| Small icon / avatar | mark-light.svg or mark-dark.svg |
| Browser tab | favicon.svg; favicon-16.png and favicon-32.png as light-ink fallbacks |
| One-color application | mark-mono.svg, wordmark-mono.svg, or either lockup-mono.svg |
| Theme-aware external image | mark.svg, wordmark.svg, lockup-horizontal.svg, lockup-stacked.svg |
| Documentation colors | tokens.css |
| Raster-only application | fixed-theme *-light.png and *-dark.png, with transparent backgrounds |

Use the explicit light or dark variants for a known background. The unsuffixed SVGs follow prefers-color-scheme, which may differ from a site's manually selected theme. Mono assets use currentColor; inline them to inherit the surrounding CSS color. An external img cannot inherit that color from its parent.

Keep the mark beside the wordmark when first introducing the standard. Use the mark alone in established contexts such as a browser tab. Do not use the mark as a certification badge, success indicator, or approval control.

## Geometry, spacing and minimum size

The symbol uses a 32 × 32 grid. Its visible bounds are x=2…30 and y=2…30. The two bands are 4 units thick, the channels are 4 units wide, and the retained record is 12 × 12 units. Preserve these proportions; all symbol variants use identical geometry.

Reserve **8 grid units of clear space** outside the symbol canvas on every side. For lockups, reserve at least one quarter of the displayed symbol box around the entire lockup. Keep the supplied symbol-to-wordmark spacing. The horizontal lockup has a 12-unit interval between its 32-unit symbol box and the wordmark box.

- Symbol: minimum 16 × 16 CSS px or 5 mm in print. At 16 px, the bands and gaps are 2 px wide.
- Wordmark: minimum 140 px wide.
- Horizontal lockup: minimum 180 px wide.
- Stacked lockup: minimum 160 px wide.
- Below lockup minimums, use the symbol alone. Scale proportionally; align to whole pixels at small sizes.

## Palette and contrast

| Token | Light | Dark |
|---|---|---|
| --sl-color-accent-low | #E3F0E8 | #1D3428 |
| --sl-color-accent | #386B50 | #9BCBAA |
| --sl-color-accent-high | #214832 | #D4EEDD |
| --sl-color-white | #18212B | #FFFFFF |
| --sl-color-gray-1 | #26313C | #E9EDF2 |
| --sl-color-gray-2 | #3C4753 | #C8D0DA |
| --sl-color-gray-3 | #536171 | #A0ADBC |
| --sl-color-gray-4 | #6F7C8B | #8593A4 |
| --sl-color-gray-5 | #CCD3DC | #394656 |
| --sl-color-gray-6 | #EFF2F6 | #222D3B |
| --sl-color-gray-7 | #F7F9FB | #192331 |
| --sl-color-black | #FFFFFF | #121A24 |

| Mode | Foreground / background | Hex pair | Ratio | Requirement |
|---|---|---|---:|---|
| light | white / black | #18212B / #FFFFFF | 16.26:1 | Body text / links ≥ 4.5:1 |
| light | gray-1 / black | #26313C / #FFFFFF | 13.23:1 | Body text / links ≥ 4.5:1 |
| light | gray-2 / black | #3C4753 / #FFFFFF | 9.47:1 | Body text / links ≥ 4.5:1 |
| light | gray-3 / black | #536171 / #FFFFFF | 6.33:1 | Body text / links ≥ 4.5:1 |
| light | accent / black | #386B50 / #FFFFFF | 6.20:1 | Body text / links ≥ 4.5:1 |
| light | white / gray-6 | #18212B / #EFF2F6 | 14.48:1 | Body text / links ≥ 4.5:1 |
| light | gray-1 / gray-6 | #26313C / #EFF2F6 | 11.78:1 | Body text / links ≥ 4.5:1 |
| light | gray-2 / gray-6 | #3C4753 / #EFF2F6 | 8.43:1 | Body text / links ≥ 4.5:1 |
| light | gray-3 / gray-6 | #536171 / #EFF2F6 | 5.64:1 | Body text / links ≥ 4.5:1 |
| light | accent / gray-6 | #386B50 / #EFF2F6 | 5.52:1 | Body text / links ≥ 4.5:1 |
| light | accent-high / accent-low | #214832 / #E3F0E8 | 8.78:1 | Callout text ≥ 4.5:1 |
| light | gray-4 / black | #6F7C8B / #FFFFFF | 4.26:1 | Essential UI border ≥ 3:1 |
| light | gray-4 / gray-6 | #6F7C8B / #EFF2F6 | 3.79:1 | Essential UI border ≥ 3:1 |
| light | black / accent | #FFFFFF / #386B50 | 6.20:1 | Solid button text ≥ 4.5:1 |
| dark | white / black | #FFFFFF / #121A24 | 17.52:1 | Body text / links ≥ 4.5:1 |
| dark | gray-1 / black | #E9EDF2 / #121A24 | 14.90:1 | Body text / links ≥ 4.5:1 |
| dark | gray-2 / black | #C8D0DA / #121A24 | 11.25:1 | Body text / links ≥ 4.5:1 |
| dark | gray-3 / black | #A0ADBC / #121A24 | 7.67:1 | Body text / links ≥ 4.5:1 |
| dark | accent / black | #9BCBAA / #121A24 | 9.61:1 | Body text / links ≥ 4.5:1 |
| dark | white / gray-6 | #FFFFFF / #222D3B | 13.94:1 | Body text / links ≥ 4.5:1 |
| dark | gray-1 / gray-6 | #E9EDF2 / #222D3B | 11.86:1 | Body text / links ≥ 4.5:1 |
| dark | gray-2 / gray-6 | #C8D0DA / #222D3B | 8.95:1 | Body text / links ≥ 4.5:1 |
| dark | gray-3 / gray-6 | #A0ADBC / #222D3B | 6.11:1 | Body text / links ≥ 4.5:1 |
| dark | accent / gray-6 | #9BCBAA / #222D3B | 7.64:1 | Body text / links ≥ 4.5:1 |
| dark | accent-high / accent-low | #D4EEDD / #1D3428 | 10.85:1 | Callout text ≥ 4.5:1 |
| dark | gray-4 / black | #8593A4 / #121A24 | 5.59:1 | Essential UI border ≥ 3:1 |
| dark | gray-4 / gray-6 | #8593A4 / #222D3B | 4.45:1 | Essential UI border ≥ 3:1 |
| dark | black / accent | #121A24 / #9BCBAA | 9.61:1 | Solid button text ≥ 4.5:1 |

Ratios use WCAG 2.2 relative sRGB luminance, computed without rounding before comparison; displayed values are rounded to two decimals. Body text and links meet 4.5:1, exceeding the 3:1 large-text requirement. Essential UI borders meet 3:1 against both page and raised surfaces. Only the pairings above are approved: gray-5, gray-6 and gray-7 are surfaces/decorative dividers, not text or essential boundaries. Accent-low is a callout surface, not text. Use accent-high for text on it. For mono, use gray-1 on black; that pairing is measured above.

## Typography

**Public Sans**, weight **600** in the wordmark and headings, **400** for prose. Licensed under **SIL Open Font License 1.1**. The original variable font and full license are bundled in [fonts/](fonts/). Sources: [Public Sans project](https://github.com/uswds/public-sans) and [Google Fonts distribution](https://github.com/google/fonts/tree/main/ofl/publicsans).

All SVG wordmarks and lockups contain glyph outlines; they need no font installed. Do not retype, respell, condense, stretch, or alter the spacing of the wordmark. Public Sans 600 is the chosen weight for the identity; do not substitute another weight in a lockup.

## Docs integration

The token file uses the existing Starlight variable names. Dark is :root; light is :root[data-theme="light"]. It supplies the three accent tokens, white/black, gray-1 through gray-7, and --oc-step-border. Import it after the default theme colors. Keep the site's existing layout rules.

For a manually selected site theme, choose the matching fixed SVG or inline the mark with fill: var(--sl-color-accent). Give a standalone logo image alt="OpenCheckpoint"; if a neighboring accessible wordmark already supplies that name, the decorative symbol should have empty alternative text. These files are prepared for integration; the documentation site itself has not been changed.

## Misuse

- Do not join the layers, narrow the channels, round the corners, or remove the solid record.
- Do not rotate, mirror, shear, or stretch the mark.
- Do not recolor layers as different vendors, add gradients, or apply shadows.
- Do not add a checkmark, arrow, approval seal, vendor initial, or additional frame.

## Confusion review

The nearest generic associations are stacked windows and nested documents. The offset upper endpoints and solid lower-right record distinguish this treatment from identical overlapping window outlines. Square concentric bands can also suggest a squared-off RSS icon; the asymmetric layer ends, L-shaped bands and large rectangular record are intentional differences from RSS arcs and a dot.

The design does not use MCP interlacing, A2A lettering, OpenAI radial knots, Anthropic initials or the Claude burst, Google's G, the CNCF diagonal square, Kubernetes wheels, Git branching nodes, or the Linux mascot. The review is a visual comparison, not exhaustive trademark clearance. No existing logo geometry was imported or traced.

## Package and verification

The kit includes adaptive, fixed-theme and monochrome SVGs, outlined horizontal and stacked lockups, transparent PNG exports, favicon PNGs, font and license, docs tokens, computed contrast data, and light/dark browser proofs. All 28 approved contrast pairs are recomputed; the lowest approved body/link ratio is 5.52:1 and the lowest essential UI ratio is 3.79:1.

The source geometry is the selected Nested / balanced study. The page embeds its font and artwork and can be opened locally. Files and SHA-256 digests are listed in ASSET-MANIFEST.json. See validation-report.json for rendering checks.
