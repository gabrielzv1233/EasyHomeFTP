import os
allowed_directory = r".\ftp" #adding a perioud (.) before the slash of behid a folder name (looks like "./ftp") make the directory relitive to the current directory (ususally the main.py's file dir) (do note remove the "r" before the string, this tells python that the string is a raw string and should not take in count things like \n or \t)
def clear_console():
  if os.name == 'nt':  # for Windows
      os.system("cls")
  else:  # for Linux and macOS
      os.system("clear")
def replace_slash(dir):
  if os.name == 'nt':  # for Windows
    return dir.replace(r"/", "\\")
  else:  # for Linux and macOS
    return dir.replace("\\", "/")
try:
    from pathvalidate import sanitize_filename, sanitize_filepath
except ModuleNotFoundError:
    print("pathvalidate not installed, installing automatically\n")
    os.system("pip install pathvalidate")
    clear_console()
try:
    from flask import Flask, render_template, request, redirect, send_from_directory, current_app, abort, make_response
except ModuleNotFoundError:
    print("flask not installed, installing automatically\n")
    os.system("pip install flask")
    clear_console()
    try:
        from flask import Flask, render_template, request, redirect, send_from_directory, current_app, abort, make_response
    except ModuleNotFoundError:
        exit("flask installation failed, please run \"pip install flask\" in terminal")
allowed_directory = replace_slash(allowed_directory)
app = Flask(__name__)
raw_dir = os.path.abspath(allowed_directory)
if not os.path.exists(raw_dir):
    exit(f"Error: Directory \"{raw_dir}\" does not exist")
else:
  print(f"running at {os.path.abspath(raw_dir)}")
current_directory = allowed_directory

def get_files_and_directories(directory):
    items = os.listdir(directory)
    files = []
    directories = []
    for item in items:
        if os.path.isfile(os.path.join(directory, item)):
            files.append(item)
        else:
            directories.append(item)
    return files, directories

@app.route('/')
def file_explorer():
    # Replace the allowed_directory path with "HOME"
    censored_directory = current_directory.replace(allowed_directory, "HOME")

    files, directories = get_files_and_directories(current_directory)
    return render_template('file_explorer.html', current_directory=censored_directory, files=files, directories=directories)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        filename = file.filename
        sanitized_filename = sanitize_filename(filename)
        file_path = os.path.join(current_directory, sanitized_filename)
        if os.path.exists(file_path):
            print(f"File '{filename}' already exists, not uploading")
            return "File already exists on the server."
        else:
            file.save(file_path)
            print("File saved successfully!")
            return redirect('/')
    else:
        print("No file received.")
        return "No file received."

@app.route('/create_directory', methods=['POST'])
def create_directory():
    directory_name = request.form['directory_name']
    if directory_name:
        sanitized_directory_name = sanitize_filename(directory_name)
        directory_path = os.path.join(current_directory, sanitized_directory_name)
        if os.path.exists(directory_path):
            # Display a client-side JavaScript alert
            return "<script>alert('Directory already exists, please choose another directory.'); window.location.href='/';</script>"
        try:
            os.makedirs(directory_path)
        except Exception as e:
            print(f"Error creating directory: {str(e)}")
            return "Error creating directory."
    return redirect('/')

@app.route('/rename', methods=['POST'])
def rename_file_or_directory():
    item_name = request.form['item_name']
    new_name = request.form['new_name']
    if item_name and new_name:
        sanitized_new_name = sanitize_filename(new_name)
        try:
            os.rename(os.path.join(current_directory, item_name), os.path.join(current_directory, sanitized_new_name))
        except Exception as e:
            print(f"Error renaming file or directory: {str(e)}")
            return "<script>alert('Error renaming file or directory:\n{str(e)}'); window.location.href='/';</script>"
    return redirect('/')

@app.route('/delete', methods=['POST'])
def delete_file_or_directory():
    item_name = request.form['item_name']
    if item_name:
        path = os.path.join(current_directory, item_name)
        if os.path.isfile(path):
            os.remove(path)
        else:
            os.rmdir(path)
    return redirect('/')

@app.route('/change_directory', methods=['POST'])
def change_directory():
    global current_directory
    directory_name = request.form['directory_name']
    if directory_name == '..':
        if current_directory != allowed_directory:
            current_directory = os.path.dirname(current_directory)
    else:
        directory_path = os.path.join(current_directory, directory_name)
        if os.path.isdir(directory_path):
            current_directory = directory_path

    # Replace the allowed_directory path with "HOME" in the new current_directory
    censored_directory = current_directory.replace(allowed_directory, "HOME")

    return redirect('/')

    # Replace the allowed_directory path with "HOME" in the new current_directory
    censored_directory = current_directory.replace(allowed_directory, "HOME")

@app.route('/download/<path:filename>')
def download_file(filename):
    # Get the file extension
    file_extension = filename.rsplit('.', 1)[-1].lower()

    # Define the allowed file types to open in a new tab
    #https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
    newtab_types = ['jpg', 'jpeg', 'png', 'gif', 'txt', 'mp3', 'wav', 'mp4', 'avi', 'html', 'm4a', 'webp']

    # Check if the file extension is in the allowed types
    if file_extension in newtab_types:
        # Get the file path
        file_path = os.path.join(current_directory, filename)

        # Try to open the file
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()

            # Create a response with appropriate content type
            response = make_response(file_content)
            
            if file_extension in ['jpg', 'jpeg', 'png', 'gif']:
                content_type = f'image/{file_extension}'
            elif file_extension in ['mp3', 'wav']:
                content_type = f'audio/{file_extension}'
            elif file_extension in ['mp4', 'avi', 'm4a', 'webp']:
                content_type = f'video/{file_extension}'
            elif file_extension == 'html':
                content_type = 'text/html'
            else:
                content_type = 'text/plain'
            
            response.headers['Content-Type'] = content_type

            # Open the file in a new tab
            response.headers['Content-Disposition'] = 'inline'

            return response
        except FileNotFoundError:
            abort(404)
    else:
        # If the file extension is not in the allowed types, download the file
        return send_from_directory(current_directory, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
