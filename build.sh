# Uninstall the old package if it exists
sudo dpkg -r mewtwo

# Extract package information from the control file
PACKAGE_NAME=$(grep '^Package:' build/DEBIAN/control | awk '{print $2}' | tr -d '\r')
VERSION=$(grep '^Version:' build/DEBIAN/control | awk '{print $2}' | tr -d '\r')
ARCHITECTURE=$(grep '^Architecture:' build/DEBIAN/control | awk '{print $2}' | tr -d '\r')

# Construct the package filename
PACKAGE_FILENAME="${PACKAGE_NAME}-${VERSION}-${ARCHITECTURE}.deb"

# Generate README.md from README.txt
sed "s/<VERSION>/${VERSION}/g" README.txt > README.md

# Remove any existing .deb files
rm -f ./*.deb

# Copy the README.md over as sample documentation
rm build/usr/share/mewtwo/Documentation/README.md
cp README.md build/usr/share/mewtwo/Documentation

# Remove dos text. (For when developing on WSL)
sudo dos2unix build/usr/share/mewtwo/mewtwo.py
sudo dos2unix build/usr/share/mewtwo/mewtwo_setup.py
sudo dos2unix build/usr/share/mewtwo/RAG/rag.py
sudo dos2unix build/usr/share/mewtwo/RAG/monitorDocs.py

# Remove any existing virtual environments
rm -rf build/usr/share/mewtwo/mewtwo-env

# Create a fresh virtual environment
mkdir -p build/usr/share/mewtwo/mewtwo-env
python3 -m venv build/usr/share/mewtwo/mewtwo-env 

# Install python dependencies
build/usr/share/mewtwo/mewtwo-env/bin/pip3 install -r build/usr/share/mewtwo/requirements.txt

# (Re)create symbolic links
rm build/usr/bin/mewtwo
ln -s /usr/share/mewtwo/mewtwo.py build/usr/bin/mewtwo
rm build/usr/bin/mewtwo-setup
ln -s /usr/share/mewtwo/mewtwo_setup.py build/usr/bin/mewtwo-setup

# Build the .deb package from the `build` directory
dpkg-deb --build build ./${PACKAGE_FILENAME}

# Clean up old databases if they exist
if [ -f ~/.mewtwo.db ]; then
    sudo rm ~/.mewtwo.db
fi

if [ -f /usr/share/mewtwo/mewtwo.db ]; then
    sudo rm /usr/share/mewtwo/mewtwo.db
fi

# Install the new package
sudo dpkg -i ${PACKAGE_FILENAME}
