# Prompting Template for Code Tasks

Use this format when requesting implementation work so requirements are explicit and testable.

## 1) Goal

State exactly what should be built.

- Bad: "write a function"
- Good: "Write a Python function that calculates factorial for non-negative integers."

## 2) Input / Output Requirements

Define full contracts.

- Input: expected types, ranges, constraints
- Output: type, schema/format, ordering
- Edge cases: null/empty values, invalid ranges, missing fields

## 3) Constraints and Context

Include runtime and style context.

- Language/runtime (Python 3.x, Rust, Node)
- Required libraries/frameworks
- Style conventions (PEP8, clippy constraints, naming)
- Existing code to integrate with (file paths + signatures)

## 4) Iteration Strategy

- Start with a minimal prompt
- Ask for explanation if logic is unclear
- Break large tasks into smaller milestones

## Reusable Prompt Template

```text
Write a [Language] function to [Task].

Input:
- [Input schema, types, constraints]

Output:
- [Output schema, types, formatting]

Edge Cases:
- [Case 1]
- [Case 2]

Constraints:
- [Libraries/runtime/style]
- [Performance target, if any]

Focus on:
- [Readability | correctness | efficiency | testability]
```

## Example

```text
Write a Python function to compute GCD of two positive integers using the Euclidean algorithm.
Input: integers a, b.
Output: integer gcd.
Edge cases: if a == 0 or b == 0 return 0.
Constraints: PEP8, include docstring and unit tests.
Focus on correctness and readability.
```
