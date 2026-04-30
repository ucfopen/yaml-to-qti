import os
import shutil
import zipfile

from app.build_imscc import build_imscc
from app.yaml_to_qti import yaml_to_qti


def validate_yaml_for_images(yaml_file):
    """Check if the YAML file contains no 'figure:' term or all 'figure:' terms are empty."""
    with open(yaml_file, "r") as file:
        content = file.read()
        if "figure:" not in content:
            return True
        # Check if all 'figure:' terms are empty
        lines = content.splitlines()
        for line in lines:
            if line.strip().startswith("figure:") and line.strip() != "figure:":
                return False
        return True


def main(
    yaml_file=None,
    image_folder=None,
    shuffle_mult=False,
    output_folder=None,
    overwrite_output=False,
):
    # Get user input for project details

    if not yaml_file:
        yaml_file = input("Enter the path to the YAML file: ").strip()
    default_image_folder = os.path.splitext(yaml_file)[0] + "-Figures"
    default_output_folder = os.path.splitext(yaml_file)[0] + "_unzipped"

    if not image_folder:
        image_folder = input(
            f"Enter the path to the image folder (or 'n' if not needed, default: {default_image_folder}): "
        ).strip()
    if image_folder.lower() == "n":
        if validate_yaml_for_images(yaml_file):
            image_folder = None
            print("No image files are associated with the problems in the bank.")
        else:
            print(
                "Error: The YAML file contains non-empty 'figure:' terms. An image folder path is required."
            )
            return
    elif not image_folder:
        if validate_yaml_for_images(yaml_file):
            image_folder = None
            print("No image files are associated with the problems in the bank.")
        else:
            image_folder = default_image_folder

    if not output_folder:
        output_folder = (
            input(
                f"Enter the output folder for the IMSCC package (default: {default_output_folder}): "
            ).strip()
            or default_output_folder
        )

    # Check if output folder exists
    if os.path.exists(output_folder):
        if not overwrite_output:
            overwrite = (
                input(
                    f"The folder '{output_folder}' already exists. Do you want to overwrite its contents? (y/n): "
                )
                .strip()
                .lower()
            )
        if overwrite != "y":
            print("Operation cancelled.")
            return
        else:
            shutil.rmtree(output_folder)

    # Validate inputs
    if not os.path.isfile(yaml_file):
        print(f"Error: YAML file '{yaml_file}' does not exist.")
        return

    if image_folder and not os.path.isdir(image_folder):
        print(f"Error: Image folder '{image_folder}' does not exist.")
        return

    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(os.path.join(output_folder, "qti"))

    # create the manifest file and relocate all media files
    print("Running build_imscc...")
    try:
        build_imscc(image_folder, output_folder)
    except Exception as e:
        raise e

    # parse the YAML input and generate the appropriate QTI XML
    print("Running yaml_to_qti...")
    yaml_to_qti(yaml_file, shuffle_mult, output_folder)

    zip_path = os.path.join(output_folder, "import.zip")

    # Aggregate media files
    all_media = []
    media_dir = os.path.join(output_folder, "media")

    if os.path.exists(media_dir):
        for filename in os.listdir(media_dir):
            full_path = os.path.join(output_folder, "media", filename)
            relative_path = f"media/{filename}"
            all_media.append((full_path, relative_path))

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.write(
            os.path.join(output_folder, "imsmanifest.xml"), "imsmanifest.xml"
        )
        zip_file.write(os.path.join(output_folder, "qti"), "qti")
        zip_file.write(os.path.join(output_folder, "qti", "qti.xml"), "qti/qti.xml")
        if len(all_media) > 0:
            for media in all_media:
                zip_file.write(media[0], media[1])

    print(f"IMSCC package created successfully in '{output_folder}'.")


if __name__ == "__main__":
    main()
