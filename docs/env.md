# Environment Variable Management with `.env` Files

This Ansible project leverages `.env` files to manage configuration variables across different environments (e.g., development, staging, and production). This approach promotes security and flexibility by separating environment-specific settings and sensitive data from the core automation code.

## How It Works

The `Taskfile.yml` is configured to load variables from `.env` files using the `dotenv` directive. It first loads a common `.env` file and then an environment-specific file (e.g., `.env-dev`), allowing for overrides.

```yaml
# From Taskfile.yml
dotenv: [ '.env', '.env-{{.ENV}}']
```

Variables are injected into Ansible through the inventory files (e.g., `inventory/dev/hosts.yml`), which use the `lookup` filter to read values from the environment:

```yaml
# Example from inventory/prod/hosts.yml
ansible_user: "{{ lookup('env', 'ANSIBLE_USER') | default('ansible', true) }}"
ansible_ssh_private_key_file: "{{ lookup('env', 'SSH_PRIVATE_KEY') | default('~/.ssh/id_rsa', true) }}"
```

## File Structure and Precedence

You'll need to create the `.env` files in the root directory of the project. They will not be committed to version control, as they are listed in the `.gitignore` file.

1.  `.env`: Use this file for variables common to all environments or for local development overrides. It is loaded first.
2.  `.env.<environment>`: (e.g., `.env.dev`, `.env.stage`, `.env.prod`). These files contain variables specific to a particular environment. They are loaded *after* the base `.env` file, so any variables defined here will **override** values from `.env`.

## Usage

To execute tasks for a specific environment, set the `ENV` variable when calling `task`. If `ENV` is not specified, it defaults to `dev`.

```bash
# Deploy to the development workstation
task deploy-workstation ENV=dev

# Deploy to the production servers
task deploy-server ENV=prod
```

## Configuration Templates

Below are templates for the `.env` files. Copy these examples into your project root and replace the placeholder values with your actual settings.

### Common/Local `.env` file

This file can contain default values or settings for a local-only setup.

```sh
# .env (Common or local-only settings)

# Default Ansible user for local connections
ANSIBLE_USER=local_user

# Default SSH key for local connections
SSH_PRIVATE_KEY=~/.ssh/id_rsa

# Default domain for local machines
DOMAIN=local
```

### Development `.env.dev` file

Based on `inventory/dev/hosts.yml`.

```sh
# .env.dev (Development environment settings)

# Ansible user for the dev environment
ANSIBLE_USER=dev_user
SSH_PRIVATE_KEY=~/.ssh/dev_key

# Hostname and domain settings
HOSTNAME_PREFIX=dev-penguin
DOMAIN=dev.lan
WORKSTATION_HOSTNAME_PREFIX=workstation-dev
SERVER_HOSTNAME_PREFIX=server-dev

# Default user to create on target machines
DEFAULT_USER=dev_foo
ADDITIONAL_GROUP=developers

# IP Addresses for dev machines
DEV_WORKSTATION_IP=192.168.1.10
DEV_SERVER_IP=192.168.1.11
```

### Staging `.env.stage` file

Based on `inventory/stage/hosts.yml`.

```sh
# .env.stage (Staging environment settings)

# Ansible user for the stage environment
ANSIBLE_USER=stage_user
SSH_PRIVATE_KEY=~/.ssh/stage_key

# Hostname and domain settings
HOSTNAME_PREFIX=stage-penguin
DOMAIN=stage.lan

# Default user to create on target machines
DEFAULT_USER=stage_foo
ADDITIONAL_GROUP=testers

# IP Addresses for stage machines
STAGE_WORKSTATION_IP=10.0.0.10
STAGE_SERVER_IP=10.0.0.11
```

### Production `.env.prod` file

Based on `inventory/prod/hosts.yml`.

```sh
# .env.prod (Production environment settings)

# Ansible user for the prod environment
ANSIBLE_USER=prod_user
SSH_PRIVATE_KEY=~/.ssh/prod_key

# Hostname and domain settings
HOSTNAME_PREFIX=penguin
DOMAIN=prod.lan

# Default user to create on target machines
DEFAULT_USER=prod_foo
ADDITIONAL_GROUP=users

# IP Addresses for production machines
PROD_WORKSTATION1_IP=172.16.0.10
PROD_WORKSTATION2_IP=172.16.0.11
PROD_SERVER1_IP=172.16.0.20
PROD_SERVER2_IP=172.16.0.21
```

### Molecule Testing

The Molecule testing framework also uses environment variables, which are defined in `roles/base-system/molecule/default/molecule.yml`. These are typically set by Molecule during its execution cycle. If you need to run Molecule steps manually, you might need to export these variables in your shell or create a temporary `.env.molecule` file.
