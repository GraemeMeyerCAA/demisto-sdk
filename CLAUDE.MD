The demisto sdk for Palo Alto's XSOAR system is not really supported properly on Windows. They tell you to either use Docker or WSL2 to run it, but that is incredibly janky, and their instructions are somewhere between terrible and non-existent.

When using the demisto-sdk on Windows, typically you will either open the sdk folder in a devcontainer, or you have to run a precompiled Docker container and pipe in the commands you want (tricky and unreliable for various reasons).

When using either method, the dev container or the docker container will then launch _another_ container to run/debug each integration/pack/script you want to run.

The VS Code extension for XSOAR is also recommended, but is _extremely_ specific about the environment it needs to work, and will fail usually silently to do anything if you don't have the environment configured _exactly_ the way they want it. For example, it will not run if the top level workspace folder is not called "content", and will generally not run if the subfolder structure doesn't match `content/Packs/$PackName/(Intergations|Scripts|Playbooks)/$IntegrationName/$IntegrationName.py`. 

The SDK will also fail or auto-abort if you don't have Git configured and initialised, and you must have a remote configured, and if the remote is the official demisto-sdk or content repo it will do some things, and if it isn't it will require some other things or it will fail.

The SDK / vs code extension do appear to support Python virtual environments, and sometimes even recommends them.

Our job is to determine exactly why the demisto-sdk doesn't run natively on Windows, and how it might be fixed. 