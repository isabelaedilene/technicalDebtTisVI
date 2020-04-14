#!/usr/bin/env bash
[[ ! $(echo $1 | java -jar satd_detector.jar test 2>/dev/null) =~ .*Not.* ]] && exit 2 || exit 1