# Bootstrap CLI/runtime Wiring Architecture

> **Status:** Accepted --- Terminally Closed
> **Target:** OpenProjectLab v1.2.7
> **Production CLI Wiring:** Not Started

``` text
generator.cli.main:main
    ↓ canonical build_parser
Existing bootstrap grammar + explicit experimental opt-in
    ├─ no opt-in → existing _handle_bootstrap path
    └─ opt-in → Bootstrap CLI/runtime adapter
                   ↓ immutable request + injected dependencies
               BootstrapRuntimeCoordinator.execute(request)
                   ↓
               existing CLI result / exit-code renderer
```

## Invariants

``` text
Canonical Entry Point --- generator.cli.main:main
Legacy Grammar --- Preserved
No Opt-in --- No Runtime Wiring Behavior Change
Runtime Selection --- Explicit
Coordinator Invocation --- Exactly Once
Dependency Construction --- Explicit / Fail Closed
Preview Mutation --- Forbidden
Validation Repair / Rollback --- Forbidden
generator.main Registration --- Forbidden
Public SDK Expansion --- Forbidden
```

The adapter translates and renders only. Planning, preview, apply, validation,
failure evidence, and ordering remain owned by the accepted core runtimes.


<!-- v1.2.7-bootstrap-cli-runtime-wiring-terminal-architecture -->

## Minimum Implementation Status

``` text
Canonical Entry Point --- generator.cli.main:main
Implementation PR #249 --- Merged
Implementation merge --- ea8dcb3df06679ad2cea84eab228db0c97373b4f
Post-merge focused verification --- 16 passed
Legacy no-opt-in path --- Preserved
Experimental runtime adapter --- Implemented / Fail Closed
Coordinator invocation --- Exactly Once
generator.main registration --- Forbidden / Unchanged
Stable option spelling / Public SDK --- Deferred
```
