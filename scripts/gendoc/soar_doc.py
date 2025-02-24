from pathlib import Path
from typing import Any

import yaml


class DocumentationGenerator:
    """
    Generates documentation in markdown format for all classes within a specified package.

    This class automates the generation of markdown files for class documentation, organizing them
    into categories based on their module structure. It also updates the mkdocs configuration to
    include these generated documents in the site navigation.

    Attributes
    ----------
    package_mapper : Any
        An instance of a class (ideally `PackageMapper`) that provides `modules_info` containing
        information about the package's modules and classes.
    base_directory : Path
        The base directory where the documentation markdown files will be generated.
    markdown_files_list : List[Path]
        A list of Paths to the generated markdown files.
    categories : Dict[str, List[Path]]
        A dictionary categorizing the generated markdown files by their module structure.

    Parameters
    ----------
    package_mapper : Any
        The package mapper instance used to retrieve modules and classes information.
    base_directory : str, optional
        The base path where the documentation files will be generated, by default 'reference/'.

    """

    def __init__(self, package_mapper: Any, base_directory: str = "reference/"):
        """
        Initializes the DocumentationGenerator with a package mapper and a base directory.
        """
        self.package_mapper = package_mapper
        self.base_directory: Path = Path(base_directory).resolve()
        self.markdown_files_list: list[Path] = []
        self.categories: dict[str, list[Path]] = {}

    def generate(self) -> None:
        """
        Generates the markdown documentation for all classes in the specified package.

        This method iterates over the modules and classes provided by the `package_mapper`,
        generating markdown files for each class. It then generates an index file and updates
        the mkdocs configuration to include the generated documentation.
        """
        try:
            self.base_directory.mkdir(parents=True, exist_ok=True)
            for module_info in self.package_mapper.modules_info:
                modname = module_info["modname"]
                self._process_module(modname, module_info["classes"])
            self._generate_index_file()
            self._update_mkdocs_config()
        except Exception as e:
            print(f"Erro ao gerar documentação: {e}")

    def _process_module(self, modname: str, classes: list[str]) -> None:
        """
        Processes each module, creating a folder structure and generating markdown for each class.

        Parameters
        ----------
        modname : str
            The full name of the module.
        classes : List[str]
            A list of class names within the module.
        """
        module_folder = self.base_directory / modname.replace(
            self.package_mapper.package_name + ".", ""
        ).replace(".", "/")
        module_folder.mkdir(parents=True, exist_ok=True)
        for class_name in classes:
            self._generate_class_markdown(modname, class_name, module_folder)

    def _generate_class_markdown(self, modname: str, class_name: str, module_folder: Path) -> None:
        """
        Generates a markdown file for a single class.

        Parameters
        ----------
        modname : str
            The full name of the module containing the class.
        class_name : str
            The name of the class to document.
        module_folder : Path
            The folder where the markdown file should be created.
        """
        markdown_file = module_folder / f"{class_name}.md"
        with markdown_file.open("w") as md_file:
            md_file.write(f"# Class `{class_name}`\n\n")
            md_file.write(
                f"Here's the reference information for the `{class_name}` class, with all its parameters, attributes, and methods.\n\n"
            )
            md_file.write(f"You can import the `{class_name}` class directly from `{modname}`:\n\n")
            md_file.write(f"## Usage\n\n```python\nfrom {modname} import {class_name}\n```\n\n")
            md_file.write(f"::: {modname}.{class_name}")
        self.markdown_files_list.append(markdown_file)
        self._categorize_file(markdown_file)

    def _categorize_file(self, markdown_file: Path) -> None:
        """
        Categorizes the generated markdown file based on its module structure.

        Parameters
        ----------
        markdown_file : Path
            The path to the generated markdown file.
        """
        relative_path = markdown_file.relative_to(self.base_directory)
        main_category, subcategory = self._extract_categories(relative_path)
        category_key = main_category if not subcategory else f"{main_category} / {subcategory}"
        if category_key not in self.categories:
            self.categories[category_key] = []
        self.categories[category_key].append(markdown_file)

    def _extract_categories(self, relative_path: Path) -> tuple[str, str]:
        """
        Extracts main and subcategories from the relative path of a markdown file.

        Parameters
        ----------
        relative_path : Path
            The relative path of the markdown file from the base directory.

        Returns
        -------
        Tuple[str, str]
            A tuple containing the main category and subcategory.
        """
        path_components = relative_path.parts
        main_category = path_components[0]
        subcategory = "/".join(path_components[1:-1]) if len(path_components) > 2 else ""
        return main_category, subcategory

    def _generate_index_file(self) -> None:
        """
        Generates an index markdown file that lists all generated documentation files.
        """
        index_file = self.base_directory / "index.md"
        with index_file.open("w") as file:
            file.write("# Index of Documentation\n\n")
            for category, files in self.categories.items():
                file.write(f"## {category.replace('_', ' ').title()}\n\n")
                for markdown_file in files:
                    title = markdown_file.stem.replace("_", " ").title()
                    relative_path = str(markdown_file.relative_to(self.base_directory)).replace(
                        "\\", "/"
                    )
                    file.write(f"- [{title}]({relative_path})\n")

    def _update_mkdocs_config(self) -> None:
        """
        Updates the mkdocs configuration file to include the generated documentation.
        """
        mkdocs_config_path = self.base_directory.parent / "../../mkdocs.yml"
        try:
            with mkdocs_config_path.open("r") as file:
                mkdocs_config = yaml.safe_load(file)
            nav = mkdocs_config.get("nav", [])
            reference_section = {"Reference (Code API)": self._generate_nav_structure()}
            nav.append(reference_section)
            print(self._generate_nav_structure())
            mkdocs_config["nav"] = nav
            with mkdocs_config_path.open("w") as file:
                yaml.safe_dump(mkdocs_config, file, sort_keys=False)
        except FileNotFoundError:
            print(f"mkdocs.yml not found in {mkdocs_config_path.parent}")
        except Exception as e:
            print(f"Error updating mkdocs.yml: {e}")

    def _generate_nav_structure(self) -> list[dict[str, list[dict[str, str]]]]:
        """
        Generates a navigation structure for mkdocs based on the categorized documentation files.

        Returns
        -------
        List[Dict[str, List[Dict[str, str]]]]
            A list of dictionaries representing the navigation structure for mkdocs.
        """
        nav_structure = []
        for category, files in self.categories.items():
            category_dict = {category: []}
            for markdown_file in files:
                title = markdown_file.stem.replace("_", " ").title()
                relative_path = markdown_file.relative_to(self.base_directory)
                category_dict[category].append({title: str(relative_path)})
            nav_structure.append(category_dict)
        return nav_structure
