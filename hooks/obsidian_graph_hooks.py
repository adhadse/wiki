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
        self.data = {"nodes": [], "links": []}
        
    def reset(self):
        """Reset state for new builds"""
        self.nodes = {}
        self.current_id = 0
        self.data = {"nodes": [], "links": []}
    
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

    def collect_pages(self, nav, config):
        for page in nav.pages:
            page.read_source(config=config)
            self.nodes[self.get_page_path(page)] = {
                "id": self.id,
                "title": page.title,
                "url": page.abs_url,
                "symbolSize": 0,
                "markdown": page.markdown,
                "is_index": page.is_index
            }
        # After collecting pages, establish directory structure links
        self.create_directory_links()

    def create_directory_links(self):
        """Create links based on directory structure - parent directories to child nodes"""
        print("Creating directory structure links...")
        # First, identify all directories and create nodes for them if they don't exist
        directories = set()
        for page_path in list(self.nodes.keys()):
            # Get all parent directories for this page
            dir_path = os.path.dirname(page_path)
            if dir_path:
                directories.add(dir_path)
                # Also add any parent directories
                parent = dir_path
                while '/' in parent:
                    parent = os.path.dirname(parent)
                    if parent:
                        directories.add(parent)
        
        # Create nodes for directories if they don't exist
        for dir_path in directories:
            if dir_path not in self.nodes:
                self.nodes[dir_path] = {
                    "id": self.id,
                    "title": os.path.basename(dir_path) or dir_path,
                    "url": "",
                    "symbolSize": 1,
                    "markdown": "",
                    "is_index": False
                }
                print(f"Created directory node: {dir_path}")
        
        # Create links from parent directories to their immediate children
        links_added = 0
        for path in list(self.nodes.keys()):
            dir_path = os.path.dirname(path)
            if dir_path and dir_path in self.nodes:
                # Create link from parent directory to child
                link = {
                    "source": str(self.nodes[dir_path]["id"]),
                    "target": str(self.nodes[path]["id"])
                }
                
                # Check if this link already exists
                link_exists = False
                for existing_link in self.data["links"]:
                    if existing_link["source"] == link["source"] and existing_link["target"] == link["target"]:
                        link_exists = True
                        break
                
                if not link_exists:
                    self.data["links"].append(link)
                    links_added += 1
                    # Increase symbol sizes for both nodes
                    self.nodes[dir_path]["symbolSize"] = self.nodes[dir_path].get("symbolSize", 1) + 1
                    self.nodes[path]["symbolSize"] = self.nodes[path].get("symbolSize", 1) + 1
        
        print(f"Added {links_added} directory structure links")

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
                source_node = source_page_path
                target_node = target_page_path
            else:
                # Otherwise, link through parent directories
                # Ensure parent directory nodes exist
                if source_dir and source_dir not in self.nodes:
                    self.nodes[source_dir] = {
                        "id": self.id,
                        "title": os.path.basename(source_dir),
                        "url": "",
                        "symbolSize": 1,
                        "markdown": "",
                        "is_index": False
                    }
                    print(f"Created parent directory node: {source_dir}")
                
                if target_dir and target_dir not in self.nodes:
                    self.nodes[target_dir] = {
                        "id": self.id,
                        "title": os.path.basename(target_dir),
                        "url": "",
                        "symbolSize": 1,
                        "markdown": "",
                        "is_index": False
                    }
                    print(f"Created parent directory node: {target_dir}")
                
                # Use directories as source and target if they exist, otherwise use pages
                source_node = source_dir if source_dir else source_page_path
                target_node = target_dir if target_dir else target_page_path
                print(f"Pages in different directories, linking through parents: {source_node} -> {target_node}")
            
            # Create the link
            link = {
                "source": str(self.nodes[source_node]["id"]),
                "target": str(self.nodes[target_node]["id"])
            }
            
            # Check if this link already exists
            link_exists = False
            for existing_link in self.data["links"]:
                if existing_link["source"] == link["source"] and existing_link["target"] == link["target"]:
                    link_exists = True
                    break
            
            if not link_exists:
                self.data["links"].append(link)
                print(f"Added link: {source_node} (ID: {self.nodes[source_node]['id']}) -> {target_node} (ID: {self.nodes[target_node]['id']})")
                
                # Increase symbol sizes
                self.nodes[source_node]["symbolSize"] = self.nodes[source_node].get("symbolSize", 1) + 1
                self.nodes[target_node]["symbolSize"] = self.nodes[target_node].get("symbolSize", 1) + 1
            else:
                print(f"Link already exists: {source_node} -> {target_node}")
        
        print(f"Finished processing markdown for {self.get_page_path(page)}. Total links: {len(self.data['links'])}")

    def create_graph_json(self, config):
        # Reset nodes and links for fresh generation
        self.data["nodes"] = []
        
        for node_path, node_data in self.nodes.items():
            node = {
                "id": str(node_data["id"]),
                "name": node_data["title"],
                "symbolSize": node_data["symbolSize"],
                "value": node_data["url"]
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
    graph_state.site_path = config['site_name'] + "/"
    return config

def on_pre_build(config, **kwargs):
    """Reset state before each build"""
    print("Obsidian Graph: Pre-build reset...")
    graph_state.reset()
    graph_state.site_path = config['site_name'] + "/"

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
    print("Obsidian Graph: Creating graph JSON...")
    graph_state.create_graph_json(config)
    return env

def on_post_build(config, **kwargs):
    """Ensure graph JSON is created after build"""
    print("Obsidian Graph: Post-build graph creation...")
    graph_state.create_graph_json(config)