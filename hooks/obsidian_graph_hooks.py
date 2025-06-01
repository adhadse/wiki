import json
import os
import re
from urllib.parse import urljoin

# Global state to maintain data across hook calls
class GraphState:
    def __init__(self):
        self.nodes = {}
        self.site_path = ""
        self.current_id = 0
        self.data = {"nodes": [], "links": [], "categories": []}
        self.categories_map = {}
        self.next_category_id = 0
        
    def reset(self):
        """Reset state for new builds"""
        self.nodes = {}
        self.current_id = 0
        self.data = {"nodes": [], "links": [], "categories": []}
        self.categories_map = {}
        self.next_category_id = 0
    
    @property
    def id(self):
        current_id = self.current_id
        self.current_id += 1
        return current_id

    def get_path(self, base: str, *argv) -> str:
        result = base
        for path in argv:
            result = urljoin(result, path)
        return result

    def get_page_path(self, page) -> str:
        return self.get_path(self.site_path, page.file.src_uri).replace(".md", "")

    def page_if_exists(self, page: str) -> str:
        page = self.get_path(self.site_path, page)
        for k in self.nodes.keys():
            if k == page:
                return page
        return None

    def _get_or_create_category_id(self, category_name: str) -> int:
        """Gets the ID for a category name, creating it if it doesn't exist."""
        if category_name not in self.categories_map:
            self.categories_map[category_name] = self.next_category_id
            self.next_category_id += 1
        return self.categories_map[category_name]

    def collect_pages(self, nav, config):
        for page in nav.pages:
            page.read_source(config=config)
            self.nodes[self.get_page_path(page)] = {
                "id": self.id,
                "title": page.title,
                "url": page.abs_url,
                "symbolSize": 0,  # Initialize to 0, will be updated later by depth
                "markdown": page.markdown,
                "is_index": page.is_index
            }
        # After collecting pages, directory structure links will be handled later
        # self.create_directory_links()

    def establish_directory_graph(self):
        """Ensure all directory nodes exist and create hierarchical links."""
        print("Obsidian Graph: Establishing directory graph...")

        site_root_key = self.site_path.rstrip('/')
        if site_root_key and site_root_key not in self.nodes:
            self.nodes[site_root_key] = {
                "id": self.id,
                "title": os.path.basename(site_root_key) or site_root_key, # e.g., "Wiki" if site_path is "Wiki"
                "url": "", # Site root itself
                "symbolSize": 0, # Placeholder, will be set by depth (should be largest)
                "markdown": "",
                "is_index": True, # Conceptually the main index/root
                "category": self._get_or_create_category_id(site_root_key or "Root") # Assign category
            }
            print(f"Obsidian Graph: Created site root node: '{site_root_key}'")
        
        # Gather all potential directory paths from existing page nodes
        all_page_node_paths = set(k for k, v in self.nodes.items() if k != site_root_key and v.get("markdown") is not None) # Consider only page paths for deriving dirs
        directories_to_ensure = set()

        for path_key in all_page_node_paths:
            current_parent = os.path.dirname(path_key)
            # Traverse up to, but not including, an empty path or the site_root_key itself
            while current_parent and current_parent != site_root_key and current_parent != '/':
                directories_to_ensure.add(current_parent)
                next_parent = os.path.dirname(current_parent)
                if next_parent == current_parent: # Reached top (e.g. dirname("/") is "/"), or dirname("foo") when CWD is root.
                    break
                current_parent = next_parent
        
        # Create nodes for these sub-directories if they don't exist
        for dir_path_key in directories_to_ensure:
            if dir_path_key not in self.nodes:
                self.nodes[dir_path_key] = {
                    "id": self.id,
                    "title": os.path.basename(dir_path_key) or dir_path_key.split('/')[-1],
                    "url": "", 
                    "symbolSize": 0, # Placeholder
                    "markdown": "",
                    "is_index": False
                }
                print(f"Obsidian Graph: Created directory node for sub-path: '{dir_path_key}'")

        # Create links from parent directories/site_root to their immediate children
        links_added = 0
        current_node_keys = list(self.nodes.keys())
        for node_key in current_node_keys:
            if node_key == site_root_key: # The root node itself doesn't have a parent in this context
                continue

            parent_key = os.path.dirname(node_key)
            # If os.path.dirname gives an empty string (e.g. for top-level files like "page.md" if site_root is not part of key)
            # and a site_root_key exists, assume parent is site_root_key.
            if not parent_key and site_root_key:
                 parent_key = site_root_key
            elif not parent_key and not site_root_key: # No parent and no site root (e.g. flat structure)
                 continue

            if parent_key in self.nodes: # Check if the determined parent_key actually corresponds to an existing node
                link = {
                    "source": str(self.nodes[parent_key]["id"]),
                    "target": str(self.nodes[node_key]["id"])
                }
                
                link_exists = any(
                    el["source"] == link["source"] and el["target"] == link["target"]
                    for el in self.data["links"]
                )
                
                if not link_exists:
                    self.data["links"].append(link)
                    links_added += 1
            # else:
                # print(f"Obsidian Graph DEBUG: For node '{node_key}', parent_key '{parent_key}' not found in self.nodes. No structural link created.")
        
        print(f"Obsidian Graph: Added {links_added} directory structure links during graph establishment.")

    def parse_markdown(self, markdown: str, page):        
        # Extract wiki links from markdown
        WIKI_PATTERN = re.compile(r"\[\[([^\]|#]+)(?:\|[^\]]+)?(?:#[^\]]+)?\]\]")
        links_found = list(re.finditer(WIKI_PATTERN, markdown))
        # print(f"Found {len(links_found)} wikilinks in page {self.get_page_path(page)}")
        
        if not links_found:
            return
            
        # Process each wiki link
        for match in links_found:
            wikilink = match.group(1).strip()
            source_page_path = self.get_page_path(page)
            print(f"Processing wikilink '{wikilink}' from page '{source_page_path}'")
            
            # Resolve target page
            target_page_path = None
            
            # Check if the wikilink is "index" and the current page is an index
            if wikilink == "index" and self.nodes[source_page_path]["is_index"]:
                target_page_path = source_page_path
                print(f"Resolved as self-reference (index)")
            else:
                # Try direct match first
                for node_path in self.nodes.keys():
                    if node_path.endswith(f"/{wikilink}") or node_path == wikilink:
                        target_page_path = node_path
                        print(f"Direct match found: {target_page_path}")
                        break
                
                # If no direct match, try relative path
                if not target_page_path:
                    relative_path = self.get_path(source_page_path, wikilink)
                    if relative_path in self.nodes:
                        target_page_path = relative_path
                        print(f"Relative path match found: {target_page_path}")
            
            if not target_page_path:
                print(f"WARNING: No target page found for wikilink: {wikilink}")
                continue
                
            # Determine if we should link pages directly or through parent directories
            source_dir = os.path.dirname(source_page_path)
            target_dir = os.path.dirname(target_page_path)
            
            # If pages are in the same directory, link them directly
            if source_dir == target_dir:
                print(f"Pages in same directory ({source_dir}), linking directly")
                source_node_path = source_page_path
                target_node_path = target_page_path
            else:
                # Otherwise, link through parent directories
                # Ensure parent directory nodes exist (basic creation if not)
                if source_dir and source_dir not in self.nodes:
                    self.nodes[source_dir] = {
                        "id": self.id,
                        "title": os.path.basename(source_dir) or source_dir.split('/')[-1] or "root_dir",
                        "url": "",
                        "symbolSize": 0, # Placeholder, will be set by depth
                        "markdown": "",
                        "is_index": False 
                    }
                    print(f"Created missing source directory node during parsing: {source_dir}")
                
                if target_dir and target_dir not in self.nodes:
                    self.nodes[target_dir] = {
                        "id": self.id,
                        "title": os.path.basename(target_dir) or target_dir.split('/')[-1] or "root_dir",
                        "url": "",
                        "symbolSize": 0, # Placeholder, will be set by depth
                        "markdown": "",
                        "is_index": False
                    }
                    print(f"Created missing target directory node during parsing: {target_dir}")
                
                # Use directories as source and target if they exist and are valid, otherwise use pages
                source_node_path = source_dir if source_dir and source_dir in self.nodes else source_page_path
                target_node_path = target_dir if target_dir and target_dir in self.nodes else target_page_path
                print(f"Pages in different directories, linking through resolved nodes: {source_node_path} -> {target_node_path}")
            
            # Create the link, ensuring nodes exist
            if source_node_path not in self.nodes:
                print(f"WARNING: Source node {source_node_path} for wikilink does not exist. Skipping link.")
                continue
            if target_node_path not in self.nodes:
                print(f"WARNING: Target node {target_node_path} for wikilink does not exist. Skipping link.")
                continue

            link = {
                "source": str(self.nodes[source_node_path]["id"]),
                "target": str(self.nodes[target_node_path]["id"])
            }
            
            # Check if this link already exists
            link_exists = any(
                existing_link["source"] == link["source"] and existing_link["target"] == link["target"]
                for existing_link in self.data["links"]
            )
            
            if not link_exists:
                self.data["links"].append(link)
                print(f"Added link: {source_node_path} (ID: {self.nodes[source_node_path]['id']}) -> {target_node_path} (ID: {self.nodes[target_node_path]['id']})")
                
                # Symbol sizes are not incremented here; they will be set by depth later.
                # self.nodes[source_node_path]["symbolSize"] = self.nodes[source_node_path].get("symbolSize", 1) + 1
                # self.nodes[target_node_path]["symbolSize"] = self.nodes[target_node_path].get("symbolSize", 1) + 1
            else:
                print(f"Link already exists: {source_node_path} -> {target_node_path}")
        
        print(f"Finished processing markdown for {self.get_page_path(page)}. Total links: {len(self.data['links'])}")

    def update_all_symbol_sizes_by_depth(self):
        """Calculate and update symbolSize for all nodes based on their directory depth."""
        print("Obsidian Graph: Updating symbol sizes by depth...")

        normalized_site_root = self.site_path.rstrip('/') if self.site_path else ""
        print(f"Obsidian Graph DEBUG: effective normalized_site_root for stripping = '{normalized_site_root}' (original site_path: '{self.site_path}')")
        
        updated_nodes_count = 0
        if not self.nodes:
            print("Obsidian Graph DEBUG: No nodes to update.")
            return

        for node_path_key, node_data in self.nodes.items():
            # Ensure node_path_key is a string, though it always should be.
            current_node_path = str(node_path_key) 
            
            path_for_depth_calc = current_node_path
            
            # If normalized_site_root is present AND the current_node_path starts with it,
            # then strip it to get a path relative to that root.
            # Otherwise, use current_node_path as is (assuming it's already relative to the true content root).
            if normalized_site_root and current_node_path.startswith(normalized_site_root):
                path_for_depth_calc = current_node_path[len(normalized_site_root):]
                starts_with_root_text = f"True (stripped prefix '{normalized_site_root}')"
            else:
                # This case handles paths like "cs/page" when normalized_site_root is "Wiki",
                # or when normalized_site_root is empty.
                starts_with_root_text = f"False (node_path '{current_node_path}' vs root '{normalized_site_root}')"

            clean_relative_path = path_for_depth_calc.lstrip('/')
            
            # Revised depth calculation:
            # The root node (where clean_relative_path is "") is depth 0.
            # Other nodes have depth based on segment count of their relative path.
            if not clean_relative_path: # This should be the site root node itself
                depth = 0
                new_symbol_size = max(1, 20 - depth*2) 
                category_name = self.site_path.rstrip('/') or "Root"
            else:
                depth = clean_relative_path.count('/') + 1
                new_symbol_size = max(1, 10 - depth*2) 
                if depth == 1:
                    # For top-level directories/pages, use their title as category
                    category_name = node_data.get("title", "Default Category")
                else:
                    # For deeper nodes, use a generic category
                    category_name = "Content"
            
            node_data["category"] = self._get_or_create_category_id(category_name)
            print(f"Obsidian Graph DEBUG: Node='{current_node_path}': StartsWithRootLogic='{starts_with_root_text}', PathForDepth='{path_for_depth_calc}', CleanRelPath='{clean_relative_path}', Depth={depth}, NewSize={new_symbol_size}, Category='{category_name}' (ID: {node_data['category']})")
            
            if "symbolSize" not in node_data:
                 print(f"Obsidian Graph WARNING:   Node '{current_node_path}' was missing 'symbolSize' key! Initializing before update.")
            
            # original_size = node_data.get("symbolSize", "MISSING") # Keep this commented unless deep debugging values
            node_data["symbolSize"] = new_symbol_size
            updated_nodes_count +=1
        
        print(f"Obsidian Graph: Symbol sizes updated for {updated_nodes_count} nodes. Total nodes in self.nodes: {len(self.nodes)}.")

    def create_graph_json(self, config):
        # Reset nodes and links for fresh generation
        self.data["nodes"] = []
        self.data["categories"] = [] # Reset categories list
        
        # Populate categories for ECharts
        for name, id_val in self.categories_map.items():
            self.data["categories"].append({"name": name}) # ECharts expects categories as list of objects with 'name'
            
        for node_path, node_data in self.nodes.items():
            node = {
                "id": str(node_data["id"]),
                "name": node_data["title"],
                "symbolSize": node_data["symbolSize"],
                "value": node_data["url"],
                "category": node_data.get("category", self._get_or_create_category_id("Default")) # Ensure category exists
            }
            self.data["nodes"].append(node)

        filename = os.path.join(config['site_dir'], 'assets', 'js', 'graph.json')
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as file:
            json.dump(self.data, file, sort_keys=False, indent=2)
        print(f"Graph JSON created at: {filename}")

