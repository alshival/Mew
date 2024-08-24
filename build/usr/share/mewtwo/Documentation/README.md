# Mewtwo - AI Assistant for Server Administrators

Mewtwo is a lightweight AI assistant designed to help server administrators manage their systems efficiently. It leverages OpenAI's API to provide intelligent responses and actionable insights based on server-specific documentation.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Installation Steps](#installation-steps)
- [Usage](#usage)
- [Documentation Overview](#documentation-overview)
- [Setup Script](#setup-script)
  - [Usage](#usage-1)
  - [Commands](#commands)
  - [How It Works](#how-it-works)
  - [Help Command](#help-command)
- [Contributing](#contributing)
- [License](#license)

## Introduction

Mewtwo is an AI assistant tailored for server administrators. It reads and interprets documentation stored on your server to provide detailed responses and instructions based on the specific setup. Whether you're setting up a PostgreSQL database, configuring an NGINX server, or managing cron jobs, Mewtwo can assist you by accessing and understanding the documentation you've provided.

## Features

- **Documentation-Aware**: Mewtwo can access and understand server-specific documentation to answer questions accurately.
- **Command Execution**: Mewtwo can run server commands directly, allowing for seamless automation of tasks.
- **Customizable**: Easily extend Mewtwo's capabilities by adding more documentation or tools.

## Installation

### Prerequisites

- Ubuntu or Windows Subsystem for Linux (WSL)
- Python 3.x
- OpenAI API Key and Organization ID

### Installation Steps

1. Download the `.deb` package.
2. Install the package using:
   ```bash
   sudo dpkg -i mewtwo-1.0-all.deb
   ```
3. Configure your OpenAI API credentials:
   ```bash
   mewtwo-setup
   ```

## Usage

Once installed, you can start using Mewtwo by running:

```bash
mewtwo "How do I set up a new PostgreSQL user?"
```

Mewtwo will read the relevant documentation and provide step-by-step instructions or run the necessary commands.

## Documentation Overview

By default, Mewtwo's algorithm searches through documentation stored in the `/usr/share/mewtwo/Documentation/` directory. You can change this using `mewtwo-setup doc-directory`. When updating documentation, it is important to run `mewtwo-setup rag` to update the search algorithm. You could use github to track your documentation and point mew to it, for example. Sample documentation is provided in the default directory. You can delete the files or change the documentation directory and they will be removed from the vector database used for retrieval-augmented generation.

- **postgres.md**: Contains detailed information about a PostgreSQL instance, including setup instructions, configuration details, and user management. You can be as detailed as you wish.

- **alshidata.md**: Documents the setup of `alshidata`, a `Rust API` hosted by Alshival's Data Service, explaining how different components are integrated.

## Setup Script

Mewtwo includes a setup script, `mewtwo-setup`, that allows you to configure OpenAI API credentials, customize the text color for Mewtwo's responses, set the documentation directory, and update the sudo password used by Mewtwo. The script can be run for the local user or globally for the team.

### Usage

To start the setup script, use the following commands:

- **User-Level Setup**: Configures Mewtwo for the current user only. The configuration is stored in the `~/.mewtwo.db` database within the user's home directory.
  ```bash
  mewtwo-setup --user
  ```

- **Team-Level Setup**: Configures Mewtwo for all users on the server. The configuration is stored in the `/usr/share/mewtwo/mewtwo.db` database. Running this setup requires elevated privileges.
  ```bash
  sudo mewtwo-setup --team
  ```

### Commands

You can also use specific commands with `mewtwo-setup` to manually set or repair your configuration:

- **Set Documentation Directory**: Set the directory containing your server's documentation.
  - For the current user:
    ```bash
    mewtwo-setup --user doc-directory
    ```
  - For the team:
    ```bash
    sudo mewtwo-setup --team doc-directory
    ```

- **Set OpenAI API Credentials**: Set the OpenAI API key and Organization ID.
  - For the current user:
    ```bash
    mewtwo-setup --user openai-api
    ```
  - For the team:
    ```bash
    sudo mewtwo-setup --team openai-api
    ```

- **Set Text Color**: Choose and set the text color for Mewtwo's responses.
  - For the current user:
    ```bash
    mewtwo-setup --user text-color
    ```
  - For the team:
    ```bash
    sudo mewtwo-setup --team text-color
    ```

- **Update Sudo Password**: Update the sudo password used by Mewtwo.
  - For the current user:
    ```bash
    mewtwo-setup --user sudo
    ```


- **Update Documentation Search Algorithm (RAG)**: After updating documentation, run this command to update Mewtwo's vector database for searching through documentation (requires sudo)
  - For the team:
    ```bash
    sudo mewtwo-setup --team rag
    ```

- **Wipe Memory**: Clear Mewtwo's chat history.
  - For the current user:
    ```bash
    mewtwo-setup --user wipe-memory
    ```
Chat history is stored within a user's database. No chats are stored within the team database. 

### How It Works

- **Credential Lookup**: Mewtwo first checks if credentials are defined within the user's database (`~/.mewtwo.db`). If not, it will search for them in the team database (`/usr/share/mewtwo/mewtwo.db`). You can safely delete any of these databases to set up Mewtwo from scratch.

- **Text Color Customization**: You can define a text color at both the user and team levels, which will change the color of Mewtwo's responses in the terminal. Similar to the Credential Lookup, it prioritizes any user-defined configuration before a team configuration.

- **Documentation Directory**: You can specify a custom directory for your server's documentation. By default, Mewtwo will look in `/usr/share/mewtwo/Documentation`, but you can change this with the `doc-directory` command.

- **Sudo Password**: Mewtwo can use a sudo password for executing privileged commands. This should be defined at the user level since every user's sudo password will vary.

- **Updating Documentation Search Algorithm**: After making changes to your documentation, run `mewtwo-setup rag` to update Mewtwo's search algorithm and ensure that the assistant can access the latest information.

### Help Command

For more information on the available options and commands, run:

```bash
mewtwo-setup --help
```

This will display detailed usage instructions and a list of commands.

# TO-DO
Implement RAG to provide context across different documenation. 

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests. Please make sure to follow the contribution guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.