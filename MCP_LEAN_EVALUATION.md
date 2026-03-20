# MCP Lean Tool Evaluation Report
**Date**: February 5, 2026  
**Evaluator**: Claude (via GitHub Copilot)  
**Context**: Formalizing Erdős Problem 530 (KSS Theorem) in Lean 4

---

## Executive Summary

### 🎉 UPDATE: New Features Deployed and Working!

The MCP Lean tool has received **significant improvements**. Three new actions address key weaknesses:

| New Action | Purpose | Status |
|------------|---------|--------|
| `audit_axioms` | Detect custom vs standard axioms | ✅ **Works perfectly** |
| `semantic_search` | Find lemmas by goal type | ✅ **Works perfectly** |
| `fill_sorry_code` | Fill sorry in code snippets (no file needed) | ✅ **Works perfectly** |

**Remaining issues:**
- `search_lemma` returns `(type not resolved)` instead of actual types
- `search_by_type` returns "No matching lemmas found"

**Updated Rating**: 9/10 (Up from 8 - library_search parsing now fixed!)

---

## 🆕 NEW: Successfully Implemented Features

### ✅ NEW FEATURE 1: `audit_axioms` - Axiom Detection

**Test Case**:
```
Action: audit_axioms
Path: D:\Erdos\KSS_Proven.lean
Theorem: kss_sqrt_bound
```

**Result**:
```markdown
⚠️ Custom Axioms (Non-Standard):
| Axiom | Description |
|-------|-------------|
| `KSSProven.kss_two_to_one_map_exists` | Custom axiom |

✅ Standard Axioms (Acceptable):
| `propext` | Propositional extensionality |
| `Classical.choice` | Axiom of choice |
| `Quot.sound` | Quotient soundness |

⚠️ Note: Proof depends on 1 custom axiom(s).
```

✅ **EXCELLENT!** Correctly identifies custom vs standard axioms.

---

### ✅ NEW FEATURE 2: `semantic_search` - Goal-Type-Aware Lemma Search

**Test Case**:
```
Action: semantic_search
Goal Type: "Finset.card (Finset.filter p s) ≤ Finset.card s"
```

**Result**:
```markdown
🔄 Similar Lemmas:
| Lemma | Suggested Tactic | Similarity |
|-------|-----------------|------------|
| `Finset.card_filter_le` | `exact Finset.card_filter_le` | ⭐⭐⭐ |
| `Finset.card_pos` | `exact Finset.card_pos.mpr` | ⭐⭐ |
```

✅ **EXCELLENT!** Finds the exact lemma needed with ready-to-use tactics.

---

### ✅ NEW FEATURE 3: `fill_sorry_code` - Inline Code Snippets

**Test Case**:
```
Action: fill_sorry_code
Code: "example (n : ℕ) : n + 0 = n := sorry"
```

**Result**:
```markdown
✅ Found Proof!
Winning Tactic: `rfl`

Fixed Code:
example (n : ℕ) : n + 0 = n := rfl
```

✅ **EXCELLENT!** No file path needed - works directly on code snippets.

---

## ✅ FIXED: Version Detection Now Works!

**Before** (broken):
```
LEAN_VERSION: Lean (version 4.27.0...)  ← Global default, WRONG
ACTIVE_PROJECT: D:\mathlib-workspace
```

**After** (fixed):
```
LEAN_VERSION: Lean (version 4.28.0-rc1) (from project lean-toolchain)  ← Correct!
ACTIVE_PROJECT: D:\mathlib-workspace
```

✅ The tool now reads the project's `lean-toolchain` file correctly!

---

## Historical Context: Version Detection Bug (Now Fixed)

### The Problem
The MCP tool shows:
```
LEAN_VERSION: Lean (version 4.27.0...)
ACTIVE_PROJECT: D:\mathlib-workspace
WORKFLOW (Lean 4.28+)
```

But the **active project may use a completely different version**!

### Why This Matters for All Users

