The demisto sdk for Palo Alto's XSOAR system is not really supported properly on Windows. They tell you to either use Docker or WSL2 to run it, but that is incredibly janky, and their instructions are somewhere between terrible and non-existent.

When using the demisto-sdk on Windows, typically you will either open the sdk folder in a devcontainer, or you have to run a precompiled Docker container and pipe in the commands you want (tricky and unreliable for various reasons).

When using either method, the dev container or the docker container will then launch _another_ container to run/debug each integration/pack/script you want to run.

The VS Code extension for XSOAR is also recommended, but is _extremely_ specific about the environment it needs to work, and will fail usually silently to do anything if you don't have the environment configured _exactly_ the way they want it. For example, it will not run if the top level workspace folder is not called "content", and will generally not run if the subfolder structure doesn't match `content/Packs/$PackName/(Intergations|Scripts|Playbooks)/$IntegrationName/$IntegrationName.py`. 

The SDK will also fail or auto-abort if you don't have Git configured and initialised, and you must have a remote configured, and if the remote is the official demisto-sdk or content repo it will do some things, and if it isn't it will require some other things or it will fail.

The SDK / vs code extension do appear to support Python virtual environments, and sometimes even recommends them.

Our job is to determine exactly why the demisto-sdk doesn't run natively on Windows, and how it might be fixed.

## Expected test failures

When running the test suite, the following failures are **expected and not Windows-specific** — they reproduce identically on a clean Ubuntu install with the same Neo4j setup. Do not treat them as Windows regressions.

- **All `GR_validators_test.py` failures with `apoc.export.graphml.all` in the traceback.** Confirmed identical on Ubuntu (see `ubuntu-test-suite-output.txt`). Root cause: APOC's file-export procedure is disabled by default in Neo4j. To run these green, add to `neo4j.conf` on whichever platform:
  ```
  apoc.export.file.enabled=true
  dbms.security.procedures.unrestricted=apoc.*
  ```
  and restart Neo4j. This is a Neo4j/APOC configuration issue, not a code issue.

- **Docker-coupled commands (`lint`, `pre-commit`, `test-content`) tests.** Out of scope for the Windows port — these require Docker + a Linux container to execute integration code. They are expected to fail or skip on Windows without a working Docker daemon.

See `WINDOWS_STATUS.md` for the full port summary.
