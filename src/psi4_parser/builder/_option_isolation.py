"""Emit a self-contained native option scope for checked calculations."""

from psi4_parser.builder._encoding import GENERATED_PREFIX

ISOLATION_SOURCE = """import contextlib as __PREFIX__contextlib
import psi4 as __PREFIX__psi4

@__PREFIX__contextlib.contextmanager
def __PREFIX__isolated_options(modules):
    core = __PREFIX__psi4.core
    options = core.get_options()
    previous_module = options.get_current_module()
    previous_namespace = core.IO.get_default_namespace()
    try:
        state = __PREFIX__psi4.driver.p4util.prepare_options_for_modules(
            changedOnly=False, stateInsteadMediated=True
        )
        state['GLOBALS'] = {
            name: {
                'value': core.get_global_option(name),
                'has_changed': core.has_global_option_changed(name),
            }
            for name in core.get_global_option_list()
        }
        # These native modules supplement the public utility's module list.
        for module in dict.fromkeys(('ADC', 'DDX', 'F12', previous_module, *modules)):
            if not module or module in state:
                continue
            state[module] = {
                name: {
                    'value': core.get_local_option(module, name),
                    'has_changed': flags[0],
                }
                for name, flags in core.options_to_python(module).items()
            }
        if any(
            item['value'] is None
            for values in state.values()
            for item in values.values()
        ):
            raise ValueError('Cannot isolate opaque Psi4 option values')
        try:
            core.clean_options()
            core.get_options().set_current_module(previous_module)
            yield
        finally:
            core.clean_options()
            for module, values in state.items():
                for name, item in values.items():
                    if module == 'GLOBALS':
                        current = core.get_global_option(name)
                        if item['value'] != current or item['has_changed']:
                            core.set_global_option(name, item['value'])
                        if not item['has_changed']:
                            core.revoke_global_option_changed(name)
                    else:
                        current = core.get_local_option(module, name)
                        if item['value'] != current or item['has_changed']:
                            core.set_local_option(module, name, item['value'])
                        if not item['has_changed']:
                            core.revoke_local_option_changed(module, name)
    finally:
        try:
            core.get_options().set_current_module(previous_module)
        finally:
            core.IO.set_default_namespace(previous_namespace)
""".replace("__PREFIX__", GENERATED_PREFIX)
"""Restore native options, module selection, and the call's entry namespace.

The scope uses the engine's public option APIs and supplements its public module
catalogue with ADC, DDX, and F12 from the reviewed native read_options.cc. It
preserves raw values as well as changed flags and skips reassigning clean default
values that native setters may reject. Native molecule declarations may select a
namespace before this scope starts. It contains no calculation or result API.
"""
