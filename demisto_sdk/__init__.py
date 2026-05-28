import os

if os.environ.get("DEMISTO_SDK_SKIP_LOGGER_SETUP", "False").lower() not in [
    "true",
    "yes",
    "1",
]:
    from demisto_sdk.commands.common.logger import logging_setup

    logging_setup(initial=True, calling_function="__init__")


# Windows fix: demisto-py's configure() builds the SaaS host with
# os.path.join(host, 'xsoar'), which produces a backslash on Windows and
# breaks every authenticated request. Normalise the host after configure().
# Upstream: https://github.com/demisto/demisto-py — needs os.path.join
# replaced with string concatenation in configure().
import demisto_client as _demisto_client

_original_configure = _demisto_client.configure


def _windows_safe_configure(*args, **kwargs):
    client = _original_configure(*args, **kwargs)
    configuration = getattr(getattr(client, "api_client", None), "configuration", None)
    if configuration is not None and isinstance(configuration.host, str):
        configuration.host = configuration.host.replace("\\", "/")
    return client


_demisto_client.configure = _windows_safe_configure
