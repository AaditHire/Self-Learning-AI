# AST adjudicator v1 failure diagnosis (written before v2 implementation)

The frozen v1 fixture suite is `ADJUDICATOR_DEVELOPMENT_REGRESSION_FIXTURES_V1`. Its expected labels remain unchanged. In particular, `superficial_spacing_and_case` expects `PROHIBITED_STRUCTURAL_TEMPLATE_REUSE` and the observed v1 result was `COARSE_AST_EQUALITY_ONLY`. The original fixture and v1 implementation are unchanged.

## Exact failed programs

Original:

```goco
NUMBER n. INPUT(n). NUMBER total=0. LOOP (NUMBER i=1 TILL i<=n, i++) { IF (i%2==1) { total+=1. } } DISPLAYNL(total).
```

Transformed:

```goco
number n.input(n).number total=0. loop(number i=1 till i<=n,i++){if(i%2==1){total+=1.}}displaynl(total).
```

The intended transformation removes optional whitespace and changes the case of keywords to GOCO-supported lower-case spellings. It preserves identifier spelling, punctuation, operators, literals, statement order, control flow and dataflow.

## GOCO syntax and semantic validity

The pinned GOCO grammar (`goco-compiler/src/main/java/parser/MyLanguageParser.jj`) defines `ID`, `DOT`, and `INPUT_CMD` as separate tokens. Its `INPUT_CMD` accepts `INPUT` and `input`; the type, loop, till, if and display commands also explicitly accept the lower-case spellings used here. Thus `n.input(n)` is parsed as `ID(n) DOT INPUT_CMD(input) LPAREN ID(n) RPAREN`, *not* a library call. Both complete programs parse and run successfully under the pinned compiler (SHA-256 `42478b3500ff31df65f411e4072f578be5fede844020392a664eb89865b2a2fb`). For input `n=0,1,2,3,4`, both yielded respectively `0.0,1.0,1.0,2.0,2.0`. Their shared semantics are counting odd positions from 1 through n. The transformation is genuinely superficial for structural template detection.

## Parser representation and v1 comparisons

The GOCO grammar yields the same abstract program tree for both after keyword-case normalization:

```text
Program[
  Declare(NUMBER,n), Input(n), Declare(NUMBER,total,0),
  Loop(init=Declare(NUMBER,i,1), condition=(i<=n), step=(i++),
       body=[If(condition=((i%2)==1), body=[AddAssign(total,1)])]),
  DisplayNL(total)
]
```

This is a grammar-derived tree description; v1 did **not** construct or compare this AST. V1 compared (1) the old coarse `ast_proxy` string and (2) exact equality of its alpha-normalized lexical tuple. The coarse strings are equal:

```text
INPUT>LOOP><=>+>+>IF>%>==>+=>DISPLAYNL
```

V1's `TOKEN` regex places an `API` alternative before `IDENT` and `PUNCT` and matches any `identifier.identifier`. At the first declaration boundary the original source gives `IDENT(n), PUNCT(.), IDENT(INPUT)`, whereas the transformed source gives the single `API(n.input)` token. The normalized structural tuples first differ at index 1:

```text
original:    NUMBER, VAR0, ., INPUT, (, VAR0, ), ., NUMBER, VAR1, ...
transformed: NUMBER, API:N.INPUT, (, VAR0, ), ., NUMBER, VAR1, ...
```

The complete compared v1 tuple fields, in order, are: normalized GOCO keywords; alpha-renamed identifiers by first occurrence; API tokens with upper-cased text; numeric `NUM` and string `STRING` placeholders; operators; punctuation and grouping tokens. Whitespace/comments are discarded. The left tuple has 48 fields and the right tuple 46 because the `API` regex swallowed two token boundaries. The first difference is the declaration's variable/dot/next keyword sequence, before any loop or predicate. V1 then found unequal enhanced tuples but equal coarse proxies and returned `COARSE_AST_EQUALITY_ONLY` by its second branch.

**Root cause:** lexical canonicalization defect and parser sensitivity in v1's regex-based pseudo-AST. It incorrectly treats a statement terminator followed immediately by a keyword as an API separator. No task-essential feature was lost or changed; the fixture specification is valid. This diagnosis was recorded before editing v2 implementation.
