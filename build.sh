# Uninstall the old package if it exists
sudo dpkg -r mew

# Extract package information from the control file
PACKAGE_NAME=$(grep '^Package:' build/DEBIAN/control | awk '{print $2}' | tr -d '\r')
VERSION=$(grep '^Version:' build/DEBIAN/control | awk '{print $2}' | tr -d '\r')
ARCHITECTURE=$(grep '^Architecture:' build/DEBIAN/control | awk '{print $2}' | tr -d '\r')

# Construct the package filename
PACKAGE_FILENAME="${PACKAGE_NAME}-${VERSION}-${ARCHITECTURE}.deb"

# Remove any existing .deb files
rm -f ./*.deb

# Remove dos text. (For when developing on WSL)
sudo dos2unix build/usr/share/mew/mew.py
sudo dos2unix build/usr/share/mew/mew_setup.py

# Remove any existing virtual environments
rm -rf build/usr/share/mew/mew-env

# Create a fresh virtual environment
mkdir -p build/usr/share/mew/mew-env
python3 -m venv build/usr/share/mew/mew-env 

# Install python dependencies
build/usr/share/mew/mew-env/bin/pip3 install -r build/usr/share/mew/requirements.txt

# (Re)create symbolic links
rm build/usr/bin/mew
ln -s /usr/share/mew/mew.py build/usr/bin/mew
rm build/usr/bin/mew-setup
ln -s /usr/share/mew/mew_setup.py build/usr/bin/mew-setup

# Build the .deb package from the `build` directory
dpkg-deb --build build ./${PACKAGE_FILENAME}

# Clean up old databases if they exist
if [ -f ~/.mew.db ]; then
    sudo rm ~/.mew.db
fi

if [ -f /usr/share/mew/mew.db ]; then
    sudo rm /usr/share/mew/mew.db
fi

# Install the new package
sudo dpkg -i ${PACKAGE_FILENAME}
