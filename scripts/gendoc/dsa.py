from collections import defaultdict
from pathlib import Path

from mkdocs_manager_soar import MkdocsManagerSoar
from pkg_map import PackageMapper
from soar_doc import DocumentationGenerator


class SoarDocumentationBuilder:
    """
    Classe responsável por automatizar a geração de documentação para um pacote Python
    e atualizar a configuração do MkDocs com a nova documentação gerada.

    Parameters
    ----------
    package_name : str
        Nome do pacote Python que será documentado.
    base_directory : str
        O diretório base onde os arquivos Markdown gerados serão salvos.
    mkdocs_file_path : str
        Caminho para o arquivo de configuração do MkDocs.
    template_path : str
        Caminho para o template do MkDocs (opcional).

    Attributes
    ----------
    base_directory_abs : Path
        Caminho absoluto para o diretório base dos arquivos Markdown.
    mkdocs_file_path_abs : Path
        Caminho absoluto para o arquivo de configuração do MkDocs.
    template_path_abs : Path
        Caminho absoluto para o template do MkDocs.

    Methods
    -------
    run():
        Executa o processo completo de geração e atualização da documentação.
    _build_documentation_structure(documentation_generator: DocumentationGenerator) -> Dict[str, Dict[str, List[Tuple[str, str]]]]:
        Constrói a estrutura de documentação a partir dos dados gerados.
    _check_and_group_subcategories(documentation_structure: Dict[str, Dict[str, List[Tuple[str, str]]]]):
        Verifica e agrupa subcategorias na estrutura de documentação.
    _add_documentation_blocks(mkdocs_manager: MkdocsManagerSoar, base_path: List[str], entries: Dict[str, List[Tuple[str, str]]] or List[Tuple[str, str]]):
        Adiciona blocos de documentação ao arquivo de configuração do MkDocs.
    """

    def __init__(
        self, package_name: str, base_directory: str, mkdocs_file_path: str, template_path: str
    ):
        """
        Inicializa a instância da classe DocumentationBuilder.
        """
        self.base_directory_abs = Path(base_directory).resolve()
        self.mkdocs_file_path_abs = Path(mkdocs_file_path).resolve()
        self.template_path_abs = Path(template_path).resolve()
        self.package_name = package_name

    def run(self) -> None:
        """
        Executa o processo de geração da documentação e atualiza o arquivo mkdocs.yml
        com as novas entradas de documentação geradas.
        """
        mapper = PackageMapper(self.package_name)
        mapper.map_package()

        documentation_generator = DocumentationGenerator(mapper, str(self.base_directory_abs))
        documentation_generator.generate()

        mkdocs_manager = MkdocsManagerSoar(
            str(self.mkdocs_file_path_abs), str(self.template_path_abs)
        )
        mkdocs_manager.load_yaml()

        documentation_structure = self._build_documentation_structure(documentation_generator)

        for main_category, subcategories in documentation_structure.items():
            self._add_documentation_blocks(
                mkdocs_manager, ["Reference (Code API)", main_category], subcategories
            )

        mkdocs_manager.save_yaml()
        print("Documentação gerada e mkdocs.yml atualizado com sucesso.")

    def _build_documentation_structure(
        self, documentation_generator: DocumentationGenerator
    ) -> dict[str, dict[str, list[tuple[str, str]]]]:
        """
        Constrói a estrutura da documentação com base nas categorias e arquivos gerados
        pelo DocumentationGenerator.

        Parameters
        ----------
        documentation_generator : DocumentationGenerator
            A instância do gerador de documentação após mapear o pacote e gerar os arquivos Markdown.

        Returns
        -------
        Dict[str, Dict[str, List[Tuple[str, str]]]]
            Um dicionário representando a estrutura de documentação para atualização no mkdocs.yml.
        """
        documentation_structure = defaultdict(lambda: defaultdict(list))
        for category, files in documentation_generator.categories.items():
            category_parts = category.split(" / ")
            main_category = category_parts[0]
            for file_path in files:
                file_path_abs = file_path.resolve()
                relative_path = file_path_abs.relative_to(self.base_directory_abs.parent)
                relative_path_unix = str(relative_path).replace("\\", "/")
                title = file_path.stem.replace("_", " ").title()
                if len(category_parts) > 1:
                    subcategory_key = "/".join(category_parts[1:])
                    documentation_structure[main_category][subcategory_key].append(
                        (title, "reference/" + relative_path_unix)
                    )
                else:
                    documentation_structure[main_category][title].append(
                        (title, "reference/" + relative_path_unix)
                    )

        self._check_and_group_subcategories(documentation_structure)
        return documentation_structure

    def _check_and_group_subcategories(
        self, documentation_structure: dict[str, dict[str, list[tuple[str, str]]]]
    ) -> None:
        """
        Verifica e agrupa subcategorias na estrutura de documentação, tratando casos especiais
        como 'ticket_system' para estruturar adequadamente no mkdocs.yml.

        Parameters
        ----------
        documentation_structure : Dict[str, Dict[str, List[Tuple[str, str]]]]
            A estrutura da documentação que está sendo construída.
        """
        for main_category, subcategories in list(documentation_structure.items()):
            new_subcategories = defaultdict(lambda: defaultdict(list))
            for subcategory, entries in list(subcategories.items()):
                subcategory_parts = subcategory.split("/")
                if len(subcategory_parts) > 1 and "ticket_system" in subcategory:
                    common_prefix = subcategory_parts[0]
                    new_subcategory_key = "/".join(subcategory_parts[:2])
                    for entry in entries:
                        if isinstance(entry, tuple) and len(entry) == 2:
                            title, path = entry
                            new_subcategories[common_prefix][new_subcategory_key].append(
                                (title, path)
                            )
                        else:
                            print(f"Unexpected entry: {entry}")
                else:
                    new_subcategories[main_category][subcategory] = entries
            documentation_structure[main_category] = new_subcategories[main_category]

    def _add_documentation_blocks(
        self,
        mkdocs_manager: MkdocsManagerSoar,
        base_path: list[str],
        entries: dict[str, list[tuple[str, str]]] or list[tuple[str, str]],
    ) -> None:
        """
        Adiciona blocos de documentação ao arquivo mkdocs.yml com base na estrutura de documentação.

        Parameters
        ----------
        mkdocs_manager : MkdocsManagerSoar
            A instância do gerenciador do MkDocs.
        base_path : List[str]
            O caminho base (categorias principais) sob o qual a documentação deve ser adicionada.
        entries : Dict[str, List[Tuple[str, str]]] or List[Tuple[str, str]]
            As entradas da documentação a serem adicionadas. Pode ser um dicionário representando
            subcategorias ou uma lista de tuplas (título, caminho) para adição direta.
        """
        if isinstance(entries, dict):
            for key, value in entries.items():
                self._add_documentation_blocks(mkdocs_manager, [*base_path, key], value)
        elif isinstance(entries, list):
            for title, path in entries:
                mkdocs_manager.add_documentation_block([*base_path, title], path)


if __name__ == "__main__":
    package_name = "imperiumengine"
    base_directory = "../../docs/reference/imperiumengine/"
    mkdocs_file_path = "../../mkdocs.yml"
    template_path = "../../doc_data/template_mkdocs.yml"

    builder = SoarDocumentationBuilder(
        package_name, base_directory, mkdocs_file_path, template_path
    )
    builder.run()