Users can have **multiple Lean versions** installed via `elan`:
```powershell
PS> elan show
installed toolchains
--------------------
leanprover/lean4:v4.26.0
leanprover/lean4:v4.27.0 (default)
leanprover/lean4:v4.28.0-rc1
leanprover/lean4:v4.29.0-rc2
# ... any combination
```

Each project specifies its own toolchain in `lean-toolchain`:
```
ProjectA/lean-toolchain → leanprover/lean4:v4.26.0
ProjectB/lean-toolchain → leanprover/lean4:v4.28.0-rc1
ProjectC/lean-toolchain → leanprover/lean4:v4.29.0-rc2
```

**The MCP tool cannot assume any specific version.** It must detect dynamically.

### Root Cause

| Command | What It Returns |
|---------|-----------------|
| `lean --version` | **Default/global** toolchain version |
| `lake env lean --version` (in project dir) | **Project-specific** version from `lean-toolchain` |

**Bug**: MCP runs `lean --version` globally instead of checking the active project.

### Evidence (My System)

```powershell
# Global default (what MCP currently reports)
PS> lean --version
Lean (version 4.27.0...)

# Active project (what MCP SHOULD report)
PS> cd D:\mathlib-workspace; lake env lean --version
Lean (version 4.28.0-rc1...)

# Proof via Lean itself
PS> #eval Lean.versionString  -- via lean_mathlib tool
"4.28.0-rc1"
```

### The Fix

The tool must detect version **per-project**, not globally:

```csharp
// ❌ WRONG - Returns user's default toolchain, not project's
var version = RunCommand("lean --version");

// ✅ CORRECT - Option 1: Run in project context
private string GetProjectLeanVersion(string projectPath)
{
    var result = RunCommand("lake env lean --version", workingDir: projectPath);
    return ParseVersion(result);
}

// ✅ CORRECT - Option 2: Parse lean-toolchain file directly (faster)
private string GetProjectLeanVersion(string projectPath)
{
    var toolchainPath = Path.Combine(projectPath, "lean-toolchain");
    if (File.Exists(toolchainPath))
    {
        var content = File.ReadAllText(toolchainPath).Trim();
        // "leanprover/lean4:v4.28.0-rc1" → "4.28.0-rc1"
        return content.Split(':').Last().TrimStart('v');
    }
    // Fallback to global only if no project toolchain
    return GetGlobalLeanVersion();
}
```

### Impact
- **Misleading status**: Users see wrong version, don't know what features are available
- **Capability mismatch**: Advertising features that may/may not exist in user's project
- **Debugging difficulty**: When things fail, version info doesn't help diagnose

---

## Test Results with Concrete Examples

### ✅ STRENGTH 1: File Compilation Checking

```
Action: check_file
Input: D:\Erdos\KSS_Proven.lean (681 lines)
Result: ✅ SUCCESS in 180.0s
```

**Working well**: Reports compilation status, errors, sorries.

---

### ✅ STRENGTH 2: `#print axioms` DOES Work (When You Add It Yourself)

**Test Case**:
```lean
axiom dangerous_axiom : ∀ (P : Prop), P
theorem everything_is_true : 1 = 2 := dangerous_axiom _
#print axioms everything_is_true
```

**Result**: 
```
STATUS: SUCCESS
OUTPUT: 'everything_is_true' depends on axioms: [dangerous_axiom]
```

✅ **This works!** But you must **manually** add `#print axioms`. 
The tool does NOT automatically audit axioms on `check_file`.

---

### ✅ STRENGTH 3: `exact?` Works (via lean_mathlib)

**Test Case** (using `lean_mathlib` tool):
```lean
import Mathlib.Data.Finset.Card
example : (s.filter p).card ≤ s.card := by exact?
```

**Result**:
```
Try this:
  [apply] exact Finset.card_filter_le s p
```

✅ **exact? works perfectly** when you use the right tool!

---

### ✅ FIXED: `library_search` Now Works!

**Test Case**:
```
Action: library_search
Goal: "n + 0 = n"
```

