// SPDX-License-Identifier: Apache-2.0
// Academic paper layout: centered title and authors, indented abstract, numbered sections,
// captioned grid tables, shaded code blocks, and a numbered reference list.

#let link-color = rgb(45, 70, 185)

#let paper(title: "", authors: (), abstract: none, body) = {
  set document(title: title, author: authors.map(a => a.name))
  set page(
    paper: "us-letter",
    margin: (x: 1.25in, top: 1in, bottom: 1.1in),
    numbering: "1",
    number-align: center,
  )
  set text(font: "New Computer Modern", size: 11pt, lang: "en")
  set par(justify: true, leading: 0.62em, spacing: 1.1em)
  set list(indent: 1em, marker: [•])
  set enum(indent: 1em, numbering: "1)")

  show link: set text(fill: link-color)
  show raw: set text(font: "DejaVu Sans Mono", size: 9pt)
  show raw.where(block: true): block.with(fill: luma(246), inset: 8pt, radius: 2pt, width: 100%)

  set heading(numbering: (..nums) => {
    let n = nums.pos()
    if n.len() == 1 { numbering("1.", ..n) } else { numbering("1.1", ..n) }
  })
  show heading.where(level: 1): it => {
    set text(size: 12pt, weight: "bold")
    v(1.8em, weak: true)
    block(below: 0.8em, it)
  }
  show heading.where(level: 2): it => {
    set text(size: 11pt, weight: "bold", style: "italic")
    v(1.5em, weak: true)
    block(below: 0.7em, it)
  }

  set table(stroke: 0.5pt + black, inset: (x: 6pt, y: 5pt), align: left)
  show table: set par(justify: false)
  show table: set text(size: 10pt, hyphenate: false)
  show table.cell.where(y: 0): set text(weight: "bold")
  show figure.where(kind: table): set figure.caption(position: bottom)
  show figure: set block(above: 1.2em, below: 1.2em)

  // Title block.
  align(center)[
    #v(0.4in)
    #block(text(size: 16pt, weight: "bold", title))
    #v(1.2em)
    #for a in authors [
      #a.name \
      #if "email" in a [#a.email \ ]
      #if "affiliation" in a [#a.affiliation]
      #v(0.6em)
    ]
  ]
  if abstract != none {
    v(1.2em)
    pad(x: 0.55in)[
      #set par(justify: true)
      *Abstract.* #abstract
    ]
  }
  v(2.4em)
  body
}

#let references-header() = {
  pagebreak()
  block(below: 1em, text(size: 12pt, weight: "bold")[References])
}

#let ref-entry(n, body) = block(below: 1.5em)[[#n] #body]
