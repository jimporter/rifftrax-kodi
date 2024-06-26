PYTHON?=python3
XBMC_PROFILE?=$(HOME)/.xbmc

ADDON_NAME=plugin.video.rifftrax
ADDON_VERSION=0.0.1
ADDON_INSTALL_DIR=$(XBMC_PROFILE)/addons/$(ADDON_NAME)

.PHONY: uninstall-dev
uninstall-dev:
	rm -rf $(ADDON_INSTALL_DIR)

.PHONY: install-dev
install-dev: uninstall-dev
	cp -R $(ADDON_NAME) $(ADDON_INSTALL_DIR)

.PHONY: package
package:
	find . -name "*.pyc" -exec rm {} \;
	rm -f $(ADDON_NAME)-$(ADDON_VERSION).zip
	zip -r $(ADDON_NAME)-$(ADDON_VERSION).zip $(ADDON_NAME)

.PHONY: install-deps
install-deps:
	$(PYTHON) -m pip install -r dev-requirements.txt

.PHONY: test
test:
	PYTHONPATH=$(PWD)/$(ADDON_NAME):$(PYTHONPATH) \
	$(PYTHON) -m unittest discover test

.PHONY: lint
lint:
	flake8 .