# Global instance
graph_state = GraphState()

# Hook functions
def on_startup(command, dirty, **kwargs):
    """Reset state when starting the server"""
    print("Obsidian Graph: Starting up...")
    graph_state.reset()

def on_config(config, **kwargs):
    """Configure the graph state"""
    print("Obsidian Graph: Configuring...")
    graph_state.site_path = config['site_name'] # Store site_name without trailing slash
    return config

def on_pre_build(config, **kwargs):
    """Reset state before each build"""
    print("Obsidian Graph: Pre-build reset...")
    graph_state.reset()
    graph_state.site_path = config['site_name'] # Store site_name without trailing slash

def on_nav(nav, config, files, **kwargs):
    """Collect all pages from navigation"""
    print("Obsidian Graph: Collecting pages...")
    graph_state.collect_pages(nav, config)
    return nav

def on_page_markdown(markdown, page, config, files, **kwargs):
    """Parse markdown for wikilinks"""
    graph_state.parse_markdown(markdown, page)
    return markdown

def on_env(env, config, files, **kwargs):
    """Create the graph JSON file"""
    print("Obsidian Graph: Establishing directory graph and updating symbol sizes...")
    graph_state.establish_directory_graph() # Ensure directory structure is fully processed
    graph_state.update_all_symbol_sizes_by_depth() # Calculate all symbol sizes by depth
    
    print("Obsidian Graph: Creating graph JSON...")
    graph_state.create_graph_json(config)
    return env

def on_post_build(config, **kwargs):
    """Ensure graph JSON is created after build"""
    print("Obsidian Graph: Post-build graph creation...")
    graph_state.create_graph_json(config)