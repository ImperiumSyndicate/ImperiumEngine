import importlib
import inspect
import pkgutil
from typing import Any


class PackageMapper:
    """
    A class for mapping out all submodules and packages within a specified package.

    This class is designed to explore a given Python package, identifying all submodules
    and classes within those submodules. It can also generate import statements for each
    class found, facilitating easier import of classes from large and complex packages.

    Parameters
    ----------
    package_name : str
        The name of the package to map.

    Attributes
    ----------
    package_name : str
        Stores the name of the package.
    modules_info : List[Dict[str, Any]]
        A list that holds information about each module and its classes.
        Each entry in the list is a dictionary with 'modname' (module name)
        and 'classes' (a list of class names found within the module).

    """

    def __init__(self, package_name: str):
        """
        Initializes the PackageMapper with the specified package name.

        Parameters
        ----------
        package_name : str
            The name of the package to map.
        """
        self.package_name: str = package_name
        self.modules_info: list[dict[str, Any]] = []

    def map_package(self) -> None:
        """
        Maps all submodules and packages within the specified package.

        This method attempts to import the package specified by `package_name`.
        If successful, it traverses through all submodules and packages, gathering
        information about classes defined in each module. This information is
        stored in `modules_info`.
        """
        try:
            package = importlib.import_module(self.package_name)
            if hasattr(package, "__path__"):
                for importer, modname, ispkg in pkgutil.walk_packages(
                    package.__path__, package.__name__ + "."
                ):
                    module = importlib.import_module(modname)
                    classes = self.get_classes_from_module(module)
                    self.modules_info.append({"modname": modname, "classes": classes})
        except ModuleNotFoundError:
            print(f"Package {self.package_name} not found.")

    def get_classes_from_module(self, module) -> list[str]:
        """
        Returns a list of class names defined in the module.

        This method inspects a given module, identifying all classes that are
        defined within it. Only classes that are defined in the module itself
        (not imported from elsewhere) are included.

        Parameters
        ----------
        module : ModuleType
            The module to inspect.

        Returns
        -------
        List[str]
            A list of class names defined in the module.
        """
        return [
            name
            for name, obj in inspect.getmembers(module, inspect.isclass)
            if obj.__module__ == module.__name__
        ]

    def get_import_statements(self) -> list[str]:
        """
        Generates a list of import statements for classes in modules.

        This method processes the information stored in `modules_info` to generate
        Python import statements for each class. These statements can be used to
        directly import the classes without manually specifying the full module path.

        Returns
        -------
        List[str]
            A list of import statements for the classes.
        """
        imports = [
            f"from {mod['modname']} import {cls}"
            for mod in self.modules_info
            for cls in mod["classes"]
        ]
        return imports

    def print_import_statements(self) -> None:
        """
        Prints the import statements for the mapped classes.

        Utilizes `get_import_statements` to generate and print import statements
        for all classes identified within the package. This is useful for quickly
        generating the required imports for a large package.
        """
        for imp in self.get_import_statements():
            print(imp)
