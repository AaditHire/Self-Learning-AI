# GOCO

## How to work with `javacc`

> Note: **DO NOT** make changes in `goco-comiler/src/main/java/parser/*.java`.<br>
> These files are made by `goco-comiler\src\main\java\parser\MyLanguageParser.jj` automatically while compiling

> For debug printing:
>
> - set `ENABLED` in `goco-comiler/src/main/java/utils/Debug.java` to `true`
> - uncomment `echo` in `goco-comiler/tests/run.bat`

### How to compile `MyLanguageParser.jj`

```powershell
goco-comiler\src\main\java\parser> javacc MyLanguageParser.jj
goco-comiler\src\main\java\parser> javac *.java
```

### How to run `.goco` files

How to run any .goco file in `goco-comiler/tests`

```powershell
goco-comiler\tests> ./run.bat <goco_file_to_run>.goco
```

How to run all tests from `goco-comiler/tests/tests`

```powershell
goco-comiler\tests> python run_tests.py
```

## Language Documentation (GOCO Syntax)

### Data Types

- `NUMBER`: Numeric values (integers and floats). Example: `NUMBER x = 5.`
- `LETTER`: Single characters. Example: `LETTER c = 'a'.`
- `SENTENCE`: Strings. Example: `SENTENCE s = "Hello, World".`
- `LOGIC`: Boolean values (`TRUE` or `FALSE`). Example: `LOGIC b = TRUE.`
- **Arrays**: Denoted by appending `[]` to the type. Example: `NUMBER[] arr = [1, 2, 3].`

### Variables and Assignments

All non-control statements must end with a period (`.`).

**Declaration:**

```java
NUMBER num = 42.
SENTENCE msg.
```

**Assignment & Compound Assignment:**

```java
msg = "Welcome".
num += 10.
num++.
```

### Display and Input

- `DISPLAY(expr).`: Prints without a newline.
- `DISPLAYNL(expr).`: Prints with a newline.
- `INPUT(var).`: Reads user input into a variable.

```java
DISPLAYNL("Enter a number:").
INPUT(x).
DISPLAYNL("You entered: " + x).
```

### Control Flow

**If-ElseIf-Else:**

```java
IF (x > 10) {
    DISPLAYNL("Large").
} ELSEIF (x > 5) {
    DISPLAYNL("Medium").
} ELSE {
    DISPLAYNL("Small").
}
```

**Switch-Case:**

```java
SWITCH (x) {
    CASE (1) {
        DISPLAYNL("One").
    }
    CASE (2) {
        DISPLAYNL("Two").
    }
    DEFAULT {
        DISPLAYNL("Other").
    }
}
```

### Loops

**While Loop:**

```java
NUMBER i = 0.
LOOP (i < 5) {
    DISPLAYNL(i).
    i++.
}
```

**For Loop:**

```java
LOOP (NUMBER i = 0 TILL i < 5, i++) {
    DISPLAYNL(i).
}
```

**Do-While Loop:**

```java
NUMBER x = 0.
DO {
    x++.
} LOOP (x < 5).
```

**Loop Controls:**
`BREAK.` and `CONTINUE.` are supported.

### Arrays

**Declaration and Initialization:**

```java
NUMBER[] arr1 = [1, 2, 3].
NUMBER[] arr2 = NEW NUMBER[5].
```

**Array Operations:**

- `PUSH(arr, val).`: Adds `val` to the end of `arr`.
- `POP(arr).`: Removes the last element from `arr`.
- `SET(arr, index, val).`: Sets the element at `index` to `val`.
- `GET(arr, index).`: Retrieves the element at `index`.
- `LENGTH(arr_or_string)`: Returns the length of the array or string.

```java
NUMBER[] primes = [2, 3, 5].
PUSH(primes, 7).
DISPLAYNL(GET(primes, 0)). // Output: 2
SET(primes, 0, 11).
DISPLAYNL(LENGTH(primes)). // Output: 4
```

### Functions

Functions are declared using the `FUNCTION` keyword and can optionally return a value using `RETURNS`. Note that function declarations do not require a terminating period, but the `RETURN` statements inside do.

**Function without return value (VOID):**

```java
FUNCTION greet(SENTENCE name) {
    DISPLAYNL("Hello, " + name).
}
greet("World").
```

**Function with return value:**

```java
FUNCTION add(NUMBER a, NUMBER b) {
    RETURN a + b.
} RETURNS NUMBER
NUMBER sum = add(5, 10).
```

**Functions with Default Parameters:**

```java
FUNCTION greet(SENTENCE name, SENTENCE greeting = "Hello") {
    DISPLAYNL(greeting + ", " + name).
}
```

### Operators & Expressions

- **Arithmetic:** `+`, `-`, `*`, `/`, `%`
- **String Concatenation:** `+` (e.g., `"Hello" + " World"`)
- **Comparison:** `==`, `!=`, `<`, `>`, `<=`, `>=`
- **Logical:** `&&` (AND), `||` (OR), `!`, `NOT`
- **Unary:** `-` (Negative)

### Things to work with (in `MyLanguageParser.jj` & `MyLanguageParser.java`)

