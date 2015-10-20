#!/usr/bin/python
# coding=utf-8

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from subprocess import check_output, call
import urllib2
import json
import sys
import subprocess

def get_exitcode_stdout_stderr(cmd):
	"""
	Execute the external command and get its exitcode, stdout and stderr.
	"""
 
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = proc.communicate()
	exitcode = proc.returncode
	return exitcode, out, err

if __name__ == '__main__':
	"""Run a bunch of boilerplate commands to sync your local clone to its
	   parent github repo.
	"""
	print("Starting sync...", "\n")

	CURRENT_REPO_CMD = ['git', 'config', '--get', 'remote.origin.url']
	ADD_REMOTE_CMD = ['git', 'remote', 'add', 'upstream']
	REMOVE_CURRENT_URL_CMD = ['git', 'remote', 'remove', 'upstream']
	CHECK_REMOTES_CMD = ['git', 'remote', '-v']
	FETCH_UPSTREAM_CMD = ['git', 'fetch', 'upstream']
	CHECKOUT_MASTER_CMD = ['git', 'checkout', 'master']
	MERGE_UPSTREAM_CMD = ['git', 'merge', 'upstream/master']
	CHECK_UPSTREAM_CMD = ['git', 'ls-remote', '--get-url', 'upstream']

	try:
		repo_url = check_output(CURRENT_REPO_CMD)
		print("Getting repo's url...")
		print("Syncing repo:", repo_url)

		url_segments = repo_url.split("github.com/")
		path = url_segments[1]
		user, repo = path.split("/")
		repo = repo.split(".git")

		print("Checking the fork's parent url...", "\n")
		url = "https://api.github.com/repos/{}/{}".format(user, repo[0])
		req = urllib2.urlopen(url)
		res = json.load(req)
		parent_git_url = res['parent']['git_url']
		parent_html_url = res['parent']['html_url']
		protocol_git = parent_git_url.split("/")
		protocol_html = parent_html_url.split("/")

		if (protocol_git[0] == 'git:' and protocol_html[0] == 'https:'):
			print("Which protocol do you want to use? \n   1:  ", parent_git_url, "\n   2:  ", parent_html_url,"\n   If you are" 
				" behind corporate or proxied network you may use https and have configured proxy in gitconfig")
			userNumber = int(input('Give me a value: '))
			if (userNumber == 1):
				print("Will add remote to parent repo:", parent_git_url, "\n")
				ADD_REMOTE_CMD.append(parent_git_url)
				call(REMOVE_CURRENT_URL_CMD)
			elif (userNumber == 2):
				print("Will add remote to parent repo:", parent_html_url, "\n")
				call(REMOVE_CURRENT_URL_CMD)
				ADD_REMOTE_CMD.append(parent_html_url)
			else:
				print("Only '1' or '2' ¬¬\n")
				exit (1)
		call(ADD_REMOTE_CMD)
		print("")

		print("Checking remotes...", "\n")
		call(CHECK_REMOTES_CMD)
		print("")

		print("Fetching upstream...", "\n")
		call(FETCH_UPSTREAM_CMD)
		print("")

		print("Merging upstream and master", "\n")
		check_output(CHECKOUT_MASTER_CMD)
		call(MERGE_UPSTREAM_CMD)
		print("Syncing done.")

	except Exception as e:
		e_type = sys.exc_info()[0].__name__
		if (e_type != 'NameError'):
			print("The following error happened:", e, "\n")
			if (e_type == 'CalledProcessError' and
				hasattr(e, 'cmd') and
				e.cmd == CURRENT_REPO_CMD):
				print("Are you sure you are on the git repo folder?", "\n")
			elif (e_type == 'IndexError' and
				e.message == 'list index out of range'):
				print("Sorry, couldn't get the user and repo names from the Git config.", "\n")
			elif (e_type == 'KeyError' and
				e.message == 'parent'):
				print("Are you sure the repo is a fork?")
			elif (e_type == 'CalledProcessError' and
				(e.cmd == MERGE_UPSTREAM_CMD or e.cmd == CHECKOUT_MASTER_CMD)):
				print("Didn't merge. Reason:", e.output)
		else:
			print("Only Numbers please")
		print("Game Over.")