**Result**:
```
✅ Found Proofs!
| Lemma | Suggested Tactic |
|-------|------------------|
| `Nat.add_eq_left.mpr` | `exact Nat.add_eq_left.mpr rfl` |
```

✅ **EXCELLENT!** The parsing bug has been fixed - proofs are now returned correctly!

---

### ❌ WEAKNESS 2: `search_by_type` Returns Nothing Useful

**Test Case**:
```
Action: search_by_type
Type: "Finset α → Finset α → Finset α"
```

**Result**: `❌ Search failed: No matching lemmas found`

**Expected**: Should find `Finset.union`, `Finset.inter`, etc.

---

### ❌ WEAKNESS 3: `search_lemma` Returns `(type not resolved)`

**Test Case**:
```
Action: search_lemma
Pattern: "Finset.card_filter"
```

**Result**:
```
| Lemma | Type |
|-------|------|
| `name` | `(type not resolved)` |
| `acc` | `(type not resolved)` |
```

**Expected**: Should return actual lemma types:
```
| Finset.card_filter_le | card (filter p s) ≤ card s |
```

**Fix needed**: Run `#check` on each matched lemma to get its type.

---

### ⚠️ WEAKNESS 4: Version Detection Shows Global Instead of Project

**The Issue**:
```
LEAN_VERSION: Lean (version X.Y.Z...)  ← This is the GLOBAL default
ACTIVE_PROJECT: D:\some-project       ← But this project may use a DIFFERENT version!
```

**Why It Matters**:
- `elan` allows multiple Lean toolchains to be installed
- Each project's `lean-toolchain` file specifies which version to use
- The MCP tool reports the global default, not the active project's version
- Users cannot trust the version displayed to know what features are available

**Example** (from my system):
```powershell
# MCP reports this (global default)
PS> lean --version
Lean (version 4.27.0...)

# But active project actually uses this
PS> cat D:\mathlib-workspace\lean-toolchain
leanprover/lean4:v4.28.0-rc1
```

**Note**: `first_par` mentioned in capabilities is custom MCP code (tries tactics sequentially), not a built-in Lean tactic. The version display issue makes capability advertising confusing.

---

### ⚠️ WEAKNESS 5: `check_file` Doesn't Report Axiom Dependencies

**Test Case**: Check KSS_Proven.lean (which uses a custom axiom)

**Result**: 
```
✅ All proofs complete - no sorries!
```

**Problem**: No mention that the proof depends on `kss_two_to_one_map_exists` (a custom axiom).
The `goal_at` action accidentally reveals it in the raw output, but `check_file` hides it.

---

### ✅ STRENGTH 4: Lean 4.28 Features DO Work (grind/simp +locals)

**Test Case**:
```lean
def foo : ℕ := 42
example : foo = 42 := by simp +locals
```

**Result**: ✅ SUCCESS

The `+locals` modifier works in the current Mathlib (even on 4.27.0 toolchain).

---

## 🔧 ACTIONABLE FIXES (Priority Order)

### FIX 1: Make `library_search` Actually Call `exact?`

**Current Bug**: Returns "No Direct Proof Found" for everything.

**Fix**: The action should generate and run:
```lean
example : {GOAL} := by exact?
```

Then parse the output `Try this: exact SomeLemma` and return it.

**Test After Fix**:
```
Input: library_search with goal "n + 0 = n"
Expected Output: "exact Nat.add_zero n"
Currently Returns: "No Direct Proof Found"
```

---

### FIX 2: Add `audit_axioms` Action to `check_file`

**Current Bug**: `check_file` says "✅ All proofs complete" but doesn't mention custom axioms.

**Fix**: After compilation succeeds, automatically run:
```lean
#print axioms MainTheorem
```
for each top-level theorem and flag non-standard axioms.

**Implementation**:
```python
STANDARD_AXIOMS = {"propext", "Classical.choice", "Quot.sound", "funext"}
custom_axioms = [a for a in detected_axioms if a not in STANDARD_AXIOMS]
if custom_axioms:
    print(f"⚠️ Custom axioms: {custom_axioms}")
```

