# Build, Portability, and Data-Access Review Rules
## ASDF system definitions
## CL-101 — One primary system definition per .asd file, though subsidiary systems (e.g., test systems) may also be defined in the same file.
**Rule ID:** CL-101  
**Name:** One primary system definition per .asd file, though subsidiary systems (e.g., test systems) may also be defined in the same file.  
**Signal:** A primary `defsystem` differs from its lowercase, same-named `.asd` file, or the file contains application code.
**Problem:** Discovery and loading become surprising; build metadata gains runtime side effects.
**Exception:** A small reader setup required by ASDF is acceptable.
**Example:**
```lisp
(asdf:defsystem "myapp" :depends-on ("alexandria"))
```
## CL-102 — State component edges
**Rule ID:** CL-102  
**Name:** Explicit component dependencies  
**Signal:** `:serial t` appears where components have a non-linear dependency graph.
**Problem:** Serial loading conceals real edges and needlessly couples unrelated files.
**Exception:** A strictly layered sequence in which each file needs all predecessors is suitable.
**Example:**
```lisp
(:module "src" :components ((:file "package") (:file "core" :depends-on ("package"))))
```
## CL-103 — Isolate tests in a test system
**Rule ID:** CL-103  
**Name:** Separate test system  
**Signal:** The library's main `:depends-on` lists a test framework or test files.
**Problem:** Consumers acquire unnecessary test dependencies at runtime. Use a separate test system defined in the same `.asd` file or a separate `.asd` file; the test system should not be a dependency of the main system.
**Exception:** An executable explicitly intended as a test harness may depend on its framework.
**Example:**
```lisp
(asdf:defsystem "myapp/test" :depends-on ("myapp" "fiveam"))
```
## CL-104 — Delegate test-op
**Rule ID:** CL-104  
**Name:** `:in-order-to` for test-op  
**Signal:** The primary system embeds test-running forms rather than delegating `test-op`.
**Problem:** Test behavior becomes entangled with library loading and ASDF operation dispatch.
**Exception:** A deliberately single-system program with no separable test dependency is rare but possible.
**Example:**
```lisp
:in-order-to ((test-op (test-op "myapp/test")))
```
## CL-105 — Restrict defsystem-time dependencies
**Rule ID:** CL-105  
**Name:** `:defsystem-depends-on` for ASDF extensions only  
**Signal:** A normal library appears in `:defsystem-depends-on`.
**Problem:** It loads while ASDF reads metadata instead of when the application needs it.
**Exception:** A system defining a custom ASDF component class belongs there.
**Example:**
```lisp
:defsystem-depends-on ("asdf-system-connections")
```
## CL-106 — Keep ASDF files declarative
**Rule ID:** CL-106  
**Name:** Minimal code in `.asd` files  
**Signal:** An `.asd` file defines functions, performs I/O, or implements substantial control flow.
**Problem:** Loading system metadata can execute opaque, implementation-dependent work.
**Exception:** Brief declarations supporting ASDF extension setup can be justified.
**Example:**
```lisp
(asdf:defsystem "myapp" :components ((:file "src/package") (:file "src/main")))
```
## Dependency management
## CL-107 — Declare every required system
**Rule ID:** CL-107  
**Name:** Declare all dependencies  
**Signal:** A used external package or `require`d system is absent from `:depends-on`.
**Problem:** Success depends on accidental contents of the caller's Lisp image.
**Exception:** ANSI packages need no declaration; optional integrations may be conditionally loaded.
**Example:**
```lisp
(asdf:defsystem "myapp" :depends-on ("alexandria" "uiop"))
```
## CL-108 — Constrain versions sparingly
**Rule ID:** CL-108  
**Name:** Version constraints  
**Signal:** Exact pins or undocumented version bounds appear in system dependencies.
**Problem:** Unneeded bounds reduce compatible installations and complicate resolution.
**Exception:** A minimum release that introduced a relied-on API should be stated.
**Example:**
```lisp
:depends-on ((:version "alexandria" "1.4"))
```
## CL-109 — Distinguish distribution from declaration
**Rule ID:** CL-109  
**Name:** Quicklisp is not dependency declaration  
**Signal:** Documentation treats Quicklisp membership as a substitute for `:depends-on`.
**Problem:** Distribution snapshots do not declare requirements or guarantee reproducible versions.
**Exception:** Project setup documentation may name Quicklisp alongside declared ASDF dependencies.
**Example:**
```lisp
:depends-on ("babel")
```
## CL-110 — Use stable lowercase names
**Rule ID:** CL-110  
**Name:** Lowercase system names  
Keep system names lowercase and hyphenated. Package names should also be lowercase but are separate from system names — a system named `myapp` may contain a package named `myapp.core`.
**Signal:** Public system names contain uppercase letters or underscores, or package designators conflate packages with their containing system names.
**Problem:** Inconsistent naming harms portability, convention, and discoverability.
**Exception:** Interoperating with a pre-existing externally named system can require its name.
**Example:**
```lisp
(asdf:defsystem "my-app" :components ((:file "package")))
```
## Portability
## CL-111 — Fence implementation extensions
**Rule ID:** CL-111  
**Name:** Write against ANSI  
**Signal:** `sb-ext:`, `ccl:`, or similar symbols occur in ordinary application files.
**Problem:** Extension use spreads implementation coupling throughout the codebase.
**Exception:** A narrow, documented portability module may encapsulate an extension.
**Example:**
```lisp
(defun platform-argv () #+sbcl sb-ext:*posix-argv* #-sbcl nil)
```
## CL-112 — Centralize reader conditionals
**Rule ID:** CL-112  
**Name:** Minimize reader conditionals  
**Signal:** `#+` or `#-` is scattered across routine business logic.
**Problem:** Compile-time branches make behavior and feature coverage difficult to inspect.
**Exception:** An unavoidable OS or implementation difference may need a localized conditional.
**Example:**
```lisp
(uiop:hostname)
```
## CL-113 — Do not guess feature keywords
**Rule ID:** CL-113  
**Name:** Don't assume feature spellings  
**Signal:** Code hardcodes feature names for threads, Unicode, or numeric capabilities.
**Problem:** Implementations advertise equivalent capabilities with different feature conventions.
**Exception:** A project-owned portability layer may define and document a normalized feature.
**Example:**
```lisp
;; Avoid: hardcoded feature test scattered in code
#+sb-thread (make-thread ...)
;; Good: centralized detection in a portability layer
(in-package :myapp.portability)
(defparameter *supports-threads* (or #+sb-thread t #+ccl t))
;; In application code:
(when *supports-threads* (make-thread ...))
```
## CL-114 — Avoid implicit implementation assumptions
**Rule ID:** CL-114  
**Name:** Don't assume implementation behavior  
**Signal:** Code relies on reader case, encoding, pathname syntax, threads, or compiler quirks silently.
**Problem:** Such defaults vary across conforming implementations and environments.
**Exception:** An implementation-specific tool may rely on them when it says so explicitly.
**Example:**
```lisp
(with-standard-io-syntax (read-from-string text))
```
## CL-115 — Exercise portability claims
**Rule ID:** CL-115  
**Name:** Test on multiple implementations  
**Signal:** A purportedly portable library documents or tests only one Lisp implementation.
**Problem:** Undetected extensions and unspecified assumptions become user-facing failures.
**Exception:** A single-implementation library is valid when its limitation is recorded.
**Example:**
```lisp
;; CI coverage should include SBCL and CCL.
```

