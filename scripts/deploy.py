#!/usr/bin/env python3
"""
OpenWebUI Functions Deployment Script

This script deploys Python functions from the functions/ directory to an OpenWebUI instance.
It uses the OpenWebUI API to create or update functions.

Environment Variables Required:
- OPENWEBUI_URL: The base URL of your OpenWebUI instance (e.g., https://openwebui.example.com)
- OPENWEBUI_API_KEY: Your OpenWebUI API key

Usage:
    python deploy.py
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional
import re


class OpenWebUIDeployer:
    """Handles deployment of functions to OpenWebUI."""

    def __init__(self, base_url: str, api_key: str):
        """
        Initialize the deployer.

        Args:
            base_url: Base URL of OpenWebUI instance
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        self.log_file = 'deployment-log.txt'
        self.logs = []

    def log(self, message: str, level: str = 'INFO'):
        """Log a message to console and log file."""
        log_entry = f'[{level}] {message}'
        print(log_entry)
        self.logs.append(log_entry)

    def save_logs(self):
        """Save logs to file."""
        with open(self.log_file, 'w') as f:
            f.write('\n'.join(self.logs))

    def extract_function_metadata(self, file_path: Path) -> Optional[Dict]:
        """
        Extract function metadata from the Python file.

        Args:
            file_path: Path to the Python function file

        Returns:
            Dictionary with function metadata or None if extraction fails
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Extract class name (usually the main class in the file)
            class_match = re.search(r'class\s+(\w+)(?:\([^)]*\))?:', content)
            if not class_match:
                self.log(f'Could not find class definition in {file_path.name}', 'WARNING')
                return None

            class_name = class_match.group(1)

            # Try to extract metadata from class attributes
            # Look for id/name attributes in the class
            id_match = re.search(r'id\s*=\s*["\']([^"\']+)["\']', content)
            name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
            description_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', content)

            # Generate ID from filename if not found
            # OpenWebUI only allows alphanumeric characters and underscores
            if id_match:
                function_id = id_match.group(1)
            else:
                # Convert filename to valid ID
                function_id = file_path.stem

            # Sanitize the ID: replace hyphens with underscores
            # and remove any other non-alphanumeric characters except underscores
            function_id = function_id.replace('-', '_')
            function_id = re.sub(r'[^a-zA-Z0-9_]', '_', function_id)

            function_name = name_match.group(1) if name_match else class_name
            function_description = description_match.group(1) if description_match else f'Function from {file_path.name}'

            return {
                'id': function_id,
                'name': function_name,
                'description': function_description,
                'content': content,
                'meta': {
                    'manifest': {}
                }
            }

        except Exception as e:
            self.log(f'Error extracting metadata from {file_path.name}: {str(e)}', 'ERROR')
            return None

    def get_existing_functions(self) -> Dict[str, str]:
        """
        Get list of existing functions from OpenWebUI.

        Returns:
            Dictionary mapping function IDs to their internal IDs
        """
        try:
            response = requests.get(
                f'{self.base_url}/api/v1/functions/',
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()

            functions = response.json()
            return {func.get('id'): func.get('id') for func in functions}

        except requests.exceptions.RequestException as e:
            self.log(f'Error fetching existing functions: {str(e)}', 'ERROR')
            return {}

    def create_function(self, function_data: Dict) -> bool:
        """
        Create a new function in OpenWebUI.

        Args:
            function_data: Function metadata and content

        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.post(
                f'{self.base_url}/api/v1/functions/create',
                headers=self.headers,
                json=function_data,
                timeout=30
            )
            response.raise_for_status()
            self.log(f'Successfully created function: {function_data["id"]}', 'SUCCESS')
            return True

        except requests.exceptions.RequestException as e:
            self.log(f'Error creating function {function_data["id"]}: {str(e)}', 'ERROR')
            if hasattr(e.response, 'text'):
                self.log(f'Response: {e.response.text}', 'ERROR')
            return False

    def update_function(self, function_id: str, function_data: Dict) -> bool:
        """
        Update an existing function in OpenWebUI.

        Args:
            function_id: ID of the function to update
            function_data: Function metadata and content

        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.post(
                f'{self.base_url}/api/v1/functions/id/{function_id}/update',
                headers=self.headers,
                json=function_data,
                timeout=30
            )
            response.raise_for_status()
            self.log(f'Successfully updated function: {function_id}', 'SUCCESS')
            return True

        except requests.exceptions.RequestException as e:
            self.log(f'Error updating function {function_id}: {str(e)}', 'ERROR')
            if hasattr(e.response, 'text'):
                self.log(f'Response: {e.response.text}', 'ERROR')
            return False

    def deploy_function(self, file_path: Path, existing_functions: Dict[str, str]) -> bool:
        """
        Deploy a single function file to OpenWebUI.

        Args:
            file_path: Path to the Python function file
            existing_functions: Dictionary of existing function IDs

        Returns:
            True if successful, False otherwise
        """
        self.log(f'Processing {file_path.name}...')

        metadata = self.extract_function_metadata(file_path)
        if not metadata:
            return False

        function_id = metadata['id']

        # Check if function exists
        if function_id in existing_functions:
            self.log(f'Function {function_id} exists, updating...')
            return self.update_function(function_id, metadata)
        else:
            self.log(f'Function {function_id} does not exist, creating...')
            return self.create_function(metadata)

    def deploy_all(self, functions_dir: Path) -> Dict[str, int]:
        """
        Deploy all functions from the functions directory.

        Args:
            functions_dir: Path to the functions directory

        Returns:
            Dictionary with deployment statistics
        """
        stats = {'total': 0, 'success': 0, 'failed': 0}

        self.log('Starting deployment...')
        self.log(f'OpenWebUI URL: {self.base_url}')

        # Get existing functions
        existing_functions = self.get_existing_functions()
        self.log(f'Found {len(existing_functions)} existing functions')

        # Find all Python files in functions directory
        python_files = list(functions_dir.rglob('*.py'))
        python_files = [f for f in python_files if not f.name.startswith('__')]

        if not python_files:
            self.log('No Python files found in functions directory', 'WARNING')
            return stats

        self.log(f'Found {len(python_files)} function files to deploy')

        # Deploy each function
        for file_path in python_files:
            stats['total'] += 1
            if self.deploy_function(file_path, existing_functions):
                stats['success'] += 1
            else:
                stats['failed'] += 1

        self.log('=' * 50)
        self.log(f'Deployment complete: {stats["success"]}/{stats["total"]} successful, {stats["failed"]} failed')

        return stats


def main():
    """Main entry point for the deployment script."""
    # Get environment variables
    openwebui_url = os.getenv('OPENWEBUI_URL')
    api_key = os.getenv('OPENWEBUI_API_KEY')

    if not openwebui_url:
        print('ERROR: OPENWEBUI_URL environment variable is not set')
        sys.exit(1)

    if not api_key:
        print('ERROR: OPENWEBUI_API_KEY environment variable is not set')
        sys.exit(1)

    # Initialize deployer
    deployer = OpenWebUIDeployer(openwebui_url, api_key)

    try:
        # Get functions directory
        script_dir = Path(__file__).parent
        repo_root = script_dir.parent
        functions_dir = repo_root / 'functions'

        if not functions_dir.exists():
            deployer.log('Functions directory not found', 'ERROR')
            sys.exit(1)

        # Deploy all functions
        stats = deployer.deploy_all(functions_dir)

        # Save logs
        deployer.save_logs()

        # Exit with appropriate code
        if stats['failed'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        deployer.log(f'Unexpected error: {str(e)}', 'ERROR')
        deployer.save_logs()
        sys.exit(1)


if __name__ == '__main__':
    main()
