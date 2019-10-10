import inspect
import logging
import pkgutil
import importlib
from pathlib import Path
from typing import List, Any

import pluggy

import photon.demo_util.plugins.transforms as plugins_pkg
from photon.demo_util.common.context_base import ContextBase

transform_spec = pluggy.HookspecMarker("transform")
transform_impl = pluggy.HookimplMarker("transform")


class TransformsDemo:
    """
    Pluggy host for image transformations.

    NOTE: this class finds plugins from our plugins directory, registers them,
    and provides a method for invoking them. Plugins are useful models for forking
    execution paths that might otherwise be handled in lengthy "if/else" statements
    or for sequential execution of multiple operations.

    Our "transforms" example is quite simple - for every image, all tranforms are
    applied and with the same parameters. This could use extend to more complex
    scenarios. Perhaps only certain images should undergo certain transform - that
    conditional logic would be the responsibility of the plugin. Maybe some transforms
    would have conditional input based on the image - those computations would also
    be handled by the plugin.Right now, all our transforms are done with ImageMagick
    via Wand, yet we could imagine some plugins using other libraries as well.

    Essentially, plugins allow us to easily (and literally) drop in new features to
    our code base and help us build composable applications.

    """

    def __init__(self, ctx: ContextBase) -> None:
        """
        Args:
            ctx: The Context object.
        """
        logname = Path(__file__).stem
        self._logger = logging.getLogger(f"{ctx.PACKAGE_NAME}.{logname}")
        self._logger.debug("")
        self._pluggy_mgr = pluggy.PluginManager("transform")
        self._pluggy_mgr.add_hookspecs(TransformSpec)
        self._load_plugins()

    def _load_plugins(self) -> None:
        plugin_modules = [
            importlib.import_module(name)
            for finder, name, ispkg in pkgutil.iter_modules(
                plugins_pkg.__path__,  # type: ignore
                plugins_pkg.__name__ + ".",
            )
        ]

        all_classesd = {}
        for plugin_module in plugin_modules:
            plugin_classesd = {
                name: klass
                for name, klass in inspect.getmembers(plugin_module, inspect.isclass)
                if name.startswith("Transform") and name != "TransformsDemo"
            }

            all_classesd.update(plugin_classesd)

        plugin_classes = [
            klass for name, klass in sorted(all_classesd.items(), reverse=True)
        ]

        for plugin_class in plugin_classes:  # plugins fire in alpha order
            self._pluggy_mgr.register(plugin_class())

    def run_transforms(self, filename: str, **kwargs: Any) -> List[str]:
        """
        Run image transforms.

        Returns:
            List of completed transforms.
        """

        transforms = self._pluggy_mgr.hook.run_transform(filename=filename)

        return transforms  # type: ignore


class TransformSpec:  # needs to come after TransformsDemo
    """
    Pluggy hookspec for an image transform.

    """

    @transform_spec  # type: ignore
    def run_transform(self, filename: str) -> str:
        pass
