import os
from flask import Flask, render_template, request, redirect, send_from_directory

app = Flask(__name__)
allowed_directory = r".\ftp"
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
        file_path = os.path.join(current_directory, filename)
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
        os.makedirs(os.path.join(current_directory, directory_name))
    return redirect('/')

@app.route('/rename', methods=['POST'])
def rename_file_or_directory():
    item_name = request.form['item_name']
    new_name = request.form['new_name']
    if item_name and new_name:
        os.rename(os.path.join(current_directory, item_name), os.path.join(current_directory, new_name))
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

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(current_directory, filename, as_attachment=True)

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

if __name__ == '__main__':
    app.run()