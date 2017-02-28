.PHONY: spec clean

spec: setup.py
	python setup.py bdist_rpm --spec-only
	python setup.py sdist

clean:
	rm -rf distdir
	rm -rf dist
	rm -rf pollinggui.egg-info
	docker stop rpmbuilder; true
	docker rm rpmbuilder; true
