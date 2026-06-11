import json
import os
from pathlib import Path

def sanitize_filename(name):
    """Sanitize filename for Obsidian"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name

def create_obsidian_vault(graph_path, output_dir):
    """Create Obsidian vault from graph.json"""
    
    # Load graph data
    with open(graph_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    nodes = data['nodes']
    links = data['links']
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Group nodes by community
    communities = {}
    for node in nodes:
        comm = node.get('community', 0)
        if comm not in communities:
            communities[comm] = []
        communities[comm].append(node)
    
    # Create community folders
    for comm_id, comm_nodes in communities.items():
        comm_dir = output_path / f"Community_{comm_id}"
        comm_dir.mkdir(exist_ok=True)
        
        # Create markdown file for each node
        for node in comm_nodes:
            label = node.get('label', 'Unknown')
            filename = sanitize_filename(label) + '.md'
            filepath = comm_dir / filename
            
            # Build content
            content = f"# {label}\n\n"
            
            # Add metadata
            if 'source_file' in node:
                content += f"**Source:** `{node['source_file']}`\n"
            if 'source_location' in node:
                content += f"**Location:** {node['source_location']}\n"
            if 'file_type' in node:
                content += f"**Type:** {node['file_type']}\n"
            
            content += f"**Community:** {comm_id}\n\n"
            
            # Find connections
            node_id = node.get('id', label)
            outgoing = []
            incoming = []
            
            for link in links:
                source = link.get('source', '')
                target = link.get('target', '')
                relation = link.get('relation', 'related')
                
                if source == node_id:
                    # Find target node label
                    target_node = next((n for n in nodes if n.get('id') == target), None)
                    if target_node:
                        outgoing.append((target_node.get('label', target), relation))
                
                if target == node_id:
                    # Find source node label
                    source_node = next((n for n in nodes if n.get('id') == source), None)
                    if source_node:
                        incoming.append((source_node.get('label', source), relation))
            
            # Add connections with wiki-links
            if outgoing:
                content += "## Uses / Calls\n"
                for target_label, relation in outgoing[:10]:  # Limit to 10
                    content += f"- [[{target_label}]] ({relation})\n"
                content += "\n"
            
            if incoming:
                content += "## Used By / Called By\n"
                for source_label, relation in incoming[:10]:  # Limit to 10
                    content += f"- [[{source_label}]] ({relation})\n"
                content += "\n"
            
            # Write file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
    
    # Create index file
    index_path = output_path / "INDEX.md"
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write("# QWMO Knowledge Graph\n\n")
        f.write(f"**Total Nodes:** {len(nodes)}\n")
        f.write(f"**Total Edges:** {len(links)}\n")
        f.write(f"**Communities:** {len(communities)}\n\n")
        
        f.write("## Communities\n\n")
        for comm_id in sorted(communities.keys()):
            comm_nodes = communities[comm_id]
            f.write(f"### Community {comm_id} ({len(comm_nodes)} nodes)\n")
            for node in comm_nodes[:5]:  # Show first 5
                label = node.get('label', 'Unknown')
                f.write(f"- [[{label}]]\n")
            if len(comm_nodes) > 5:
                f.write(f"- ... and {len(comm_nodes) - 5} more\n")
            f.write("\n")
    
    print(f"[OK] Created Obsidian vault at: {output_path}")
    print(f"[OK] {len(nodes)} markdown files")
    print(f"[OK] {len(communities)} community folders")
    print(f"[OK] INDEX.md with overview")

if __name__ == '__main__':
    graph_path = 'graphify-out/graph.json'
    output_dir = 'obsidian-vault'
    create_obsidian_vault(graph_path, output_dir)