| ReturnNodeType   | ReturnNodeName           | ParserMethods         | WhatItDoes                                                                                                                                                   |
| ---------------- | ------------------------ | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| CoreNodes        | .ASTNode                 | StatementWithRecovery | Parses one statement and checks that it ends with `.`. Throws an error if the terminator is missing.                                                         |
| CoreNodes        | .ASTNode                 | Program               | Parses the entire program as a sequence of statements until end of file and stores them in a ProgramNode.                                                    |
| CoreNodes        | .ASTNode                 | Statement             | Determines which type of statement appears next. Routes to control statements or non-control statements.                                                     |
| CoreNodes        | .ASTNode                 | IfStatement           | Parses an `IF` condition with optional `ELSEIF` and `ELSE` blocks and builds an IfNode with nested statements.                                               |
| ConditionalNodes | .ElseIfNode              | ElseIfBlock           | Parses an `ELSEIF` condition block and stores its statements.                                                                                                |
| ConditionalNodes | .ElseNode                | ElseBlock             | Parses an `ELSE` block and stores its statements.                                                                                                            |
| CoreNodes        | .ASTNode                 | DoWhileStatement      | Parses a `DO { ... } LOOP(condition).` structure and creates a DoWhileNode.                                                                                  |
| CoreNodes        | .ASTNode                 | LoopStatement         | Parses loop constructs. Handles while-style loops and for-style loops with initialization, condition, and update.                                            |
| CoreNodes        | .ASTNode                 | SwitchStatement       | Parses a `SWITCH(expression)` block with multiple `CASE` clauses and an optional `DEFAULT`.                                                                  |
| SwitchNodes      | .CaseNode                | CaseClause            | Parses one `CASE(expression)` block and collects its statements.                                                                                             |
| SwitchNodes      | .DefaultNode             | DefaultClause         | Parses the `DEFAULT` block of a switch statement.                                                                                                            |
| CoreNodes        | .ASTNode                 | ForLoopInit           | Parses the initialization part of a for-style loop, either variable declaration or assignment.                                                               |
| CoreNodes        | .ASTNode                 | ForLoopUpdate         | Parses the update expression of a for-style loop such as `i++`, `++i`, or compound assignments.                                                              |
| CoreNodes        | .ASTNode                 | NonControlStatement   | Parses statements that are not control flow. Includes declarations, assignments, array operations, input, output, increment, decrement, break, and continue. |
| CoreNodes        | .ASTNode                 | VarDeclaration        | Parses variable or array declarations with optional assignment.                                                                                              |
| CoreNodes        | .ASTNode                 | PureDeclaration       | Parses a simple variable declaration without assignment.                                                                                                     |
| ExpressionNodes  | .ExpressionNode          | Value                 | Parses literal values, array literals, dynamic arrays with `NEW`, or nested expressions.                                                                     |
| ExpressionNodes  | .ExpressionNode          | Expression            | Entry point for expression parsing. Delegates to logical OR expressions.                                                                                     |
| ExpressionNodes  | .ExpressionNode          | ConcatExpression      | Parses string concatenation using `+`.                                                                                                                       |
| ExpressionNodes  | .ExpressionNode          | OrExpression          | Parses logical OR operations.                                                                                                                                |
| ExpressionNodes  | .ExpressionNode          | AndExpression         | Parses logical AND operations.                                                                                                                               |
| ExpressionNodes  | .ExpressionNode          | NotExpression         | Parses unary logical NOT operations.                                                                                                                         |
| ExpressionNodes  | .ExpressionNode          | ComparisonExpression  | Parses comparison operators such as `>`, `<`, `>=`, `<=`, `==`, `!=`.                                                                                        |
| ExpressionNodes  | .ExpressionNode          | ArithmeticExpression  | Parses addition and subtraction operations.                                                                                                                  |
| ExpressionNodes  | .ExpressionNode          | Term                  | Parses multiplication, division, and modulus operations.                                                                                                     |
| CoreNodes        | .ASTNode                 | Assignment            | Parses variable or array assignments, including compound assignments and dynamic array creation.                                                             |
| CoreNodes        | .ASTNode                 | DisplayStatement      | Parses `DISPLAY` and `DISPLAYNL` output statements.                                                                                                          |
| CoreNodes        | .ASTNode                 | InputStatement        | Parses `INPUT` statements for variables or array elements.                                                                                                   |
| ExpressionNodes  | .ExpressionNode          | Factor                | Parses the smallest expression units such as literals, variables, array access, function calls, increments, and parenthesized expressions.                   |
| FunctionNodes    | .FunctionDeclarationNode | FunctionDeclaration   | Parses the definition and body of user-defined functions, storing parameter names and default values.                                                        |
| FunctionNodes    | .FunctionCallNode        | FunctionCall          | Parses a function call and the required arguments, checking parameter lengths at runtime.                                                                    |
| FunctionNodes    | .ReturnNode              | ReturnStatement       | Parses `RETURN` expressions to end function execution early with a value.                                                                                    |

## Notes for Devs

> Note: USE **`java 25.0.1`** ONLY.

- Parentheses
  - `(` -> `\u0028`
  - `)` -> `\u0029`
- Curly braces
  - `{` -> `\u007B`
  - `}` -> `\u007D`
- Square brackets
  - `[` -> `\u005B`
  - `]` -> `\u005D`
- Extra (often useful)
  - `.` -> `\u002E`
  - `,` -> `\u002C`
  - `=` -> `\u003D`
