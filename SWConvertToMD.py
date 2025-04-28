import subprocess
import os
import pandas as pd
import yaml


# Function to convert document using pandoc
def convert_to_markdown(input_file, output_dir):
    # Create the output file path by changing the file extension to .md
    output_file = os.path.join(output_dir, os.path.splitext(os.path.basename(input_file))[0] + ".md")

    # Run the pandoc command to convert to markdown
    subprocess.run(['pandoc', input_file, '-o', output_file])

    return output_file


# Function to generate YAML metadata from the spreadsheet
def generate_yaml_metadata(row):
    metadata_dict = {
        'last_name': row['Last Name'],
        'first_name': row['First Name'],
        'email': row['Email'],
        'institution': row['Institution'],
        'title_of_doc': row['Title of Doc'],
        'file_name': row['File Name'],  # Added File Name column
        'original_doc_type': row['Original Doc Type'],
        'primary_discipline': row['Primary Discpline'],
        'url': row['URL'],
    }

    # Generate the YAML metadata string from the dictionary
    yaml_metadata = yaml.dump(metadata_dict, default_flow_style=False)

    # Add comments from the 'Comments' field as YAML comments
    comments = row['Comments']
    if pd.notna(comments):  # Check if there are comments
        # Split the comments into lines and format them as YAML comments
        comment_lines = [f"# {line}" for line in comments.splitlines()]
        comments_yaml = "\n".join(comment_lines)
        # Append the comments at the end of the YAML block
        yaml_metadata += "\n" + comments_yaml

    return yaml_metadata


# Function to combine YAML metadata with markdown content
def combine_yaml_with_markdown(yaml_content, markdown_content):
    return f"---\n{yaml_content}\n---\n{markdown_content}"


# Main function to process all files in the "source" folder
def process_files(source_dir, output_docs_dir, output_yamls_dir, spreadsheet_file):
    # Ensure the output directories exist
    if not os.path.exists(output_docs_dir):
        os.makedirs(output_docs_dir)

    if not os.path.exists(output_yamls_dir):
        os.makedirs(output_yamls_dir)

    # Read the spreadsheet
    df = pd.read_excel(spreadsheet_file)

    # Loop through all files in the source directory
    for index, row in df.iterrows():
        # Extract the filename from the spreadsheet row using 'File Name' column to match the file
        filename = row['File Name']

        # Check if 'filename' is valid (not NaN, empty, or a non-string type)
        if pd.isna(filename) or not isinstance(filename, str) or filename.strip() == '':
            print(f"Warning: Invalid or missing filename in row {index}, skipping file.")
            continue

        # Ensure the full path to the file
        input_file = os.path.join(source_dir, filename)

        # Skip if the file doesn't exist in the source directory
        if not os.path.exists(input_file):
            print(f"Warning: File {filename} not found in source directory.")
            continue

        # Convert the document to markdown
        try:
            markdown_file = convert_to_markdown(input_file, output_docs_dir)
        except Exception as e:
            print(f"Error converting {filename}: {e}")
            continue

        # Generate YAML metadata from the spreadsheet row
        yaml_content = generate_yaml_metadata(row)

        # Read the generated markdown file
        with open(markdown_file, 'r') as f:
            markdown_content = f.read()

        # Combine YAML metadata with markdown content
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


# Example usage
if __name__ == "__main__":
    current_directory = os.getcwd()  # Get the current directory where the script is located
    source_directory = os.path.join(current_directory, "source")  # Path to the source folder
    output_documents_directory = os.path.join(current_directory,
                                              "output_documents")  # Path to the documents output folder
    output_yamls_directory = os.path.join(current_directory, "output_yamls")  # Path to the YAML output folder
    spreadsheet_file = os.path.join(current_directory, "metadata.xlsx")  # Path to the spreadsheet containing metadata

    # Process all files in the source folder
    process_files(source_directory, output_documents_directory, output_yamls_directory, spreadsheet_file)
