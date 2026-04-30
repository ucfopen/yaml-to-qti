import logging
import os
import tempfile
import traceback
import zipfile
from shutil import rmtree

from flask import (
    Flask,
    after_this_request,
    jsonify,
    render_template,
    request,
    send_from_directory,
)

from app.create_imscc import main as main_converter

flask_app = Flask(__name__)

if os.environ.get("SCRIPT_NAME"):
    flask_app.config["APPLICATION_ROOT"] = os.environ.get("SCRIPT_NAME")

app_dir = os.path.dirname(os.path.abspath(__file__))

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)

flask_app.logger.addHandler(handler)
flask_app.logger.setLevel(logging.INFO)


def get_temp_dir():
    temporary_file = tempfile.NamedTemporaryFile(dir=os.path.join(app_dir, "tmp"))

    if os.path.isfile(temporary_file.name):
        temporary_file.close()
    os.mkdir(temporary_file.name)
    if os.path.isdir(temporary_file.name):
        if temporary_file.name[-1] != "/":
            return f"{temporary_file.name}/"
        return temporary_file.name
    return None


def get_media_dir(media_path):
    media_subdirs = [f.path for f in os.scandir(media_path) if f.is_dir()]
    if len(media_subdirs) < 1:
        return media_path

    if len(media_subdirs) > 1:
        pass  # TODO: error handling
    else:
        media_path = media_subdirs[0]
    return media_path


def get_yaml_path(parent_path):
    files = os.listdir(parent_path)
    for file in files:
        if os.path.splitext(file)[1] in [".yml", ".yaml"]:
            return os.path.join(parent_path, file)
    return None


@flask_app.route("/", methods=["GET"])
def index():
    return render_template("main.html")


@flask_app.route("/upload", methods=["POST"])
def upload():
    shuffle_mult = request.form.get("shuffle", False) == "true"

    if len(request.files) > 0:
        filename = list(request.files.keys())[0]
        file = request.files[filename]
        uploaded_filename = file.filename

        temp_storage_path = get_temp_dir()
        # directory to which media files are written
        final_image_path = None

        if file.content_type == "application/x-yaml":
            main_file_path = os.path.join(temp_storage_path, f"{filename}.yml")
            file.save(main_file_path)
        elif (
            file.content_type == "application/zip"
            or file.content_type == "application/x-zip-compressed"
        ):
            main_file_path = os.path.join(temp_storage_path, f"{filename}.zip")
            file.save(main_file_path)
            with zipfile.ZipFile(main_file_path, "r") as main_zip:
                main_zip.extractall(temp_storage_path)
            os.remove(main_file_path)
            # TODO: handle this not returning something usable
            main_file_path = get_yaml_path(temp_storage_path)
            final_image_path = get_media_dir(temp_storage_path)
        elif file.content_type == "application/octet-stream":
            file_extension = file.filename.split(".")[-1]
            # TODO: define a function we can run here and above in the normal YAML detection area
            if file_extension == "yml" or file_extension == "yaml":
                main_file_path = os.path.join(temp_storage_path, f"{filename}.yml")
                file.save(main_file_path)
        else:
            return jsonify(message=f"Unrecognized file type {file.content_type}"), 500

        # if a media file was uploaded separately, unzip its contents
        if len(request.files) > 1:
            media_filename = list(request.files.keys())[1]
            media_file = request.files[media_filename]
            media_file_path = os.path.join(temp_storage_path, f"{media_filename}.zip")
            media_file.save(media_file_path)
            final_image_path = os.path.join(temp_storage_path, "extracted_media")
            with zipfile.ZipFile(media_file_path, "r") as media_zip:
                media_zip.extractall(final_image_path)
            os.remove(media_file_path)
            get_media_dir(final_image_path)

        if final_image_path == temp_storage_path or not final_image_path:
            final_image_path = "n"

        try:
            main_converter(
                main_file_path,
                final_image_path,
                shuffle_mult,
                os.path.join(temp_storage_path, "output"),
                True,
            )
        except Exception as e:
            flask_app.logger.error(traceback.format_exc())
            # in the event of an error, remove non-viable temporary files
            rmtree(temp_storage_path)
            # allow the front end to handle error presentation
            return jsonify(message=str(e)), 500

        temp_folder = os.path.basename(os.path.normpath(temp_storage_path))

        with open(os.path.join(temp_storage_path, "output", "filename"), "w") as f:
            f.write(uploaded_filename)

        return jsonify(id=temp_folder), 200
    else:
        flask_app.logger.info("No files provided - handle this error more gracefully")
        return "need better error messages", 500


@flask_app.route("/download/<download_id>", methods=["GET"])
def download(download_id):
    app_dir = os.path.dirname(os.path.abspath(__file__))
    download_path = os.path.join(app_dir, "tmp", download_id, "output")

    filename = ""
    with open(os.path.join(download_path, "filename"), "r") as f:
        filename = os.path.splitext(f.read())[0]

    @after_this_request
    def cleanup(response):
        cleanup_path = os.path.join(app_dir, "tmp", download_id)
        rmtree(cleanup_path)
        return response

    return send_from_directory(
        download_path, "import.zip", as_attachment=True, download_name=filename + ".zip"
    )
