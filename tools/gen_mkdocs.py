import yaml
import os
from collections import defaultdict
from pprint import pprint

def deep_merge_dicts(dict1, dict2):
    """
    Recursively merges dict2 into dict1.
    Handles lists by extending them and dictionaries by merging them.
    """
    for key, value in dict2.items():
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
            dict1[key] = deep_merge_dicts(dict1[key], value)
        elif key in dict1 and isinstance(dict1[key], list) and isinstance(value, list):
            dict1[key].extend(value)
        else:
            dict1[key] = value
    return dict1

def get_vrf_attach_list(vrf_attach_group_name="", overlay_config={}):
    """
    Returns a list of VRF names attached to a given VRF attachment group.

    Args:
        vrf_attach_group (str): The VRF attachment group name.
        overlay_config (dict): The overlay configuration dictionary.

    Returns:
        list: List of Switch names attached to the specified VRF attachment group.
    """
    switch_list = []

    if 'vrf_attach_groups' in overlay_config:
        for vrf_attach_group in overlay_config['vrf_attach_groups']:
            if vrf_attach_group_name == vrf_attach_group.get('name'):
                switches = vrf_attach_group.get('switches', [])
                for switch in switches:
                    switch_list.append(switch.get('hostname'))
    return switch_list
def get_network_attach_list(net_attach_group="", overlay_config={}):
    """
    Returns a list of Network names attached to a given Network attachment group.

    Args:
        net_attach_group (str): The Network attachment group name.
        overlay_config (dict): The overlay configuration dictionary.

    Returns:
        list: List of Network names attached to the specified Network attachment group.
    """
    switch_list = []

    if 'network_attach_groups' in overlay_config:
        for network_attach_group in overlay_config['network_attach_groups']:
            if net_attach_group == network_attach_group.get('name'):
                pprint(network_attach_group)
                switches = network_attach_group.get('switches', [])
                for switch in switches:
                    switch_list.append(switch)
    return switch_list