---

### FIX 3: Fix Version Detection to Use Project Context (Critical)

**Current Bug**: Status shows global `lean --version` instead of project-specific version.

**Why This Is Critical**:
- Users have different Lean versions installed (`elan` manages multiple toolchains)
- Each project can specify its own version in `lean-toolchain`
- The MCP tool cannot know beforehand which version any user's project uses
- Must detect dynamically at runtime

**Fix**: 
```csharp
// Option 1: Run lake env lean --version in project context
private string GetProjectLeanVersion(string projectPath)
{
    try
    {
        var result = RunCommand("lake env lean --version", workingDir: projectPath);
        return ParseVersion(result); // Extract "X.Y.Z" from output
    }
    catch
    {
        return GetGlobalLeanVersion(); // Fallback
    }
}

// Option 2: Read lean-toolchain file directly (faster, no subprocess)
private string GetProjectLeanVersion(string projectPath)
{
    var toolchainPath = Path.Combine(projectPath, "lean-toolchain");
    if (File.Exists(toolchainPath))
    {
        var content = File.ReadAllText(toolchainPath).Trim();
        // Parse: "leanprover/lean4:v4.28.0-rc1" → "4.28.0-rc1"
        var match = Regex.Match(content, @":v?(\d+\.\d+\.\d+(?:-[\w.]+)?)");
        if (match.Success) return match.Groups[1].Value;
    }
    return GetGlobalLeanVersion();
}

// Then use it in status:
var projectVersion = GetProjectLeanVersion(ActiveProject);
var capabilities = GetCapabilitiesForVersion(projectVersion);
```

**Test After Fix**:
```
ACTIVE_PROJECT: D:\some-project
LEAN_VERSION: Lean (version X.Y.Z)  ← Must match lean-toolchain in project
```

---

### FIX 4: Make `search_lemma` Return Useful Results

**Current Bug**: Returns `| name | (found in environment) |` which is useless.

**Fix**: Run `#check` on matched lemmas to get their types:
```python
for lemma in matches:
    type = run_lean(f"#check {lemma}")
    results.append({"name": lemma, "type": type})
```

**Test After Fix**:
```
Input: search_lemma with pattern "Finset.card_filter"
Expected: | Finset.card_filter_le | card (filter p s) ≤ card s |
```

---

### FIX 5: Support Inline Code in `fill_sorry`

**Current Bug**: Requires file path, can't process inline code.

**Fix**: Create temp file, run, delete:
```python
if code and not path:
    temp_path = create_temp_file(code)
    result = fill_sorry(temp_path)
    delete_temp_file(temp_path)
```

---

## Recommendations Based on Lean 4.28.0-rc1 Features

> ⚠️ **Note**: These require upgrading from Lean 4.27.0 to 4.28.0-rc1

### 1. `first_par` for Parallel Tactic Search (#11949)
```lean
first_par [exact?, apply?, simp_all, grind]
```
Use for `fill_sorry` to try multiple approaches simultaneously.

### 2. `SymM` for Fast Pattern Matching (#11788, #11813)
Use for semantic lemma search - match goal types against library signatures efficiently.

### 3. `lake shake` Built-in (#11921)
Replace custom import optimization with the official command.

### 4. `#import_path` for Dependency Analysis (#11726)
```lean
#import_path SomeLemma  -- shows import chain
assert_not_exists Foo   -- dependency management
```

### 5. `simp +locals` / `grind +locals` (#11946, #11947)
Already works on 4.27.0! Recommend these in tactic suggestions.

---

## Recommendations Based on MCP C# SDK Features

### 1. MCP Tasks for Long Operations (#1170)
```csharp
[McpServerTask]
public async Task<FileCheckResult> CheckFileAsync(string path)
{
    // Can take 180+ seconds - show progress
}
```

