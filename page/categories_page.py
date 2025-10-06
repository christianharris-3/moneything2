import src.utils as utils
# utils.block_if_no_auth()
import streamlit as st
from src.db_manager import DatabaseManager
from src.logger import log

# st.set_page_config(page_title="Categories - Money Thing", page_icon="📈",layout="wide")


class CategoryTree:
    def __init__(self, category_row):
        self.category_row = category_row
        self.category_name = category_row["name"]
        self.children = []
    def attempt_to_add_child(self, parent_category, child_tree):
        if parent_category == self.category_name:
            self.children.append(child_tree)
            return True
        for child in self.children:
            if child.attempt_to_add_child(parent_category, child_tree):
                return True
        return False
    def get_width(self):
        if len(self.children) == 0:
            return 1
        else:
            return sum([child.get_width() for child in self.children])

    def make_streamlit_ui(self, container):
        container.button(
            self.category_name,
            use_container_width=True,
            on_click=set_selected_category,
            args=(self.category_row["category_id"], self.category_row["name"], self.category_row["parent_name"])
        )
        if len(self.children)>0:
            widths = [child.get_width() for child in self.children]
            columns = container.columns(widths)

            for i, child in enumerate(self.children):
                child.make_streamlit_ui(columns[i])

    def __str__(self):
        child_strs = [str(child) for child in self.children]
        return f"<CategoryTree ({self.category_name}): [{', '.join(child_strs)}]>"
    def __repr__(self):
        return str(self)


    @staticmethod
    def generate_category_trees(db_manager):
        categories = db_manager.categories.db_data
        trees = []
        used_names = set()
        for i, row in categories.iterrows():
            if row["name"] in used_names:
                continue
            used_names.add(row["name"])
            CategoryTree.add_category_to_trees(
                trees,
                row
            )
        return trees


    @staticmethod
    def add_category_to_trees(trees, row):
        category = row["name"]
        parent_category = row["parent_name"]
        if category is None:
            return

        child_tree = None
        for tree in trees:
            if tree.category_name == category:
                child_tree = tree
                break
        if child_tree is None:
            child_tree = CategoryTree(row)

        child_added = False
        for tree in trees:
            if tree.attempt_to_add_child(parent_category, child_tree):
                child_added = True
        if not child_added:
            trees.append(child_tree)

def set_selected_category(category_id, category_name, parent_category_name):
    st.session_state["selected_category"] = category_id
    st.session_state["category_name_input"] = category_name
    st.session_state["parent_category_input"] = parent_category_name

def clear_selection():
    set_selected_category(None, None, None)


def save_category(category_id, name, parent_name):
    db_manager = DatabaseManager()
    parent_category_id = db_manager.categories.get_id_from_value("name", parent_name)
    save_data = {
        "name": name,
        "parent_category_id": parent_category_id
    }

    if category_id is None:
        if name in db_manager.get_all_categories():
            st.toast(f"Name '{name}' already in use", icon="⛔")
        else:
            db_manager.db.create_row(
                db_manager.categories.TABLE,
                save_data
            )
            st.toast(f"Added new '{name}' Category with parent '{parent_name}'")
    else:
        db_manager.db.update_row(
            db_manager.categories.TABLE,
            save_data,
            "category_id",
            category_id
        )
        st.toast(f"Updated ID {category_id} to '{name}' Category with parent '{parent_name}'")

def delete_category(category_id):
    db_manager = DatabaseManager()
    db_manager.db.delete(
        db_manager.categories.TABLE,
        "category_id",
        category_id
    )
    st.toast(f"Deleted Category {category_id}")
    clear_selection()

def categories_page_ui():
    log("Loading page 2: Edit Vendors")

    if "selected_category" not in st.session_state:
        st.session_state["selected_category"] = None

    db_manager = DatabaseManager()

    trees = CategoryTree.generate_category_trees(db_manager)

    root_nodes = [tree.category_name for tree in trees]
    categories = db_manager.get_all_categories()

    st.markdown("# Categories")

    tree, _, specific = st.columns([0.59, 0.01, 0.4])

    root = tree.selectbox("Parent Categories", root_nodes)
    tree.divider()

    trees[root_nodes.index(root)].make_streamlit_ui(tree)

    selected = st.session_state["selected_category"]

    with specific:
        specific_view = specific.container(border=True)

        title_space, clear = specific_view.columns([0.6, 0.3], vertical_alignment="center")
        if selected is None:
            title_space.markdown("## Create Category")
        else:
            title_space.markdown(f"## Category {selected}")
        clear.button("Clear", use_container_width=True, on_click=clear_selection)

        new_category_name = specific_view.text_input("Name", None, key="category_name_input")

        textbox, clear_button = specific_view.columns([0.8, 0.2], vertical_alignment="center")
        clear_button.markdown("")
        if clear_button.button("No Parent", use_container_width=True):
            st.session_state["parent_category_input"] = None
        parent_category_name = textbox.selectbox(
            "Parent Category",
            options=categories,
            key="parent_category_input"
        )

        save, add_child, delete = specific_view.columns([1, 1, 1])

        if selected is not None:
            delete.button(
                "Delete",
                use_container_width=True,
                icon="🗑️",
                on_click=delete_category,
                args=(selected,)
            )
        save.button(
            "Save Category",
            use_container_width=True,
            on_click=save_category,
            args=(selected, new_category_name, parent_category_name)
        )
        add_child.button(
            "Add Child",
            use_container_width=True,
            on_click=set_selected_category,
            args=(None, "new category", new_category_name)
        )


if __name__ == "__main__":
    import src.utils as utils
    utils.block_if_no_auth()
    categories_page_ui()