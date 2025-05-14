import json
import os
from datetime import datetime

# =================== MODELOS ===================

class Author:
    def __init__(self, name: str, email: str):
        self.__name = name
        self.__email = email
        self.__articles = []

    @property
    def name(self):
        return self.__name

    @property
    def email(self):
        return self.__email

    def add_article(self, article):
        self.__articles.append(article)

    def __str__(self):
        return f"Author: {self.__name} ({self.__email})"


class Category:
    def __init__(self, name: str):
        self.__name = name
        self.__articles = []

    @property
    def name(self):
        return self.__name

    def add_article(self, article):
        self.__articles.append(article)

    def __str__(self):
        return f"Category: {self.__name}"


class Article:
    def __init__(self, title: str, content: str, author: Author, category: Category):
        self.__title = title
        self.__content = content
        self.__author = author
        self.__category = category
        self.__published_at = None

        author.add_article(self)
        category.add_article(self)

    @property
    def title(self):
        return self.__title

    @property
    def content(self):
        return self.__content

    @property
    def author(self):
        return self.__author

    @property
    def category(self):
        return self.__category

    @property
    def published_at(self):
        return self.__published_at

    def publish(self):
        self.__published_at = datetime.now()

    def __str__(self):
        return f"Article: {self.__title} by {self.__author.name} in {self.__category.name} (Published: {self.__published_at})"


# =================== FACTORIES ===================

class EntityFactory:
    @staticmethod
    def get_or_create_author(name: str, email: str, authors: dict):
        if email in authors:
            return authors[email]
        author = Author(name, email)
        authors[email] = author
        return author

    @staticmethod
    def get_or_create_category(name: str, categories: dict):
        if name in categories:
            return categories[name]
        category = Category(name)
        categories[name] = category
        return category


class ArticleFactory:
    @staticmethod
    def create_article(title: str, content: str, author: Author, category: Category) -> Article:
        article = Article(title, content, author, category)
        article.publish()
        return article


# =================== FACADE ===================

class CatalogManager:
    def __init__(self, filepath="database.json"):
        self.filepath = filepath
        self.data = self.load()
        self.authors = {a["email"]: Author(a["name"], a["email"]) for a in self.data["authors"]}
        self.categories = {c["name"]: Category(c["name"]) for c in self.data["categories"]}

    def load(self):
        try:
            with open(self.filepath, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {"authors": [], "categories": [], "articles": []}

    def save(self):
        with open(self.filepath, "w") as file:
            json.dump(self.data, file, indent=4)

    def add_article(self, name, email, category_name, title, content):
        author = EntityFactory.get_or_create_author(name, email, self.authors)
        category = EntityFactory.get_or_create_category(category_name, self.categories)
        article = ArticleFactory.create_article(title, content, author, category)

        if not any(a["email"] == author.email for a in self.data["authors"]):
            self.data["authors"].append({"name": author.name, "email": author.email})

        if not any(c["name"] == category.name for c in self.data["categories"]):
            self.data["categories"].append({"name": category.name})

        self.data["articles"].append({
            "title": article.title,
            "content": article.content,
            "author": author.email,
            "category": category.name,
            "published_at": article.published_at.strftime("%Y-%m-%d %H:%M:%S")
        })

        self.save()
        return article

    def show_catalog(self):
        print("\n=== CATÁLOGO ===")

        print("\n🧠 Autores:")
        for author in self.data.get("authors", []):
            print(f"- {author['name']} ({author['email']})")

        print("\n📁 Categorias:")
        for category in self.data.get("categories", []):
            print(f"- {category['name']}")

        print("\n📝 Artigos:")
        for article in self.data.get("articles", []):
            print(f"- '{article['title']}' por {article['author']} em {article['category']} ({article['published_at']})")

    def list_articles(self):
        return self.data.get("articles", [])

    def show_article(self, index):
        articles = self.data.get("articles", [])
        if 0 <= index < len(articles):
            a = articles[index]
            print("\n=== ARTIGO SELECIONADO ===")
            print(f"Título: {a['title']}\nAutor: {a['author']}\nCategoria: {a['category']}\nPublicado em: {a['published_at']}\n\nConteúdo:\n{a['content']}")


# =================== COMMANDS ===================

class Command:
    def execute(self):
        raise NotImplementedError()


class ShowCatalogCommand(Command):
    def __init__(self, manager: CatalogManager):
        self.manager = manager

    def execute(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.manager.show_catalog()
        input("\nPressione ENTER para voltar ao menu.")


class AddArticleCommand(Command):
    def __init__(self, manager: CatalogManager):
        self.manager = manager

    def execute(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        name = input("Nome do autor: ")
        email = input("Email do autor: ")
        category = input("Nome da categoria: ")
        title = input("Título do artigo: ")
        content = input("Conteúdo do artigo: ")
        self.manager.add_article(name, email, category, title, content)
        print("\n✅ Artigo salvo com sucesso!")
        input("\nPressione ENTER para voltar ao menu.")


class ReadArticleCommand(Command):
    def __init__(self, manager: CatalogManager):
        self.manager = manager

    def execute(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        artigos = self.manager.list_articles()
        if not artigos:
            print("Nenhum artigo cadastrado.")
            input("\nPressione ENTER para voltar.")
            return

        print("=== LISTA DE ARTIGOS ===")
        for i, artigo in enumerate(artigos, start=1):
            print(f"{i}. {artigo['title']} (por {artigo['author']})")

        try:
            escolha = int(input("\nNúmero do artigo: "))
            self.manager.show_article(escolha - 1)
        except (ValueError, IndexError):
            print("\nEntrada inválida.")

        input("\nPressione ENTER para voltar ao menu.")


# =================== MAIN ===================

def main():
    manager = CatalogManager()
    commands = {
        '1': ShowCatalogCommand(manager),
        '2': AddArticleCommand(manager),
        '3': ReadArticleCommand(manager)
    }

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=== MENU PRINCIPAL ===")
        print("1. Ver Catálogo")
        print("2. Adicionar Artigo")
        print("3. Ler Artigo")
        print("0. Sair")

        opcao = input("\nEscolha uma opção: ")

        if opcao == '0':
            break
        elif opcao in commands:
            commands[opcao].execute()
        else:
            print("Opção inválida.")
            input("\nPressione ENTER para continuar.")


if __name__ == "__main__":
    main()
