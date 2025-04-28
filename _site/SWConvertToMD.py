import subprocess
import os
import pandas as pd
import yaml
import argparse


# Function to convert document using pandoc
def convert_to_markdown(input_file, output_dir):
    output_file = os.path.join(output_dir, os.path.splitext(os.path.basename(input_file))[0] + ".md")

    try:
        result = subprocess.run(
            ['pandoc', input_file, '-o', output_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            print(f"Converted: {os.path.basename(input_file)}")
            return output_file
        else:
            print(f"Failed to convert {os.path.basename(input_file)}: {result.stderr.strip()}")
            return None
    except Exception as e:
        print(f"Error converting {os.path.basename(input_file)}: {e}")
        return None


# Function to generate minimal YAML metadata for Jekyll
def generate_yaml_metadata(row):
    # Create the metadata dictionary in the desired order
    metadata_dict = {
        'layout': 'post',  # Default layout for Jekyll
        'title': row['Title of Doc'],  # Document title from spreadsheet
        'permalink': os.path.splitext(row['File Name'])[0],  # Permalink (use filename without extension)
        'last_name': row['Last Name'],
        'first_name': row['First Name'],
        'email': row['Email'],
        'institution': row['Institution'],
        'title_of_doc': row['Title of Doc'],
        'file_name': row['File Name'],
        'original_doc_type': row['Original Doc Type'],
        'primary_discipline': row['Primary Discpline'],
        'url': row['URL'],
    }

    # Convert the dictionary to YAML format in the specified order
    yaml_metadata = yaml.dump(metadata_dict, default_flow_style=False, sort_keys=False)

    # Add comments if any are provided in the spreadsheet
    comments = row['Comments']
    if pd.notna(comments):
        comment_lines = [f"# {line}" for line in comments.splitlines()]
        comments_yaml = "\n".join(comment_lines)
        yaml_metadata += "\n" + comments_yaml

    return yaml_metadata


# Combine YAML metadata with markdown content
def combine_yaml_with_markdown(yaml_content, markdown_content):
    return f"---\n{yaml_content}\n---\n{markdown_content}"


# Main processing function
def process_files(source_dir, output_docs_dir, output_yamls_dir, spreadsheet_file):
    os.makedirs(output_docs_dir, exist_ok=True)
    os.makedirs(output_yamls_dir, exist_ok=True)

    df = pd.read_excel(spreadsheet_file)

    for index, row in df.iterrows():
        filename = row['File Name']
        if pd.isna(filename) or not isinstance(filename, str) or filename.strip() == '':
            print(f"Warning: Invalid or missing filename in row {index}, skipping file.")
            continue

        input_file = os.path.join(source_dir, filename)
        if not os.path.exists(input_file):
            print(f"Warning: File {filename} not found in source directory.")
            continue

        markdown_file = convert_to_markdown(input_file, output_docs_dir)
        if not markdown_file:
            continue  # Skip to the next file if conversion failed

        # Generate the YAML metadata, including Jekyll front matter
        yaml_content = generate_yaml_metadata(row)

        # Read the generated markdown file
        with open(markdown_file, 'r') as f:
            markdown_content = f.read()

        # Combine the existing YAML metadata with the markdown content
        combined_content = combine_yaml_with_markdown(yaml_content, markdown_content)

        # Write the combined content back to the markdown file in the output_docs_dir
        with open(markdown_file, 'w') as f:
            f.write(combined_content)

        # Save the YAML metadata to a separate file in the output_yamls_dir
        yaml_filename = os.path.splitext(filename)[0] + ".yaml"
        yaml_file_path = os.path.join(output_yamls_dir, yaml_filename)
        with open(yaml_file_path, 'w') as yaml_file:
            yaml.dump(yaml.safe_load(yaml_content), yaml_file)

        print(f"Processed {filename}: Markdown saved to {markdown_file}, YAML saved to {yaml_file_path}")


# Entry point
if __name__ == "__main__":
    current_directory = os.getcwd()

    parser = argparse.ArgumentParser(description="Convert documents to Markdown and extract metadata to YAML.")

    parser.add_argument('--source', default=os.path.join(current_directory, "source"),
                        help="Path to the source folder (default: ./source)")
    parser.add_argument('--output-docs', default=os.path.join(current_directory, "output_documents"),
                        help="Path to output markdown folder (default: ./output_documents)")
    parser.add_argument('--output-yamls', default=os.path.join(current_directory, "output_yamls"),
                        help="Path to output YAML folder (default: ./output_yamls)")
    parser.add_argument('--spreadsheet', default=os.path.join(current_directory, "metadata.xlsx"),
                        help="Path to metadata spreadsheet (default: ./metadata.xlsx)")

    args = parser.parse_args()

    process_files(args.source, args.output_docs, args.output_yamls, args.spreadsheet)
