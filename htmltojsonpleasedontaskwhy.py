import json

def html_file_to_json_string(html_file_path):
    """
    Read an HTML file and convert it to a JSON-safe string.
    
    Args:
        html_file_path (str): Path to the HTML file
        
    Returns:
        str: JSON-safe string that can be used in JSON objects
    """
    try:
        # Read the HTML file
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        # Use json.dumps to properly escape the string for JSON
        return json.dumps(html_content)[1:-1]  # Remove surrounding quotes
    
    except FileNotFoundError:
        raise FileNotFoundError(f"HTML file not found: {html_file_path}")
    except Exception as e:
        raise Exception(f"Error reading HTML file: {str(e)}")


# Example usage
if __name__ == "__main__":
    # Convert HTML file to JSON-safe string
    json_safe = html_file_to_json_string('example.html')
    print(json_safe)
    
    # Save to a JSON file
    output_data = {
        "html_content": json_safe,
        "source_file": "example.html"
    }
    
    with open('output.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
    
    print("\n✅ Saved to output.json")