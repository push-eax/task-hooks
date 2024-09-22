#!/usr/bin/env bash

if [ $# -eq 0 ]
then
	echo "Please supply the sfcli alias corresponding to your org."
else
	# init access token and user ID
	echo -n "Initializing access token... "
	SFCLIJSON=`sf org display user -o $1 --json | ansi2txt`
	export SFACCESSTOKEN=`echo -nE $SFCLIJSON | jq '.result.accessToken' | tr -d '"'`
	export SFUSERID=`echo -nE $SFCLIJSON | jq '.result.id' | tr -d '"'`
	export SFINSTANCE=`echo -nE $SFCLIJSON | jq '.result.instanceUrl' | tr -d '"' | sed 's/^.*[/]//'`
	export PYTHONPATH="${PYTHONPATH}:$PWD/hooks"
	echo "done"
fi
