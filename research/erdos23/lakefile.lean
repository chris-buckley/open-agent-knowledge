import Lake

open Lake DSL

package Erdos23 where
  version := v!"0.1.0"

require mathlib from git "https://github.com/leanprover-community/mathlib4.git" @
  "a3a10db0e9d66acbebf76c5e6a135066525ac900"

@[default_target]
lean_lib Erdos23
