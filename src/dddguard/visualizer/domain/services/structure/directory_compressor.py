from typing import Any

from dddguard.shared.domain import CodeNode

from ...value_objects import LeafNode, StyleConfig, VisualContainer, VisualElement


class DirectoryCompressor:
    """
    Stateless Logic: Implements the 'Empty Folder Compression' algorithm.
    Transforms a raw Trie (dict) into a list of VisualElements (Containers + Leaves).
    """

    @staticmethod
    def compress_and_convert(
        trie_node: dict[str, Any],
        style: StyleConfig,
    ) -> list[VisualElement]:
        results: list[VisualElement] = []

        # 1. Identify folders (keys that are not metadata)
        folder_names = [k for k in trie_node if k != "_files"]

        for folder_name in folder_names:
            sub_tree = trie_node[folder_name]

            # --- PATH COMPRESSION ALGORITHM ---
            current_label = folder_name
            cursor = sub_tree

            while True:
                sub_folders = [k for k in cursor if k != "_files"]
                current_files = cursor.get("_files", [])
                has_files = len(current_files) > 0

                if (not has_files) and (len(sub_folders) == 1):
                    next_folder = sub_folders[0]
                    current_label = f"{current_label}/{next_folder}"
                    cursor = cursor[next_folder]
                else:
                    break
            # ----------------------------------

            # Recursion
            children_elements = DirectoryCompressor.compress_and_convert(cursor, style=style)

            if children_elements:
                uid = f"dir_{current_label}_{len(children_elements)}"

                # Standard Folder Container
                container = VisualContainer(
                    x=0.0,
                    y=0.0,
                    width=0.0,
                    height=0.0,
                    label=current_label,
                    children=children_elements,
                    is_visible=True,
                    internal_padding=style.CONTAINER_PAD_X,
                    id=uid,
                )
                results.append(container)

        # 2. Process Files -> WRAP THEM IN CONTAINERS
        raw_files: list[CodeNode] = trie_node.get("_files", [])

        for code_node in raw_files:
            if not code_node.path:
                continue

            # A. Calculate Dimensions
            label_text = style.format_label(code_node.path)
            width_calc = style.calculate_node_width(label_text)
            height_calc = style.NODE_HEIGHT

            # B. Create the LeafNode (The File)
            leaf = LeafNode(
                x=0.0,
                y=0.0,
                width=width_calc,
                height=height_calc,
                label=label_text,
                id=code_node.path,
                source_node=code_node,
                color="none",
            )

            # C. Create the Wrapper Container (The Padding Box)
            # We set is_visible=True so the Layout Engine applies 'pad_x/pad_y'.
            # We set label="" so it renders as a clean box without text overhead.
            wrapper_id = f"wrap_{code_node.path}"

            wrapper = VisualContainer(
                x=0.0,
                y=0.0,
                width=0.0,
                height=0.0,  # Will be expanded by optimizer
                label="",  # No text label
                children=[leaf],  # File is inside
                is_visible=True,  # Must be visible to enforce padding logic
                internal_padding=style.CONTAINER_PAD_X,
                id=wrapper_id,
            )

            results.append(wrapper)

        return results
