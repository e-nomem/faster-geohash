#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2025 Eashwar Ranganathan <eashwar@eashwar.com>
# SPDX-License-Identifier: MIT

from collections.abc import Generator
from collections.abc import Mapping
from dataclasses import dataclass
from os import getenv
from pathlib import Path
from typing import Any

import requests
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from typer import Typer

IS_CI = getenv('CI', '').casefold() == 'true'

GITHUB_DIR = Path(__file__).parent.parent
HASHES_FILE = GITHUB_DIR / 'actions-hashes.yaml'
WORKFLOWS_DIR = GITHUB_DIR / 'workflows'

YAML_RT = YAML()
YAML_RT.width = 4096  # Prevent ruamel from line-wrapping our files
YAML_RT.indent(mapping=2, offset=2, sequence=4)

app = Typer(pretty_exceptions_show_locals=not IS_CI)


@dataclass(frozen=True, kw_only=True)
class ActionVersion:
	sha: str
	version: str


def rt_load_yaml(path: Path) -> CommentedMap:
	with open(path) as f:
		return YAML_RT.load(f)


def rt_dump_yaml(path: Path, data: CommentedMap) -> None:
	with open(path, 'w') as f:
		YAML_RT.dump(data, f)


def load_hashes() -> Mapping[str, ActionVersion]:
	return {k: ActionVersion(**v) for k, v in rt_load_yaml(HASHES_FILE).items()}


def all_workflow_files() -> Generator[Path, None, None]:
	for file in WORKFLOWS_DIR.iterdir():
		if file.is_file() and file.suffix == '.yml':
			yield file


def update_workflow(hashes: Mapping[str, ActionVersion], workflow: CommentedMap) -> bool | set[str]:
	did_change = False
	unknown_actions = set()
	for job_def in workflow.get('jobs', {}).values():
		for step in job_def.get('steps', []):
			if 'uses' in step:
				action, _, sha = step['uses'].strip().partition('@')
				try:
					action_version = hashes[action]
					if sha != action_version.sha:
						did_change = True
						step['uses'] = f'{action}@{action_version.sha}'
						step.yaml_add_eol_comment(f'{action_version.version}', 'uses')
				except KeyError:
					unknown_actions.add(action)

	if unknown_actions:
		return unknown_actions

	return did_change


def _call_github(action: str, path: str) -> Mapping[str, Any]:
	response = requests.get(
		url=f'https://api.github.com/repos/{action}/{path}',
		headers={
			'Accept': 'application/vnd.github+json',
			'X-GitHub-Api-Version': '2022-11-28',
		},
		timeout=3.0,
	)
	if response.status_code != requests.codes['ok']:
		raise RuntimeError(f'Received unexpected response from Github: {action=}, {path=}, {response.status_code=}')

	return response.json()


def get_latest_release_tag(action: str) -> str:
	return _call_github(action, 'releases/latest')['tag_name']


def get_tag_sha(action: str, tag: str) -> str:
	git_obj = _call_github(action, f'git/ref/tags/{tag}')['object']
	if git_obj['type'] == 'tag':
		return _call_github(action, f'git/tags/{git_obj["sha"]}')['object']['sha']

	return git_obj['sha']


@app.command()
def update(action: str | None = None) -> None:
	updated_actions = {}
	hashes = rt_load_yaml(HASHES_FILE)
	for current_action, details in hashes.items():
		if action is not None and current_action != action:
			continue

		latest_tag = get_latest_release_tag(current_action)
		latest_sha = get_tag_sha(current_action, latest_tag)

		if details['sha'] != latest_sha or details['version'] != latest_tag:
			updated_actions[current_action] = (details['version'], latest_tag)
			details['sha'] = latest_sha
			details['version'] = latest_tag

	if updated_actions:
		rt_dump_yaml(HASHES_FILE, hashes)

		print('The following actions were updated:')
		for current_action, versions in updated_actions.items():
			print(f' - {current_action}: {versions[0]} -> {versions[1]}')


@app.command()
def check(fix: bool = False) -> None:
	hashes = load_hashes()
	files_needing_action = {}
	for workflow_file in all_workflow_files():
		workflow = rt_load_yaml(workflow_file)
		if result := update_workflow(hashes, workflow):
			files_needing_action[workflow_file] = result
			if fix:
				rt_dump_yaml(workflow_file, workflow)

	updated_files = [f for f, r in files_needing_action.items() if isinstance(r, bool)]
	invalid_files = {f: r for f, r in files_needing_action.items() if not isinstance(r, bool)}

	if updated_files:
		if fix:
			print('The following files were updated:')
		else:
			print('The following files require updates:')

		for file in updated_files:
			print(f' - {file.name}')

	if invalid_files:
		print('The following files use invalid actions:')
		for file, actions in invalid_files.items():
			print(f' - {file.name}: {", ".join(actions)}')

	if invalid_files or (updated_files and not fix):
		raise SystemExit(1)


if __name__ == '__main__':
	app()
