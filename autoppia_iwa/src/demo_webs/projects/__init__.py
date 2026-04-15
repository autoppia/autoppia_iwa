"""Project package compatibility helpers.

This module keeps backward-compatible import paths for legacy project package
names (e.g. ``autobooks_2``) after the migration to ``pNN_*`` directories.
"""

from importlib import import_module
import sys


_LEGACY_TO_NEW = {
    "autocinema_1": "p01_autocinema",
    "autobooks_2": "p02_autobooks",
    "autozone_3": "p03_autozone",
    "autodining_4": "p04_autodining",
    "autocrm_5": "p05_autocrm",
    "automail_6": "p06_automail",
    "autodelivery_7": "p07_autodelivery",
    "autolodge_8": "p08_autolodge",
    "autoconnect_9": "p09_autoconnect",
    "autowork_10": "p10_autowork",
    "autocalendar_11": "p11_autocalendar",
    "autolist_12": "p12_autolist",
    "autodrive_13": "p13_autodrive",
    "autohealth_14": "p14_autohealth",
    "autostats_15": "p15_autostats",
    "autodiscord_16": "p16_autodiscord",
}


_COMMON_SUBMODULES = (
    "data",
    "data_utils",
    "dataExtractionUseCases",
    "events",
    "generation_functions",
    "main",
    "replace_functions",
    "use_cases",
    "utils",
)


def _register_legacy_import_aliases() -> None:
    base = __name__
    for legacy_name, new_name in _LEGACY_TO_NEW.items():
        legacy_package = f"{base}.{legacy_name}"
        new_package = f"{base}.{new_name}"

        try:
            new_package_module = import_module(new_package)
        except Exception:
            continue

        sys.modules.setdefault(legacy_package, new_package_module)

        for submodule in _COMMON_SUBMODULES:
            new_submodule_name = f"{new_package}.{submodule}"
            legacy_submodule_name = f"{legacy_package}.{submodule}"
            try:
                new_submodule = import_module(new_submodule_name)
            except Exception:
                continue
            sys.modules.setdefault(legacy_submodule_name, new_submodule)


_register_legacy_import_aliases()
