import json

def read_file_to_string(file_path):
    """
    Reads the entire content of a file into a single string.
    
    Args:
        file_path (str): Path to the file.
        
    Returns:
        str: The content of the file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        # This error is now very important, as we expect the file to exist!
        raise FileNotFoundError(f"Your file was not found at: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading file: {str(e)}")

# --- Main execution block ---
if __name__ == "__main__":
    # Define the path to YOUR existing HTML file
    your_html_file = 'example.html'

    print(f"Reading content from '{your_html_file}'...")
    
    # 1. Read YOUR HTML file into a plain Python string.
    html_content_string = read_file_to_string(your_html_file)
    
    # 2. Create the Python dictionary with your HTML content.
    output_data = {
        "id": 1,
        "name": "Seed From My HTML",
        "html_content": html_content_string, # The raw string from your file
        "source_file": your_html_file
    }
    
    # 3. Let json.dump handle all the escaping and save to a file.
    output_json_file = 'output.json'
    with open(output_json_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4)
    
    print(f"✅ Success! Your HTML has been correctly saved to '{output_json_file}'")