## Streams and pathnames
## CL-116 — Close streams reliably
**Rule ID:** CL-116  
**Name:** Always use `with-open-file`  
**Signal:** `open` lacks a matching `close` protected by `unwind-protect`.
**Problem:** Non-local exits can leak descriptors and leave buffered output unfinished.
**Exception:** A caller-owned stream intentionally returned from an API must document ownership.
**Example:**
```lisp
(with-open-file (in path :direction :input) (read-line in))
```
## CL-117 — Specify the I/O model
**Rule ID:** CL-117  
**Name:** Choose element type deliberately  
**Signal:** Binary data uses character defaults, or encoding-dependent text omits needed options.
**Problem:** Stream contents can be decoded, encoded, or represented incorrectly.
**Exception:** A documented implementation default may suffice for private, controlled input.
**Example:**
```lisp
(with-open-file (out file :direction :output :element-type '(unsigned-byte 8)))
```
## CL-118 — Keep paths as pathnames
**Rule ID:** CL-118  
**Name:** Use pathname objects internally  
**Signal:** Library code concatenates namestrings or embeds directory separators.
**Problem:** String path assembly fails on differing filesystem and pathname conventions.
**Exception:** Convert with `namestring` at an OS-command or user-interface boundary.
**Example:**
```lisp
(merge-pathnames "config.lisp" directory)
```
## CL-119 — Resolve paths at runtime
**Rule ID:** CL-119  
**Name:** Avoid absolute pathnames  
**Signal:** Source embeds host-specific absolute paths or assumes portable parsing of `#p` text.
**Problem:** The system cannot relocate and pathname syntax is implementation-sensitive.
**Exception:** A deployment configuration may supply an absolute path outside source code.
**Example:**
```lisp
(merge-pathnames #p"data/" (uiop:getcwd))
```
## CL-120 — Reuse UIOP pathname operations
**Rule ID:** CL-120  
**Name:** Prefer UIOP pathname utilities  
**Signal:** Project/build code reimplements merging, subpath, or directory enumeration logic.
**Problem:** Handwritten filesystem handling often misses cross-implementation cases.
**Exception:** A specialized operation absent from UIOP may be implemented and tested locally.
**Example:**
```lisp
(uiop:directory-files (uiop:subpathname root "assets/"))
```

