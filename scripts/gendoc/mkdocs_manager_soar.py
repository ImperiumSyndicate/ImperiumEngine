from pathlib import Path

import yaml


class MkdocsManagerSoar:
    """
    Gerencia operações no arquivo mkdocs.yml, permitindo carregar templates,
    adicionar ou remover blocos de documentação.

    Parameters
    ----------
    filepath: str
        O caminho para o arquivo mkdocs.yml que será gerenciado.
    template_path: str
        O caminho para o arquivo de template do mkdocs.yml.

    Attributes
    ----------
    filepath: str
        O caminho para o arquivo mkdocs.yml.
    template_path: str
        O caminho para o arquivo de template do mkdocs.yml.
    data: Optional[dict]
        Os dados carregados do arquivo mkdocs.yml ou template.

    """

    def __init__(
        self,
        filepath: str = "mkdocs.yml",
        template_path: str = "../../doc_data/template_mkdocs.yml",
    ):
        self.filepath: Path = Path(filepath)
        self.template_path: Path = Path(template_path)
        self.data: dict | None = None
        if self.template_path.exists():
            self.load_template()

    def load_yaml(self) -> None:
        """
        Carrega o arquivo mkdocs.yml especificado pelo atributo `filepath`.
        """
        with self.filepath.open("r") as file:
            self.data = yaml.safe_load(file)

    def load_template(self) -> None:
        """
        Carrega o template do arquivo mkdocs.yml especificado pelo atributo `template_path`.
        Levanta FileNotFoundError se o template não for encontrado.
        """
        if not self.template_path.exists():
            msg = f"O arquivo de template {self.template_path} não foi encontrado."
            raise FileNotFoundError(msg)
        with self.template_path.open("r") as file:
            self.data = yaml.safe_load(file)
        self.save_yaml()  # Salva o template como o novo arquivo mkdocs.yml

    def save_yaml(self) -> None:
        """
        Salva as alterações feitas nos dados do mkdocs.yml de volta ao arquivo especificado por `filepath`.
        """
        with self.filepath.open("w") as file:
            yaml.safe_dump(self.data, file, sort_keys=False, default_flow_style=False)

    def recreate_documentation(self) -> None:
        """
        Recria o arquivo mkdocs.yml, deletando a versão existente e criando uma nova a partir do template.
        """
        if self.template_path.exists() and self.filepath.exists():
            self.filepath.unlink()  # Remove o arquivo existente
        self.load_template()  # Carrega e salva o template como novo arquivo mkdocs.yml

    def add_documentation_block(self, path: list[str], content: list[str] or str) -> None:
        """
        Adiciona um novo bloco de documentação ao arquivo mkdocs.yml seguindo um caminho especificado.

        Parameters
        ----------
        path : List[str]
            O caminho no arquivo mkdocs.yml onde o novo bloco de documentação será adicionado.
        content : List[str] or str
            O conteúdo a ser adicionado. Pode ser uma lista de strings ou uma única string.
        """
        if "nav" not in self.data:
            self.data["nav"] = []
        current_level = self.data["nav"]
        for part in path[:-1]:  # Navega através do caminho, exceto o último elemento
            found = False
            for item in current_level:
                if isinstance(item, dict) and part in item:
                    current_level = item[part]
                    found = True
                    break
            if not found:  # Se a parte não foi encontrada, cria uma nova
                new_part = {part: []}
                current_level.append(new_part)
                current_level = new_part[part]
        # Adiciona o conteúdo no último nível do caminho
        last_part = path[-1]
        found = False
        for item in current_level:
            if isinstance(item, dict) and last_part in item:
                if isinstance(content, list):
                    item[last_part].extend(content)
                else:
                    item[last_part].append(content)
                found = True
                break
        if not found:
            if isinstance(content, list):
                new_content = {last_part: content}
            else:
                new_content = {last_part: [content]}
            current_level.append(new_content)

    def remove_documentation_block(self, path: list[str]) -> None:
        """
        Remove um bloco de documentação do arquivo mkdocs.yml seguindo um caminho especificado.

        Parameters
        ----------
        path : List[str]
            O caminho no arquivo mkdocs.yml do bloco de documentação a ser removido.
        """
        if "nav" not in self.data or not path:
            return
        current_level = self.data["nav"]
        for i, part in enumerate(path):
            found = False
            for j, item in enumerate(current_level):
                if isinstance(item, dict) and part in item:
                    if i == len(path) - 1:  # Se for o último elemento do caminho, remove
                        current_level.pop(j)
                    else:
                        current_level = item[part]
                    found = True
                    break
            if not found:
                break  # Se a parte do caminho não for encontrada, interrompe a busca
        self.save_yaml()
