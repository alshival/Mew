# Mew - AI Assistant for Server Administrators

Mew is a lightweight AI assistant designed to help server administrators manage their systems efficiently. It leverages OpenAI's API to provide intelligent responses and actionable insights based on server-specific documentation.

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

Mew is an AI assistant tailored for server administrators. It reads and interprets documentation stored on your server to provide detailed responses and instructions based on the specific setup. Whether you're setting up a PostgreSQL database, configuring an NGINX server, or managing cron jobs, Mew can assist you by accessing and understanding the documentation you've provided.

## Features

- **Documentation-Aware**: Mew can access and understand server-specific documentation to answer questions accurately.
- **Command Execution**: Mew can run server commands directly, allowing for seamless automation of tasks.
- **Customizable**: Easily extend Mew's capabilities by adding more documentation or tools.

## Installation

### Prerequisites

- Ubuntu or Windows Subsystem for Linux (WSL)
- Python 3.x
- OpenAI API Key and Organization ID

### Installation Steps

1. Download the `.deb` package.
2. Install the package using:
   ```bash
   sudo dpkg -i mew-1.0-all.deb
   ```
3. Configure your OpenAI API credentials:
   ```bash
   mew-setup
   ```

## Usage

Once installed, you can start using Mew by running:

```bash
mew "How do I set up a new PostgreSQL user?"
```

Mew will read the relevant documentation and provide step-by-step instructions or run the necessary commands.

## Documentation Overview

Mew relies on the documentation stored in the `/usr/share/mew/Documentation/` directory. The `README.md` within this folder is required and provides Mew with context about your server. Within this file, you would describe the additional files on your server. There are some sample docs within the `Documentation` directory to get you started. You can create directories to organize your documentation as well and can edit them using your favorite markdown editor.

- **postgres.md**: Contains detailed information about a PostgreSQL instance, including setup instructions, configuration details, and user management. You can be as detailed as you wish.

- **alshidata.md**: Documents the setup of `alshidata`, a `Rust API` hosted by Alshival's Data Service, explaining how different components are integrated.

You can describe additional documents within the `/usr/share/mew/Documentation` folder. For example, 

- **nginx.md**: Provides guidelines for setting up and managing the NGINX web server, including configuration examples and common use cases.

- **cronjobs.md**: Lists scheduled cron jobs on the server, including their purpose and schedules.

You must provide a description of each documentation file within `Documentation/README.md`. Mew uses this structured documentation to provide accurate and context-aware assistance.

## Setup Script

Mew includes a setup script, `mew-setup`, that allows you to configure OpenAI API credentials and customize the text color for Mew's responses. The script can be run for the local user or globally for the team.

### Usage

To start the setup script, use the following commands:

- **User-Level Setup**: Configures Mew for the current user only. The configuration is stored in the `~/.mew.db` database within the user's home directory.
  ```bash
  mew-setup --user
  ```

- **Team-Level Setup**: Configures Mew for all users on the server. The configuration is stored in the `/usr/share/mew/mew.db` database. Running this setup requires elevated privileges.
  ```bash
  sudo mew-setup --team
  ```

### Commands

You can also use specific commands with `mew-setup` to manually set or repair your configuration:

- **Set OpenAI API Credentials**:
  - For the current user:
    ```bash
    mew-setup --user openai-api
    ```
  - For the team:
    ```bash
    sudo mew-setup --team openai-api
    ```

- **Set Text Color**:
  - For the current user:
    ```bash
    mew-setup --user text-color
    ```
  - For the team:
    ```bash
    sudo mew-setup --team text-color
    ```

### How It Works

- **Credential Lookup**: Mew first checks if credentials are defined within the user's database (`~/.mew.db`). If not, it will search for them in the team database (`/usr/share/mew/mew.db`). You can safely delete any of these databases to set up Mew from scratch.
  
- **Text Color Customization**: You can define a text color at both the user and team levels, which will change the color of Mew's responses in the terminal. Similar to the Credential Lookup, it prioritizes any user defined configuration before a team configuration.

### Help Command

For more information on the available options and commands, run:

```bash
mew-setup --help
```

This will display detailed usage instructions and a list of commands.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests. Please make sure to follow the contribution guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.