## Hash tables
## CL-121 — Match the test to keys
**Rule ID:** CL-121  
**Name:** Choose `:test` by key type  
**Signal:** `equalp` is a default choice without an identity or equivalence rationale.
**Problem:** Overbroad equality changes lookup semantics and can add unnecessary cost.
**Exception:** Case- and representation-insensitive keys legitimately require `equalp`.
**Example:**
```lisp
(make-hash-table :test #'equal) ; structural string or cons keys
```
## CL-122 — Specify public key equivalence
**Rule ID:** CL-122  
**Name:** Document key semantics  
**Signal:** A public API exposes a table without saying how its keys compare.
**Problem:** Callers cannot predict whether distinct-looking keys retrieve the same entry.
**Exception:** A private table with obvious local symbol keys needs no public contract.
**Example:**
```lisp
;; Keys are case-insensitive strings, compared with EQUALP.
(make-hash-table :test #'equalp)
```
## CL-123 — Inspect `gethash` presence
**Rule ID:** CL-123  
**Name:** Use second value of `gethash`  
**Signal:** A lookup treats one `gethash` value as absence when stored values may be `nil`.
**Problem:** A present `nil` becomes indistinguishable from a missing key.
**Exception:** Ignoring presence is fine when `nil` is prohibited or equivalent to absent by contract.
**Example:**
```lisp
(multiple-value-bind (value presentp) (gethash key table) (values value presentp))
```
## CL-124 — Size tables from evidence
**Rule ID:** CL-124  
**Name:** Supply `:size` when known  
**Signal:** Known-cardinality tables omit `:size`, or rehash options are tuned without measurement.
**Problem:** Avoidable growth costs or fragile implementation-specific tuning can result.
**Exception:** Unknown or tiny tables need no estimate; profiling may justify tuning hints.
**Example:**
```lisp
(make-hash-table :test #'eq :size expected-symbol-count)
```
