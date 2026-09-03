#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2026 Eashwar Ranganathan <eashwar@eashwar.com>
# SPDX-License-Identifier: MIT

import json

PYTHON_DEFS = [
	{
		'python': 'cp310',  # tag::MIN_PYTHON
		'macos_deployment_target': '10.12',
	},
	{
		'python': 'cp314t',
		'macos_deployment_target': '10.15',
	},
	{
		'python': 'cp315t',
		'macos_deployment_target': '10.15',
	},
]

OS_DEFS = [
	{
		'platform': 'manylinux_x86_64',
		'os': 'ubuntu-24.04',
		'arch': 'x86_64',
	},
	{
		'platform': 'manylinux_aarch64',
		'os': 'ubuntu-24.04-arm',
		'arch': 'arm64',
	},
	{
		'platform': 'macosx_x86_64',
		'os': 'macos-15-intel',
		'arch': 'x86_64',
	},
	{
		'platform': 'macosx_arm64',
		'os': 'macos-15',
		'arch': 'arm64',
		'macos_deployment_target': '11.0',
	},
]

if __name__ == '__main__':
	print(json.dumps([{**py_def, **os_def} for py_def in PYTHON_DEFS for os_def in OS_DEFS]))
