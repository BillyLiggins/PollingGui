.PHONY: container ssh rpm clean

container: Dockerfile rpms
	docker build -t alarmgui .
	docker run -p 2200:22 --rm -t -i alarmgui

ssh:
	@echo "The password is 'password'"
	ssh -Y -p 2200 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@127.0.0.1

rpms: Dockerfile.rpmbuilder
	docker build -t alarmgui_rpmbuilder -f Dockerfile.rpmbuilder .
	docker run --name rpmbuilder -ti alarmgui_rpmbuilder
	docker cp rpmbuilder:/alarmgui/distdir ./
	docker stop rpmbuilder
	docker rm rpmbuilder

spec: setup.py
	python setup.py bdist_rpm --spec-only
	python setup.py sdist

clean:
	rm -rf distdir
	rm -rf dist
	rm -rf alarmgui.egg-info
	docker stop rpmbuilder; true
	docker rm rpmbuilder; true