### 2. Streaming Progress Updates
```csharp
await Progress.ReportAsync(new()
{
    Message = "Checking KSS_Proven.lean... [████████░░] 80%",
    PercentComplete = 80
});
```

### 3. Sampling for LLM-Assisted Proofs
```csharp
// When exact? fails, ask the LLM
var suggestion = await server.AsSamplingChatClient()
    .GetResponseAsync($"Suggest tactics for: {goal}");
```

### 4. Message Filters for Clean Output (#1207)
```csharp
.AddMcpServer()
.WithMessageFilter(msg => msg.Level >= LogLevel.Warning)
```
Filter verbose Lean warnings, surface only errors and axiom warnings.

---

## Summary: What Works vs What's Broken

| Feature | Status | Notes |
|---------|--------|-------|
| `check_file` | ✅ Works | 180s for 681-line file |
| `audit_sorries` | ✅ Works | Finds sorry statements |
| `goal_at` | ✅ Works | Shows goal + hypotheses |
| `audit_axioms` | ✅ **NEW** | Detects custom vs standard axioms |
| `semantic_search` | ✅ **NEW** | Finds lemmas by goal type |
| `fill_sorry_code` | ✅ **NEW** | Fill sorry in code snippets |
| `suggest_tactics` | ⚠️ Generic | Doesn't suggest exact lemmas |
| `library_search` | ✅ **FIXED** | Returns proofs correctly now! |
| `search_lemma` | ❌ Broken | Returns `(type not resolved)` instead of types |
| `search_by_type` | ❌ Broken | Always fails |
| `fill_sorry` | ⚠️ Limited | Requires file path |
| Version detection | ✅ **FIXED** | Now reads from project's `lean-toolchain` |

---

## Recommended Workflow (Updated)

### For Lemma Search - Use `semantic_search` (NEW!)
```python
# Instead of broken library_search:
mcp_lean_lean(action='semantic_search', paramsJson='{"goal_type":"Finset.card (Finset.filter p s) ≤ Finset.card s"}')
# Returns: Finset.card_filter_le with "exact Finset.card_filter_le"
```

### For Axiom Auditing - Use `audit_axioms` (NEW!)
```python
# Instead of manually adding #print axioms:
mcp_lean_lean(action='audit_axioms', paramsJson='{"path":"file.lean","theorem":"my_theorem"}')
# Returns: List of custom vs standard axioms
```

### For Code Snippets - Use `fill_sorry_code` (NEW!)
```python
# Instead of creating a temp file:
mcp_lean_lean(action='fill_sorry_code', paramsJson='{"code":"example (n : ℕ) : n + 0 = n := sorry"}')
# Returns: Fixed code with "rfl"
```

### Fallback: Use `lean_mathlib` Directly
If the above don't work, use `lean_mathlib` with `action='run'`:

```python
lean_mathlib(action='run', code='''
import Mathlib
example : (s.filter p).card ≤ s.card := by exact?
''')
# Returns: "exact Finset.card_filter_le s p"
```

---

## Conclusion

The MCP Lean tool has **improved significantly** with three new features:

| Priority | Issue | Status |
|----------|-------|--------|
| 🟢 Fixed | Axiom detection | ✅ `audit_axioms` works |
| 🟢 Fixed | Goal-type lemma search | ✅ `semantic_search` works |
| 🟢 Fixed | Inline code sorry filling | ✅ `fill_sorry_code` works |
| 🟢 Fixed | `library_search` parsing | ✅ Now returns proofs correctly |
| 🔴 P0 | `search_lemma` returns garbage | ❌ Still broken |
| � Fixed | Version detection | ✅ Now reads project's `lean-toolchain` |

**Updated Rating: 9/10** (Up from 5.5)

Both `library_search` and `semantic_search` now work for finding lemmas! Use `audit_axioms` to verify proof soundness. Version detection correctly identifies project-specific Lean versions.

---

*Report generated by Claude (GitHub Copilot) during Erdős Problem 530 formalization project*  
*Updated: February 5, 2026 - New features tested and working*
