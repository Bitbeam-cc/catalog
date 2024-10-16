

TEST_REPORT_XML ?= pytest.xml
TEST_REPORT_LOG ?= pytest.log
TEST_ARGS       ?=

TEST_API_URL    ?= http://localhost:8000

PKG_TARGET_DIR ?= pkgs

COMPONENT = bitbeam-catalog
TEST_REMOTE_COMPONENT = $(COMPONENT)-test
SOURCES = \
	$(shell find ./bitbeam_catalog) \
	$(shell find ./tests) \
	etc/* \
	openapi.yaml \
	redoc.html \
	setup.py

DOCKER_IMAGE_BUILDER = python:3.9-bullseye
DOCKER_IMAGE = $(COMPONENT)
DOCKER_IMAGE_TEST = $(COMPONENT)-test

VERSION := $(shell python3 -B setup.py --version)

DOCKER_RUN_PARAMS = \
		-t \
		--rm \
		-u $$(id -u):$$(getent group docker | awk -F : '{print $$3}') \
		-e HOME=/tmp \
		-e VERSION=$(VERSION) \
		-h "$(shell hostname -f)" \
		-w "$(CURDIR)" \
		-v "$(CURDIR):$(CURDIR)" \
		-v "/etc/group:/etc/group:ro" \
		-v "/etc/passwd:/etc/passwd:ro" \
		-v "$(HOME)/.ssh:$(HOME)/.ssh:ro"

stamp/requirements.stamp: requirements.txt
	mkdir -p $(PKG_TARGET_DIR)
	docker run $(DOCKER_RUN_PARAMS) $(DOCKER_IMAGE_BUILDER) \
		pip3 wheel --find-links=file://$(CURDIR)/$(PKG_TARGET_DIR) git+https://github.com/PoorHttp/PoorWSGI.git -w $(PKG_TARGET_DIR)
	docker run $(DOCKER_RUN_PARAMS) $(DOCKER_IMAGE_BUILDER) \
		pip3 wheel --find-links=file://$(CURDIR)/$(PKG_TARGET_DIR) -r requirements.txt -w $(PKG_TARGET_DIR)
	docker run $(DOCKER_RUN_PARAMS) $(DOCKER_IMAGE_BUILDER) \
		pip3 wheel --find-links=file://$(CURDIR)/$(PKG_TARGET_DIR) pytest requests -w $(PKG_TARGET_DIR)
	mkdir -p stamp
	touch $@

# pytest -v --pylint --pep8 --doctest-plus --doctest-rst bitbeam-catalog
stamp/package.stamp: $(SOURCES) stamp/requirements.stamp
	docker run $(DOCKER_RUN_PARAMS) $(DOCKER_IMAGE_BUILDER) \
		bash -c "pip3 install --find-links=file://$(CURDIR)/$(PKG_TARGET_DIR) -r requirements.txt && \
			 python3 setup.py test -a --junit-xml='$(CURDIR)/$(TEST_REPORT_XML)' bdist_wheel -d $(PKG_TARGET_DIR) clean -a"
	touch $@

stamp/docker.stamp: stamp/package.stamp Dockerfile
	docker build \
		--build-arg "PKG_DIR=$(PKG_TARGET_DIR)" \
		-f Dockerfile \
		-t $(DOCKER_IMAGE) .

stamp/docker: docker.stamp

docker-run: stamp/docker.stamp
	docker run \
		--rm \
		-p 8000:8000 \
		"$(DOCKER_IMAGE)"

docker-develop: stamp/requirements.stamp
	docker build \
		--build-arg "PKG_DIR=$(PKG_TARGET_DIR)" \
		$(DOCKER_OPTS) \
		-f Dockerfile.develop \
		-t $(COMPONENT)-develop .
	docker run \
		-ti \
		$(DOCKER_RUN_PARAMS) \
		-v "$(CURDIR):/usr/local/share/$(COMPONENT)" \
		--network=host \
		-p 8000:8000 \
		"$(COMPONENT)-develop" \
		bash

stamp/test-remote-docker.stamp: \
	stamp/requirements.stamp \
	Dockerfile.test \
	$(shell find ./tests_integrity) \
	openapi.yaml

	docker build \
		--build-arg "PKG_DIR=$(PKG_TARGET_DIR)" \
		$(DOCKER_OPTS) \
		-f Dockerfile.test \
		-t '$(DOCKER_IMAGE_TEST)' .
	touch $@

test: stamp/docker.stamp stamp/test-remote-docker.stamp
	export DOCKER_IMAGE=$(DOCKER_IMAGE) ; \
	export DOCKER_IMAGE_TEST=$(DOCKER_IMAGE_TEST) ; \
	export TEST_REPORT_XML=$(TEST_REPORT_XML) ; \
	docker-compose run test ; \
	docker-compose logs app ; \
	docker-compose down ;

test-remote: stamp/test-remote-docker.stamp
	docker run \
		--rm \
		--network=host \
		-e "TEST_API_URL=$(TEST_API_URL)" \
		'$(DOCKER_IMAGE_TEST)'

clean:
	docker rmi -f "$(DOCKER_IMAGE_BUILDER)" "$(DOCKER_IMAGE)" "$(DOCKER_IMAGE_TEST)" || true
	rm -rf dist .eggs *.egg-info
	rm -rf $(PKG_TARGET_DIR) stamp
	rm -rf .pytest_cache $(TEST_REPORT_XML) $(TEST_REPORT_LOG)