def generate_mkdocs_from_nac_yaml_dir(config_dir_path, output_dir="docs"):
    """
    Reads all NetAsCode VXLAN YAML files from a directory, merges them,
    and generates MkDocs-formatted Markdown.

    Args:
        config_dir_path (str): Path to the directory containing input YAML configuration files.
        output_dir (str): Directory where Markdown files and mkdocs.yml will be generated.
    """
    docs_output_path = os.path.join(output_dir, "docs")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(docs_output_path):
        os.makedirs(docs_output_path)

    combined_config = {}
    yaml_files_found = []

    # Read and merge all YAML files in the directory
    for filename in os.listdir(config_dir_path):
        if filename.endswith((".yaml", ".yml")):
            filepath = os.path.join(config_dir_path, filename)
            yaml_files_found.append(filename)
            with open(filepath, 'r') as f:
                try:
                    current_config = yaml.safe_load(f)
                    if current_config: # Ensure the file is not empty
                        combined_config = deep_merge_dicts(combined_config, current_config)
                except yaml.YAMLError as e:
                    print(f"Error parsing YAML file {filepath}: {e}")
                    continue

    if not combined_config:
        print(f"No valid YAML configuration found in {config_dir_path}. Exiting.")
        return
    new_config = combined_config.get('vxlan', {})
    combined_config = new_config
    overlay_config = combined_config.get('overlay', {})
    global_config = combined_config.get('global', {})

    # Determine fabric name for site_name, default if not found
    fabric_name = combined_config.get('fabric', {}).get('name', 'Unnamed Fabric').replace('_', ' ')
    print("Found Fabric Name: ", fabric_name)

    # --- Generate mkdocs.yml ---
    mkdocs_yml_content = f"""
site_name: VXLAN Fabric Documentation - {fabric_name}
site_url: https://your-org.github.io/vxlan-docs/
repo_url: https://github.com/your-org/your-repo/
edit_uri: edit/main/docs/

nav:
  - Home: index.md
  - Fabric Overview: fabric.md
  - Global Settings: global_settings.md
  - Topology:
    - Spines: topology_spines.md
    - Leafs: topology_leafs.md
  - VRFs: vrfs.md
  - Networks: networks.md

theme:
  name: material
  highlightjs: true
  hljs_languages:
    - yaml
    - python
    - json
    - bash
    - console
    - markdown
    - ini
    - diff
    - nginx
    - plaintext
    - css
    - javascript
    - xml

markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.superfences
  - attr_list
  - md_in_html
"""
    with open(os.path.join(output_dir, "mkdocs.yml"), 'w') as f:
        f.write(mkdocs_yml_content)
    print(f"Generated {os.path.join(output_dir, 'mkdocs.yml')}")

    # --- Generate index.md ---
    with open(os.path.join(docs_output_path, "index.md"), 'w') as f:
        f.write(f"# VXLAN Fabric Documentation\n\n")
        f.write(f"This documentation provides an overview of the VXLAN EVPN fabric configured via NetAsCode.\n\n")
        f.write(f"Generated from YAML files in `{config_dir_path}` on {os.environ.get('CI_COMMIT_TIMESTAMP', 'N/A')}.\n\n")
        f.write(f"The following YAML files were processed: {', '.join(yaml_files_found)}.\n\n")
        f.write(f"Use the navigation on the left to explore the fabric configuration details.\n")
    print(f"Generated {os.path.join(docs_output_path, 'index.md')}")

    # --- Generate fabric.md ---
    if 'fabric' in combined_config:
        with open(os.path.join(docs_output_path, "fabric.md"), 'w') as f:
            f.write("# Fabric Overview\n\n")
            f.write("| Setting | Value |\n")
            f.write("|---------|-------|\n")
            for key, value in combined_config['fabric'].items():
                f.write(f"| {key.replace('_', ' ').title()} | {value} |\n")
        print(f"Generated {os.path.join(docs_output_path, 'fabric.md')}")

    # --- Generate global_settings.md ---
    if 'ibgp' in global_config:
        with open(os.path.join(docs_output_path, "global_settings.md"), 'w') as f:
            f.write("# Global Settings\n\n")
            f.write("| Setting | Value |\n")
            f.write("|---------|-------|\n")
            for key, value in global_config['ibgp'].items():
                f.write(f"| {key.replace('_', ' ').title()} | {value} |\n")
        print(f"Generated {os.path.join(docs_output_path, 'global_settings.md')}")

    # --- Generate topology_spines.md ---
    if 'topology' in combined_config and 'switches' in combined_config['topology']:
        with open(os.path.join(docs_output_path, "topology_spines.md"), 'w') as f:
            f.write("# Spine Switches\n\n")
            for spine in combined_config['topology']['switches']:
                if spine.get('role', '').lower() == 'spine':
                    f.write(f"## {spine.get('name', 'Unnamed Spine')}\n\n")
                    f.write("| Setting | Value |\n")
                    f.write("|---------|-------|\n")
                    for key, value in spine.items():
                        f.write(f"| {key.replace('_', ' ').title()} | {value} |\n")
                    f.write("\n")
        print(f"Generated {os.path.join(docs_output_path, 'topology_spines.md')}")

    # --- Generate topology_leafs.md ---
    if 'topology' in combined_config and 'switches' in combined_config['topology']:
        with open(os.path.join(docs_output_path, "topology_leafs.md"), 'w') as f:
            f.write("# Leaf Switches\n\n")
            for leaf in combined_config['topology']['switches']:
                if leaf.get('role', '').lower() != 'spine':
                    f.write(f"## {leaf.get('name', 'Unnamed Leaf')}\n\n")
                    f.write("| Setting | Value |\n")
                    f.write("|---------|-------|\n")
                    for key, value in leaf.items():
                        if key == 'interfaces':
                            f.write(f"| Interfaces | |\n")
                            for iface in value:
                                f.write(f"| &nbsp;&nbsp;&nbsp;&nbsp;**{iface.get('name', 'N/A')}** | |\n")
                                for iface_key, iface_val in iface.items():
                                    if iface_key != 'name':
                                        f.write(f"| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{iface_key.replace('_', ' ').title()} | {iface_val} |\n")
                        else:
                            f.write(f"| {key.replace('_', ' ').title()} | {value} |\n")
                    f.write("\n")
        print(f"Generated {os.path.join(docs_output_path, 'topology_leafs.md')}")

    # pprint(overlay_config)
    # --- Generate vrfs.md ---
    if 'vrfs' in overlay_config:
        with open(os.path.join(docs_output_path, "vrfs.md"), 'w') as f:
            f.write("# VRFs\n\n")
            for vrf in overlay_config['vrfs']:
                f.write(f"## {vrf.get('name', 'Unnamed VRF')}\n\n")
                f.write("| Setting | Value |\n")
                f.write("|---------|-------|\n")
                for key, value in vrf.items():
                    f.write(f"| {key.replace('_', ' ').title()} | {value} |\n")
                f.write("\n")
                switch_list = get_vrf_attach_list(vrf.get('vrf_attach_group', ''), overlay_config)
                if switch_list:
                    f.write(f"### VRF Attached List\n\n")
                    f.write("| Switch Hostname |\n")
                    f.write("|-----------------|\n")
                    for switch in switch_list:
                        f.write(f"| {switch} |\n")
                    f.write("\n")
        print(f"Generated {os.path.join(docs_output_path, 'vrfs.md')}")

    # --- Generate networks.md ---
    if 'networks' in overlay_config:
        with open(os.path.join(docs_output_path, "networks.md"), 'w') as f:
            f.write("# Networks\n\n")
            for network in overlay_config['networks']:
                f.write(f"## {network.get('name', 'Unnamed Network')}\n\n")
                f.write("| Setting | Value |\n")
                f.write("|---------|-------|\n")
                for key, value in network.items():
                    f.write(f"| {key.replace('_', ' ').title()} | {value} |\n")
                f.write("\n")
                switch_list = get_network_attach_list(network.get('network_attach_group', ''), overlay_config)
                f.write(f"### Network Attached List\n\n")
                for switch in switch_list:
                    f.write("#### Switch: " + switch.get('hostname', '') + "\n\n")
                    for port in switch.get('ports', []):
                        f.write(f"- Port: {port}\n")
                    f.write("\n")
        print(f"Generated {os.path.join(docs_output_path, 'networks.md')}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate MkDocs documentation from a directory of NetAsCode VXLAN YAML files.")
    parser.add_argument("input_dir", help="Path to the directory containing YAML configuration files (e.g., config_files/).")
    parser.add_argument("--output_dir", default="docs", help="Directory to output MkDocs files (default: docs).")

    args = parser.parse_args()

    generate_mkdocs_from_nac_yaml_dir(args.input_dir, args.output_dir)
    print("\nDocumentation generation complete. To build and view the site:")
    print(f"1. Change directory to '{args.output_dir}'.")
    print(f"2. Run 'mkdocs serve' to preview locally.")
    print(f"3. Run 'mkdocs build' to generate static HTML files.")
